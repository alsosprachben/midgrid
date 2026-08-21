#!/usr/bin/env python3
"""perform_baroque.py -- a Baroque TIME transform for fixed-volume instruments.

On the organ/harpsichord you cannot shade a note's volume, so expression is made
in time (Harnoncourt's Klangrede). This applies that as a MIDI-timing transform,
leaving velocity flat:

  * base tempo   -- an appropriate, unhurried tempo
  * articulation -- an ORDINARY (non-legato) touch: each note releases early,
                    leaving a small silence. The gap scales with the note's own
                    value but is capped, so running passagework stays nearly
                    connected while weightier notes get real air (= lighter/softer).
  * cadential rit -- broadening into the final bars: rubato AS diminuendo, the
                    relaxation of energy at the close.

All event times (notes AND registration CCs AND ornament figures) warp through one
monotonic time-map, so nothing desyncs. Velocity is untouched (fixed volume).
Agogic metric stress is a planned refinement (see the skill).

Usage: perform_baroque.py IN.mid OUT.mid [--bpm 63] [--gap-frac 0.22]
       [--gap-cap 0.13] [--gap-min 0.03] [--rit-beats 8] [--rit-amount 1.8]
"""
import sys, argparse, mido

def meter_profile(num, den):
    """(bar_len_quarters, [(phase_q, weight), ...]) for the metric hierarchy.
    Strong beats carry more weight -> the agogic lengthens them (the meter breathes)."""
    if den == 8 and num % 3 == 0:                    # compound (6/8, 9/8, 12/8): dotted-qtr beats
        nb = num // 3; bar = nb * 1.5
        prof = []
        for k in range(nb):
            base = k * 1.5
            head = 1.0 if k == 0 else (0.62 if k == nb // 2 else 0.5)   # 1st beat strongest
            prof += [(base, head), (base + 0.5, 0.2), (base + 1.0, 0.38)]  # strong/weak/lead-in
        return bar, prof
    beat = 4.0 / den                                  # simple: quarter(4) or half(2) tactus
    nb = num; bar = nb * beat
    w = {1: [1.0], 2: [1.0, 0.5], 3: [1.0, 0.3, 0.5], 4: [1.0, 0.3, 0.6, 0.3]}.get(nb,
        [1.0] + [0.4] * (nb - 1))
    return bar, [(i * beat, w[i]) for i in range(nb)]

def meter_weight(bar_len, prof):
    """phase-in-bar (quarters) -> metric weight, interpolated and wrapping."""
    import bisect
    ph = [p for p, _ in prof] + [bar_len]
    wv = [w for _, w in prof] + [prof[0][1]]
    def weight(phase):
        phase %= bar_len
        i = bisect.bisect_right(ph, phase) - 1
        i = max(0, min(i, len(ph) - 2))
        f = (phase - ph[i]) / (ph[i + 1] - ph[i]) if ph[i + 1] > ph[i] else 0.0
        return wv[i] + f * (wv[i + 1] - wv[i])
    return weight

def build_timemap(total_beats, bpm, rit_beats, rit_amount, agogic, bar_len, prof,
                  ineg=0.5, ineg_div=2, res=0.02):
    """beat -> performed seconds (cumulative, monotonic). Base tempo x a per-bar
    agogic breath (strong beats slower/longer, mean-preserving so no drift) x a
    smoothstep cadential broadening over the last rit_beats."""
    spb0 = 60.0 / bpm
    rit_start = total_beats - rit_beats
    weight = meter_weight(bar_len, prof)
    mean_w = sum(weight(p) for p in [k * res for k in range(int(bar_len / res))]) / (int(bar_len / res) or 1)
    def rit(b):
        if rit_beats <= 0 or b <= rit_start: return 1.0
        x = min((b - rit_start) / rit_beats, 1.0)
        return 1.0 + (rit_amount - 1.0) * (x * x * (3 - 2 * x))
    def inegal(b):
        # notes inegales (French, plucked/keyboard): the subdivisions of a beat are
        # played long-short. As a TIME-MAP warp (rather than per-note surgery) the
        # beat boundaries are fixed points, so longer values are untouched and every
        # voice stays consistent automatically. ineg = the first note's share of the
        # pair (0.5 equal, 0.60 lourer/gentle, 0.667 = a sharp 2:1 pointer).
        if ineg == 0.5: return 1.0
        phase = (b * ineg_div) % 2.0            # position within the long-short pair
        return 2.0 * ineg if phase < 1.0 else 2.0 * (1.0 - ineg)   # mean-preserving
    def factor(b):
        return rit(b) * (1.0 + agogic * (weight(b) - mean_w)) * inegal(b)
    bs, times, t = [], [], 0.0
    b = 0.0; prev_spb = spb0 * factor(0.0)
    while b <= total_beats + res:
        cur = spb0 * factor(b)
        if bs:
            t += (prev_spb + cur) / 2 * res
        bs.append(b); times.append(t); prev_spb = cur; b += res
    def tm(beat):
        # linear interpolation into (bs, times)
        if beat <= 0: return 0.0
        if beat >= bs[-1]: return times[-1] + (beat - bs[-1]) * prev_spb
        lo, hi = 0, len(bs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if bs[mid] <= beat: lo = mid
            else: hi = mid
        f = (beat - bs[lo]) / (bs[hi] - bs[lo])
        return times[lo] + f * (times[hi] - times[lo])
    return tm

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("outp")
    ap.add_argument("--bpm", type=float, default=63.0)
    ap.add_argument("--gap-frac", type=float, default=0.22)   # gap as fraction of note's performed value
    ap.add_argument("--gap-cap", type=float, default=0.13)    # max silence (s) -- long notes keep most value
    ap.add_argument("--gap-min", type=float, default=0.03)    # min silence (s) -- always some air
    ap.add_argument("--rit-beats", type=float, default=8.0)
    ap.add_argument("--rit-amount", type=float, default=1.8)
    ap.add_argument("--agogic", type=float, default=0.09)   # metric breath depth (0 = off)
    # --- plucked-instrument levers (harpsichord/lute): the pluck is fixed, so
    # accent is made by SPREAD and shape by inequality.
    ap.add_argument("--spread", type=float, default=0.0)    # ms between notes of a rolled chord
    ap.add_argument("--spread-dir", choices=('up','down'), default='up')
    ap.add_argument("--spread-accent", action='store_true') # roll wider on strong beats
    ap.add_argument("--inegales", type=float, default=0.5)  # first note's share of the pair
    ap.add_argument("--inegales-div", type=int, default=2)  # subdivisions per beat made unequal
    a = ap.parse_args()

    m = mido.MidiFile(a.inp); TPB = m.ticks_per_beat
    # --- arpegement (plucked): roll the notes of a chord instead of striking them
    # together. On a harpsichord the pluck is fixed, so SPREAD is the accent --
    # a wider roll reads as a stronger chord (Couperin's arpegement). Collected
    # GLOBALLY (across tracks/voices) so a chord split between staves rolls as one
    # gesture; only the onsets move, the note-offs stay (the hand lifts together).
    spread_of = {}
    if a.spread > 0.0:
        groups = {}
        for tr in m.tracks:
            t = 0
            for x in tr:
                t += x.time
                if x.type == 'note_on' and x.velocity > 0:
                    groups.setdefault((x.channel, t), set()).add(x.note)
        for (chan, tick), notes in groups.items():
            if len(notes) < 2: continue
            order = sorted(notes, reverse=(a.spread_dir == 'down'))
            for i, n in enumerate(order):
                spread_of[(chan, tick, n)] = i          # index in the roll
    # meter (for the agogic bar grid); tick 0 = downbeat (no anacrusis in 543)
    num, den = 4, 4
    for tr in m.tracks:
        for x in tr:
            if x.type == 'time_signature': num, den = x.numerator, x.denominator; break
    bar_len, prof = meter_profile(num, den)
    # total length in beats
    total = 0.0
    for tr in m.tracks:
        t = 0
        for x in tr:
            t += x.time
        total = max(total, t / TPB)
    tm = build_timemap(total, a.bpm, a.rit_beats, a.rit_amount, a.agogic, bar_len, prof,
                       a.inegales, a.inegales_div)
    weight_at = meter_weight(bar_len, prof)
    OUT_TEMPO = 500000                       # fixed output tempo; warped ticks carry the timing
    sec2tick = lambda s: int(round(s / (OUT_TEMPO / 1e6) * TPB))

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    for ti, tr in enumerate(m.tracks):
        # gather absolute-tick events; pair note_on/off for articulation
        t = 0; events = []; on = {}
        for x in tr:
            t += x.time
            b = t / TPB
            if x.type == 'note_on' and x.velocity > 0:
                on.setdefault((x.channel, x.note), []).append((b, x.velocity))
            elif x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0):
                q = on.get((x.channel, x.note))
                if q:
                    on_b, vel = q.pop(0)
                    p_on = tm(on_b); p_off_full = tm(b)
                    idx = spread_of.get((x.channel, int(round(on_b * TPB)), x.note))
                    if idx:                       # 0 = first of the roll, no delay
                        w = weight_at(on_b) if a.spread_accent else 1.0
                        p_on += idx * a.spread * w / 1000.0
                        if p_on > p_off_full - 0.02: p_on = max(p_off_full - 0.02, tm(on_b))
                    dur = p_off_full - p_on
                    gap = min(a.gap_frac * dur, a.gap_cap)
                    gap = max(gap, min(a.gap_min, dur * 0.5))
                    p_off = max(p_on + dur - gap, p_on + 0.005)
                    events.append((sec2tick(p_on), 1, mido.Message('note_on', channel=x.channel, note=x.note, velocity=vel)))
                    events.append((sec2tick(p_off), 0, mido.Message('note_off', channel=x.channel, note=x.note, velocity=0)))
            elif x.type == 'set_tempo':
                continue                                     # replaced by OUT_TEMPO below
            elif x.is_meta and x.type == 'end_of_track':
                continue
            else:
                events.append((sec2tick(tm(b)), 2, x.copy(time=0)))  # CC, prog, other meta -- warp onset
        if ti == 0:
            events.append((0, -1, mido.MetaMessage('set_tempo', tempo=OUT_TEMPO)))
        events.sort(key=lambda e: (e[0], e[1]))
        nt = mido.MidiTrack(); last = 0
        for tick, _, msg in events:
            msg.time = max(0, tick - last); last = tick
            nt.append(msg)
        nt.append(mido.MetaMessage('end_of_track', time=0))
        out.tracks.append(nt)
    out.save(a.outp)
    extra = ""
    if a.spread > 0: extra += " | spread %.0fms %s%s" % (a.spread, a.spread_dir, "+accent" if a.spread_accent else "")
    if a.inegales != 0.5: extra += " | inegales %.3f /%d" % (a.inegales, a.inegales_div)
    print("wrote %s | %.0f beats @ %.0f bpm | %d/%d agogic %.2f | rit last %.0f x%.2f%s | len %.1fs"
          % (a.outp, total, a.bpm, num, den, a.agogic, a.rit_beats, a.rit_amount, extra, out.length))

if __name__ == "__main__":
    main()
