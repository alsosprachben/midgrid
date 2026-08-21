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

def analyze_score(mid, TPB, bar_len=4.0):
    """Read the music itself, so the shaping can respond to it rather than treating
    every bar alike. Returns (phrase_ends, density_at, tension_at):

      phrase_ends -- beats where the music BREATHES. Detected PER VOICE (a rest, or
                     a note well longer than that voice's norm) and then pooled:
                     a boundary counts when several voices breathe together. This
                     matters because in real counterpoint the aggregate onset
                     stream never stops -- when one voice rests the others cover
                     it, which is what fugal writing is FOR -- so looking for gaps
                     in the whole texture finds nothing. Voices phrase; textures
                     rarely do.
      density_at  -- local onset density (onsets per beat). Fast passagework must
                     NOT be stretched beat-by-beat; it wants to flow.
      tension_at  -- vertical dissonance (a sounding m2/M2/tritone/7th). A
                     dissonance or suspension is a "good note" wherever it falls,
                     and a player leans on it -- with time, not volume.
    """
    import bisect
    notes = []; per_voice = []
    for tr in mid.tracks:
        t = 0; on = {}; vn = []
        for x in tr:
            t += x.time
            if x.type == 'note_on' and x.velocity > 0:
                on.setdefault(x.note, []).append(t)
            elif x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0):
                q = on.get(x.note)
                if q:
                    n = (q.pop(0) / TPB, t / TPB, x.note); notes.append(n); vn.append(n)
        if vn: per_voice.append(sorted(vn))
    if not notes: return [], (lambda b: 0.0), (lambda b: 0.0)
    notes.sort()
    onsets = sorted(set(round(n[0], 4) for n in notes))

    # -- phrase ends, per voice then pooled
    cand = []
    for vn in per_voice:
        durs = sorted(e - s for s, e, _ in vn)
        med_d = durs[len(durs) // 2] or 0.25
        for k, (s, e, _) in enumerate(vn):
            nxt = vn[k + 1][0] if k + 1 < len(vn) else None
            rest = (nxt - e) if nxt is not None else 0.0
            # Score every note-end by how much it BREATHES, continuously rather than
            # by a threshold: a rest, or a note long for this voice. Thresholds are
            # fragile across textures (a fugue whose voices rest often would fire
            # constantly; strict 4-part counterpoint that never rests would fire
            # never), so we rank instead and take the best at a musical RATE.
            score = max(rest / med_d, (e - s) / med_d - 1.0)
            if score > 0.25: cand.append((round(e, 2), score))
    phrase_ends = []
    if cand:
        cand.sort()
        clusters = []                                  # pool near-simultaneous breaths
        i = 0
        while i < len(cand):
            j = i
            while j < len(cand) and cand[j][0] - cand[i][0] <= 0.6: j += 1
            times = [c[0] for c in cand[i:j]]
            clusters.append((sum(times) / len(times), sum(c[1] for c in cand[i:j])))
            i = j
        # Phrases run in BARS: aim for roughly one boundary every 4 bars, and keep
        # the strongest candidates subject to a minimum spacing. Adapts to any piece.
        span = notes[-1][1] - notes[0][0]
        target = max(1, int(span / (4.0 * max(bar_len, 1.0))))
        min_gap = max(2.0 * bar_len, span / (2.5 * target))
        clusters.sort(key=lambda c: -c[1])
        kept = []
        for t, sc in clusters:
            if len(kept) >= target: break
            if all(abs(t - u) >= min_gap for u in kept): kept.append(t)
        phrase_ends = sorted(kept)

    # -- local onset density (onsets per beat, +-1 beat window)
    def density_at(b):
        lo = bisect.bisect_left(onsets, b - 1.0); hi = bisect.bisect_right(onsets, b + 1.0)
        return (hi - lo) / 2.0

    # -- vertical dissonance at each onset (interval classes 1, 2, 6 = m2/M2/tritone)
    starts = [n[0] for n in notes]
    tension_pts = []
    for t in onsets:
        i = bisect.bisect_right(starts, t + 1e-6)
        sounding = [p for (s, e, p) in notes[max(0, i - 24):i] if s <= t + 1e-6 < e]
        d = 0.0
        for a in range(len(sounding)):
            for c in range(a + 1, len(sounding)):
                ic = abs(sounding[a] - sounding[c]) % 12
                ic = min(ic, 12 - ic)
                if ic in (1, 2, 6): d = 1.0
        if d: tension_pts.append(t)
    def tension_at(b):
        i = bisect.bisect_left(tension_pts, b - 0.25)
        return 1.0 if (i < len(tension_pts) and tension_pts[i] <= b + 0.25) else 0.0
    return phrase_ends, density_at, tension_at


def add_cadential_trills(mid, TPB, phrase_ends, verbose=True):
    """EDITORIAL ornamentation: put a trill on the penultimate note at cadences.

    A Baroque player ornamented far beyond what the page shows, and the cadential
    trill is the least optional of all -- at a cadence it is expected, not decorative.
    The phrase-ends found by analyze_score are exactly the cadence candidates, so
    they feed straight into midgrid's C.P.E. Bach engine (every wavy sign is a trill
    FROM ABOVE, appui-supported on long notes, on the beat).

    Conservative by construction: only the TOP voice, only a note long enough to
    hold a trill, and only where it resolves by STEP into the cadence note -- the
    classic 4-3 / 2-1 formula. The score's own ornaments are untouched.
    """
    import os, bisect
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    if root not in sys.path: sys.path.insert(0, root)
    try:
        from kern2midi_ornaments import realize
        from fractions import Fraction
    except Exception as e:
        if verbose: print("  (cadential trills skipped: %s)" % e)
        return 0

    # per-track absolute-time notes, and the piece's scale from its pitch-class use
    tracks = []
    hist = [0] * 12
    for tr in mid.tracks:
        t = 0; on = {}; vn = []
        for x in tr:
            t += x.time
            if x.type == 'note_on' and x.velocity > 0:
                on.setdefault(x.note, []).append((t, x.velocity)); hist[x.note % 12] += 1
            elif x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0):
                q = on.get(x.note)
                if q:
                    s, v = q.pop(0); vn.append([s, t, x.note, v, x.channel])
        vn.sort(); tracks.append(vn)
    scale = {pc for pc, _ in sorted(enumerate(hist), key=lambda kv: -kv[1])[:7]}

    added = 0
    for pe in phrase_ends:
        tick = pe * TPB
        # the cadence note: highest-pitched note ending at this boundary
        best = None
        for ti, vn in enumerate(tracks):
            for k, n in enumerate(vn):
                if abs(n[1] - tick) <= 0.6 * TPB and (best is None or n[2] > best[1][2]):
                    best = (ti, n, k)
        if best is None: continue
        ti, cad, k = best
        vn = tracks[ti]
        # The penultimate note of the MELODIC line. A registered MIDI merges several
        # voices into one track per division, so "the previous note in the track" is
        # not "the previous note in the voice" -- pick the note that continues this
        # LINE, i.e. the one ending just before the cadence note and closest to it in
        # pitch. (Without this we happily picked a note 20 semitones away.)
        prev = None; bestd = 99
        for j in range(k - 1, -1, -1):
            n = vn[j]
            if n[1] < cad[0] - 1.5 * TPB: break
            if n[1] <= cad[0] + TPB // 8:
                d = abs(n[2] - cad[2])
                if d < bestd: bestd = d; prev = j
        if prev is None: continue
        p = vn[prev]
        dur_beats = (p[1] - p[0]) / float(TPB)
        step = abs(p[2] - cad[2])
        # Long enough to hold a trill, and a stepwise close (the 4-3 / 2-1 formula).
        # 0.22 beat still supports a proper short Pralltriller; below that the
        # writing simply does not offer a trill and a player would not force one.
        if dur_beats < 0.22 or not (1 <= step <= 2):
            continue
        fig = realize(p[2], Fraction(dur_beats).limit_denominator(32), 't', scale)
        if len(fig) < 3: continue
        p.append(fig)                                   # mark for splicing
        added += 1

    if not added: return 0
    # splice: rebuild each track, replacing marked notes with their figures and
    # leaving every other event (CC, program change, meta) exactly where it was.
    for ti, tr in enumerate(mid.tracks):
        marked = {(n[0], n[2]): n for n in tracks[ti] if len(n) > 5}
        if not marked: continue
        ev = []; t = 0; drop = set()
        for x in tr:
            t += x.time
            key = None
            if x.type == 'note_on' and x.velocity > 0: key = (t, x.note)
            if key in marked and key not in drop:
                drop.add(key); n = marked[key]; tt = n[0]
                for pitch, d in n[5]:
                    dt = max(1, int(round(float(d) * TPB)))
                    ev.append((tt, 1, mido.Message('note_on', channel=n[4], note=pitch, velocity=n[3])))
                    ev.append((tt + dt, 0, mido.Message('note_off', channel=n[4], note=pitch, velocity=0)))
                    tt += dt
                continue
            if x.type in ('note_off',) or (x.type == 'note_on' and x.velocity == 0):
                if (None, None) != (None, None) : pass
            ev.append((t, 2 if x.is_meta else 1, x.copy(time=0)))
        # drop the original note_offs of the replaced notes
        out = []; pending = {(n[0], n[2]): n[1] for n in marked.values()}
        for tick_, order, msg in ev:
            if (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)):
                hit = [k for k, offt in pending.items() if k[1] == msg.note and offt == tick_]
                if hit: del pending[hit[0]]; continue
            out.append((tick_, order, msg))
        out.sort(key=lambda e: (e[0], e[1]))
        nt = mido.MidiTrack(); last = 0
        for tick_, _, msg in out:
            msg.time = max(0, tick_ - last); last = tick_; nt.append(msg)
        mid.tracks[ti] = nt
    if verbose: print("  added %d cadential trills" % added)
    return added


def build_timemap(total_beats, bpm, rit_beats, rit_amount, agogic, bar_len, prof,
                  ineg=0.5, ineg_div=2, res=0.02,
                  phrase_ends=(), density_at=None, tension_at=None,
                  phrase=0.0, density_damp=0.0, tension=0.0):
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
    # --- phrase-aware shaping -------------------------------------------------
    # A player does not breathe identically in every bar: they broaden INTO a
    # phrase end and re-gather after it, they let fast passagework flow instead of
    # stressing every beat inside it, and they lean on a dissonance. Each of these
    # scales or adds to the base agogic rather than replacing it.
    import bisect as _b
    pend = sorted(phrase_ends)
    med_dens = 0.0
    if density_at is not None and total_beats > 0:
        samp = sorted(density_at(k) for k in range(1, int(total_beats)))
        med_dens = samp[len(samp) // 2] if samp else 0.0

    def depth_scale(b):
        """How strongly the METRIC breath applies here: damped where the texture
        is running fast (let it flow), full where it is broad."""
        if density_damp <= 0.0 or density_at is None or med_dens <= 0: return 1.0
        rel = density_at(b) / med_dens
        return 1.0 / (1.0 + density_damp * max(0.0, rel - 1.0))

    def phrase_bump(b):
        """Broaden approaching a phrase end and re-gather just after it -- the
        breath between sentences. Peaks just BEFORE the boundary."""
        if phrase <= 0.0 or not pend: return 0.0
        i = _b.bisect_left(pend, b)
        best = 0.0
        for j in (i - 1, i):
            if 0 <= j < len(pend):
                d = b - pend[j]                     # <0 before the boundary
                if -1.25 <= d <= 0.35:
                    x = (d + 1.25) / 1.6            # 0..1 across the window
                    best = max(best, (x ** 2) * (1.0 - x) * 6.0)   # rises, peaks at the end
        return phrase * best

    def tension_bump(b):
        """Lean on a sounding dissonance/suspension -- agogic weight, not volume."""
        if tension <= 0.0 or tension_at is None: return 0.0
        return tension * tension_at(b)

    def factor(b):
        return (rit(b) * (1.0 + agogic * depth_scale(b) * (weight(b) - mean_w))
                * inegal(b) * (1.0 + phrase_bump(b) + tension_bump(b)))
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
    ap.add_argument("--overhold", type=float, default=0.0)  # beats: hold notes past their value
    # --- phrase-aware shaping (respond to the music, not just the barline) ---
    ap.add_argument("--phrase", type=float, default=0.0)        # broaden into phrase ends
    ap.add_argument("--density-damp", type=float, default=0.0)  # let fast passagework flow
    ap.add_argument("--tension", type=float, default=0.0)       # lean on dissonances
    ap.add_argument("--cadential-trills", action="store_true")  # editorial ornaments at cadences
    ap.add_argument("--figuration-hold", type=float, default=0.0)  # hold a figure's inner voice
    a = ap.parse_args()

    m = mido.MidiFile(a.inp); TPB = m.ticks_per_beat
    # --- arpegement (plucked): roll the notes of a chord instead of striking them
    # together. On a harpsichord the pluck is fixed, so SPREAD is the accent --
    # a wider roll reads as a stronger chord (Couperin's arpegement). Collected
    # GLOBALLY (across tracks/voices) so a chord split between staves rolls as one
    # gesture; only the onsets move, the note-offs stay (the hand lifts together).
    # --- overholding (style brisé / style luthé): the fingers hold keys past the
    # written value so a broken chord accumulates into a sounding harmony. This is
    # NOT a sustain pedal -- a harpsichord has none (its dampers ride on the jacks,
    # one per key), so the effect is purely note-duration. The only real constraint
    # is that a held note must end before its own pitch is struck again.
    # meter first: the figuration alternation and the agogic grid both need it
    num, den = 4, 4
    for tr in m.tracks:
        for x in tr:
            if x.type == 'time_signature': num, den = x.numerator, x.denominator; break
    bar_len, prof = meter_profile(num, den)
    # (bar_len/prof are needed below for the alternation parity)
    # --- figuration inner voice ------------------------------------------------
    # Broken-chord figuration carries an implied inner voice: the lowest note of each
    # beat-group, which the ear hears as HELD under the running notes. BWV 543's
    # prelude spells this out as held quarters (<< ...tuplet... \\ { e4 f e d } >>)
    # in ALTERNATE bars, and writes the same note as a struck 16th in the bars
    # between -- a deliberate alternation, not an inconsistency. E. Power Biggs
    # carried that alternation on through the triplet runs, and that is what this
    # does: find the bars the source already holds, take their PARITY, and continue
    # the pattern into later bars of the same parity. It never flattens the
    # alternation into a uniform sustain -- that would erase what is composed.
    fig_hold = {}
    if a.figuration_hold > 0.0:
        W = a.figuration_hold
        by_chan = {}
        held_bars = set()
        for tr in m.tracks:
            t = 0; on = {}
            for x in tr:
                t += x.time
                if x.type == 'note_on' and x.velocity > 0:
                    on.setdefault(x.note, []).append(t)
                elif x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0):
                    q = on.get(x.note)
                    if q:
                        s = q.pop(0)
                        by_chan.setdefault(x.channel, []).append((s / TPB, (t - s) / TPB, x.note))
        # which bars does the source ALREADY hold? (an on-beat note of ~the group
        # length, sitting under a group of faster notes)
        for chan, ns in by_chan.items():
            ns.sort()
            for i, (s, d, p) in enumerate(ns):
                if d < W * 0.9: continue
                if abs((s / W) - round(s / W)) > 0.02: continue
                grp = [n for n in ns[i:i + 14] if s <= n[0] < s + W and n[1] < W * 0.6]
                if len(grp) >= 2: held_bars.add(int(s // bar_len))
        # The pattern belongs to a SECTION, not the whole piece: it may only be
        # continued while the same figuration texture lasts. Characterise each bar by
        # its dominant short-note value (a triplet run and a 16th run are different
        # music), take the value of the bars the source already holds, and extend only
        # through the contiguous run of bars that share it.
        from collections import Counter as _C
        allnotes = sorted(n for ns in by_chan.values() for n in ns)
        nbars = int(max(n[0] for n in allnotes) // bar_len) + 2
        sub_of = {}
        for bi in range(nbars):
            sh = [round(d, 3) for s, d, p in allnotes if bi * bar_len <= s < (bi + 1) * bar_len and d < 0.4]
            if sh: sub_of[bi] = _C(sh).most_common(1)[0][0]
        # Segment the piece into contiguous runs of one subdivision -- a triplet run
        # and a 16th run are different sections, and a pattern may only be continued
        # inside the section that established it.
        section_of = {}; sid = 0
        for bi in range(nbars):
            if bi and abs(sub_of.get(bi, -9) - sub_of.get(bi - 1, -99)) > 0.02: sid += 1
            section_of[bi] = sid
        parity = None
        if held_bars:
            odd = sum(1 for b in held_bars if b % 2)
            parity = 1 if odd * 2 >= len(held_bars) else 0
            # Only continue where an ALTERNATION was actually established: the section
            # must hold on >= 3 bars of one parity, every other bar. Sections whose
            # held bars are irregular are just ordinary inner voices, not a pattern,
            # and inventing more of them would be composing rather than performing.
            per_section = {}
            for hb in held_bars: per_section.setdefault(section_of.get(hb), []).append(hb)
            start_of_section = {}
            for sec, bars in per_section.items():
                bars = sorted(bars)
                run = [b for b in bars if b % 2 == parity]
                if len(run) >= 3 and all(y - x == 2 for x, y in zip(run, run[1:])):
                    start_of_section[sec] = run[0]
        for chan, ns in by_chan.items():
            ns.sort()
            for i, (s, d, p) in enumerate(ns):
                if d >= W * 0.9: continue                  # already held
                if abs((s / W) - round(s / W)) > 0.02: continue   # must start the group
                bar = int(s // bar_len)
                if parity is not None:
                    st = start_of_section.get(section_of.get(bar))
                    if bar % 2 != parity or st is None or bar < st:
                        continue      # keep the alternation, and stay inside the section
                        # that established it (never leak into the next texture)
                grp = [n for n in ns[i:i + 12] if s <= n[0] < s + W]
                if len(grp) < 3: continue
                if p != min(n[2] for n in grp): continue   # the group's inner/bass voice
                fig_hold[(chan, round(s, 4), p)] = W

    next_same = {}
    if a.overhold > 0.0:
        onsets = {}
        for tr in m.tracks:
            t = 0
            for x in tr:
                t += x.time
                if x.type == 'note_on' and x.velocity > 0:
                    onsets.setdefault((x.channel, x.note), []).append(t)
        for k, v in onsets.items(): next_same[k] = sorted(v)

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
    # total length in beats
    total = 0.0
    for tr in m.tracks:
        t = 0
        for x in tr:
            t += x.time
        total = max(total, t / TPB)
    pend, dens_at, tens_at = analyze_score(m, TPB, bar_len)
    if a.cadential_trills and pend:
        # ornament FIRST, then warp -- so the trills stretch with the tempo and
        # broaden with the cadential rit, exactly as a player's would.
        if add_cadential_trills(m, TPB, pend):
            pend, dens_at, tens_at = analyze_score(m, TPB, bar_len)
    tm = build_timemap(total, a.bpm, a.rit_beats, a.rit_amount, a.agogic, bar_len, prof,
                       a.inegales, a.inegales_div, phrase_ends=pend, density_at=dens_at,
                       tension_at=tens_at, phrase=a.phrase, density_damp=a.density_damp,
                       tension=a.tension)
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
                    fh = fig_hold.get((x.channel, round(on_b, 4), x.note))
                    if fh:                    # hold the figure's inner voice for the group
                        p_off = max(p_off, tm(on_b + fh) - min(0.04, 0.25 * (tm(on_b + fh) - p_on)))
                    if a.overhold > 0.0:
                        # hold on past the written value -- but stop short of this
                        # pitch's next strike (a string can only sound once).
                        held = tm(b + a.overhold)
                        seq = next_same.get((x.channel, x.note), ())
                        import bisect as _bs
                        i = _bs.bisect_right(seq, int(round(on_b * TPB)))
                        if i < len(seq):
                            held = min(held, tm(seq[i] / TPB) - 0.03)
                        p_off = max(p_off, min(held, p_off + a.overhold * 60.0 / a.bpm))
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
    if a.overhold > 0: extra += " | overhold %.1f" % a.overhold
    if a.figuration_hold > 0: extra += " | fig-hold %.2f (%d notes)" % (a.figuration_hold, len(fig_hold))
    if a.phrase or a.density_damp or a.tension:
        extra += " | phrase %.2f (%d ends) dens-damp %.2f tension %.2f" % (
            a.phrase, len(pend), a.density_damp, a.tension)
    print("wrote %s | %.0f beats @ %.0f bpm | %d/%d agogic %.2f | rit last %.0f x%.2f%s | len %.1fs"
          % (a.outp, total, a.bpm, num, den, a.agogic, a.rit_beats, a.rit_amount, extra, out.length))

if __name__ == "__main__":
    main()
