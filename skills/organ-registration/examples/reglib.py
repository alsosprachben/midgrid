#!/usr/bin/env python3
"""reglib -- shared mechanics for CC-driven organ registration generators.

Every registration script does the same four things: read the source's notes,
emit one MIDI track per division carrying a stop-mask timeline, carry the
source's meta (tempo AND time signature) across, and sometimes split a
multi-movement file. Those mechanics were duplicated verbatim across five
generators (`read_notes` was byte-identical in all of them); they live here now
so a new registration is only the *design* -- the divisions, the stops, and where
the terraces fall.

The registration DESIGN stays per-piece and hand-made. Only the plumbing is shared.
"""
import os
import mido

HERE = os.path.dirname(os.path.abspath(__file__))


# --- reading a source ---------------------------------------------------------

def read_notes(mid, ti, by_channel=True):
    """Notes of track `ti` as [(start_tick, end_tick, note, velocity)].

    Pairs note-on to note-off by (CHANNEL, pitch), not by pitch alone. When an
    engraving puts two voices on one staff -- `<< { ... } \\ { ... } >>`, which
    BWV 565's toccata uses throughout its broken-chord figures -- and the voices
    momentarily share a pitch, pairing by pitch alone matches the sustained
    voice's note-on to the passing voice's note-off. The durations swap: the held
    note comes out short and a passing note comes out long, so a figure written
    as a moving line over a sustained one is flattened into equal semiquavers.
    Compile with midi-voice-channels.ly so the voices are on separate channels
    and this pairing can tell them apart.
    """
    t = 0; on = {}; out = []
    for msg in mid.tracks[ti]:
        t += msg.time
        if msg.type not in ('note_on', 'note_off'): continue
        key = (msg.channel, msg.note) if by_channel else msg.note
        if msg.type == 'note_on' and msg.velocity > 1:
            on.setdefault(key, []).append((t, msg.velocity))
        else:
            q = on.get(key)
            if q:
                s, v = q.pop(0); out.append((s, t, msg.note, v))
    out.sort()
    return out


def read_channel(mid, chan):
    """Notes on MIDI channel `chan` gathered across every track. Use when the
    source is organised by channel (a performance MIDI) rather than by track."""
    notes = []; on = {}
    for tr in mid.tracks:
        t = 0
        for x in tr:
            t += x.time
            if x.type == 'note_on' and x.velocity > 0 and x.channel == chan:
                on.setdefault(x.note, []).append((t, x.velocity))
            elif (x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0)) \
                    and x.channel == chan:
                q = on.get(x.note)
                if q:
                    s, v = q.pop(0); notes.append((s, t, x.note, v))
    return notes


def read_tracks(mid, indices):
    """Notes of several tracks merged (e.g. the manual voices of one division)."""
    out = []
    for ti in indices:
        out += read_notes(mid, ti)
    return out


# --- emitting a registered division ------------------------------------------

def make_channel_track(ch, prog, notes, mask_events, TPB=None, unit='tick',
                       transpose=0, cc7=None, min_velocity=None):
    """One MIDI track = one organ division.

    `mask_events` is [(pos, stop_mask)]; `unit` says whether pos is in 'tick' or
    'beat' (beats need TPB). The mask is the **14-bit stop word**: CC11 carries
    bits 0-6 and CC43 bits 7-13, so the Mixtur (flue bit 7) is drawable. CC43=0
    reproduces the old 7-bit behaviour exactly.

    `cc7` is for NON-registerable voices (a plain BlownPipe/brass channel), where
    channel_volume = (CC7*CC11)^2 -- never send CC11=0 to those or they go silent.
    `transpose` shifts the whole line (an octave-doubling rank on its own channel).
    `min_velocity` floors the velocity (some engravings emit very soft notes).

    Event order at a shared tick is program change < controls < note-ons <
    note-offs, so a stop is drawn before the notes that should speak on it.
    """
    scale = (TPB if unit == 'beat' else 1)
    if unit == 'beat' and TPB is None:
        raise ValueError("unit='beat' needs TPB")
    ev = [(0, 0, mido.Message('program_change', channel=ch, program=prog, time=0))]
    if cc7 is not None:
        ev.append((0, 0, mido.Message('control_change', channel=ch, control=7, value=cc7)))
    for pos, mask in mask_events:
        tick = int(pos * scale)
        ev.append((tick, 1, mido.Message('control_change', channel=ch, control=11,
                                         value=mask & 0x7F)))
        ev.append((tick, 1, mido.Message('control_change', channel=ch, control=43,
                                         value=(mask >> 7) & 0x7F)))
    for s, e, n, v in notes:
        nn = n + transpose
        if not (0 <= nn <= 127):
            continue
        vv = max(v, min_velocity) if min_velocity is not None else v
        ev.append((s, 2, mido.Message('note_on',  channel=ch, note=nn, velocity=vv, time=0)))
        ev.append((e, 3, mido.Message('note_off', channel=ch, note=nn, velocity=0, time=0)))
    ev.sort(key=lambda x: (x[0], x[1]))
    tr = mido.MidiTrack(); last = 0
    for tick, _, msg in ev:
        msg.time = tick - last; last = tick
        tr.append(msg)
    tr.append(mido.MetaMessage('end_of_track', time=0))
    return tr


def conductor(name, tempo=None, src=None, time_signature=True, fermatas=(),
              arpeggios=()):
    """The meta track. Carries the source's tempo and -- importantly -- its
    TIME SIGNATURE: baroque-agogics derives the metric grid from it, and a
    missing one silently makes a 6/8 fugue breathe in 4/4.

    `fermatas` is [(tick, dur_ticks)] from read_fermatas; each becomes a marker
    the performer holds on. They live here rather than in a sidecar so they
    travel with the file through the movement split."""
    tr = mido.MidiTrack()
    if tempo is None and src is not None:
        tempo = get_tempo(src)
    tr.append(mido.MetaMessage('set_tempo', tempo=tempo or 500000, time=0))
    if time_signature and src is not None:
        ts = get_time_signature(src)
        if ts is not None:
            tr.append(ts.copy(time=0))
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    marks = fermata_markers(sorted(fermatas)) + arpeggio_markers(sorted(arpeggios))
    marks.sort(key=lambda tm: tm[0])
    last = 0
    for tick, msg in marks:
        tr.append(msg.copy(time=tick - last)); last = tick
    tr.append(mido.MetaMessage('end_of_track', time=0))
    return tr


def get_tempo(mid, default=500000):
    for tr in mid.tracks:
        for x in tr:
            if x.type == 'set_tempo':
                return x.tempo
    return default


def get_time_signature(mid):
    for tr in mid.tracks:
        for x in tr:
            if x.type == 'time_signature':
                return x
    return None


# --- multi-movement splitting -------------------------------------------------

def split_at(path, beat, outA, outB, verbose=True):
    """Split a registered MIDI at `beat` into two movement files, carrying the
    registration state across the cut: the program change and every CC's CURRENT
    value are restated at the start of part B, so the second movement opens on
    the stops that were actually drawn rather than on defaults. Notes still
    sounding at the cut are closed.

    Splitting matters because a single tempo and a single cadential rit cannot
    serve two movements -- each wants its own.
    """
    m = mido.MidiFile(path); TPB = m.ticks_per_beat; cut = int(beat * TPB)
    # A cut through a sounding note truncates it in A and loses it from B. Report
    # it: choosing a seam is a musical decision and it should not fail silently.
    crossing = 0
    for tr in m.tracks:
        t = 0; on = {}
        for x in tr:
            t += x.time
            if x.type == 'note_on' and x.velocity > 0:
                on.setdefault((x.channel, x.note), []).append(t)
            elif x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0):
                q = on.get((x.channel, x.note))
                if q and q.pop(0) < cut < t:
                    crossing += 1
    if crossing and verbose:
        print("  !! split at beat %.1f truncates %d sounding note(s) -- move the seam"
              % (beat, crossing))
    A = mido.MidiFile(type=1, ticks_per_beat=TPB)
    B = mido.MidiFile(type=1, ticks_per_beat=TPB)
    for tr in m.tracks:
        ta, tb = mido.MidiTrack(), mido.MidiTrack()
        t = 0; lastA = 0; lastB = 0
        prog = {}; cc = {}; ts = None; tempo = None; open_notes = {}; pend = []
        for x in tr:
            t += x.time
            # An event exactly AT the cut: a note-OFF belongs to part A (it closes a
            # note that started there); anything else belongs to part B. Without this
            # the note-offs of chords ending on the seam land in B as orphans and
            # immediately kill whatever legitimately begins at the cut -- which
            # silenced the opening note of BWV 582's fugue subject.
            is_off = x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0)
            if t < cut or (t == cut and is_off):
                if x.type == 'program_change': prog[x.channel] = x.program
                elif x.type == 'control_change': cc.setdefault(x.channel, {})[x.control] = x.value
                elif x.type == 'time_signature': ts = x
                elif x.type == 'set_tempo': tempo = x
                if x.type == 'note_on' and x.velocity > 0:
                    open_notes[(x.channel, x.note)] = True
                elif x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0):
                    open_notes.pop((x.channel, x.note), None)
                y = x.copy(time=t - lastA); lastA = t; ta.append(y)
            else:
                pend.append((t, x))
        for (ch, n) in list(open_notes):
            ta.append(mido.Message('note_off', channel=ch, note=n, velocity=0,
                                   time=max(0, cut - lastA)))
            lastA = cut
        ta.append(mido.MetaMessage('end_of_track', time=0)); A.tracks.append(ta)
        head = []
        if tempo is not None: head.append(tempo.copy(time=0))
        if ts is not None: head.append(ts.copy(time=0))
        for ch, p in prog.items():
            head.append(mido.Message('program_change', channel=ch, program=p, time=0))
        for ch, d in cc.items():
            for c, v in d.items():
                head.append(mido.Message('control_change', channel=ch, control=c, value=v, time=0))
        for h in head: tb.append(h)
        for t2, x in pend:
            if x.is_meta and x.type == 'end_of_track': continue
            y = x.copy(time=(t2 - cut) - lastB); lastB = t2 - cut; tb.append(y)
        tb.append(mido.MetaMessage('end_of_track', time=0)); B.tracks.append(tb)
    A.save(outA); B.save(outB)
    if verbose:
        print("split %s at beat %.1f -> %s (%.1fs) + %s (%.1fs)"
              % (path, beat, outA, A.length, outB, B.length))



# --- ornaments ----------------------------------------------------------------
# LilyPond's MIDI backend does NOT expand ornament signs: a \prall, \mordent or
# \trill in the score simply plays as a plain note. So every wavy sign in the
# notation is silently lost unless we put it back. We recover the signs from an
# event-listener log (emitted by mutopia_to_midi.py alongside each MIDI), and
# realize them with midgrid's own C.P.E. Bach engine -- Bach's wavy line is a
# trill FROM ABOVE, on the beat, appui on long notes -- rather than with
# LilyPond's articulate.ly, whose mordent-from-below reading is not Bach's.
#
# This bit us on BWV 565: its opening gesture is `a8 \fermata \prall`, and the
# render had no mordent at all on the most recognisable phrase in organ music.

from fractions import Fraction

# Every sign LilyPond can name, mapped to the engine's code. All wavy signs are
# one thing to Bach (a trill from above); only the turn is distinct.
# 'w' = trillo, from the note ABOVE.  'v' = Mordant, a bite to the note BELOW.
# 'S' = turn.  These are DIFFERENT signs in Bach's Explication and LilyPond prints
# them differently, so they must not be collapsed: mapping \mordent to 'w' (as
# this table first did) played 115 mordents across 25 works as upper trills.
ORNAMENT_SIGNS = {
    'prall': 'w', 'prallprall': 'w', 'upprall': 'w', 'downprall': 'w',
    'lineprall': 'w', 'trill': 'w', 'pralldown': 'w',
    'prallmordent': 'w',                     # begins as a prall; the trill reading holds
    'mordent': 'v', 'upmordent': 'v', 'downmordent': 'v',
    'turn': 'S', 'reverseturn': 'S',
}

MAJOR_STEPS = (0, 2, 4, 5, 7, 9, 11)

def scale_pcs(tonic_pc, mode='major'):
    """Pitch-class set of a key, for the ornament engine's neighbour lookup."""
    steps = MAJOR_STEPS if mode == 'major' else (0, 2, 3, 5, 7, 8, 10)
    return {(tonic_pc + s) % 12 for s in steps}

_MOMENT = __import__('re').compile(r'(-?\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)?$')

def _moment(tok):
    """Event-listener moments are whole notes, but a GRACE note is written as
    main+grace, e.g. "109.00000000-0.06250000" (a grace 1/16 whole-note before
    beat 109). Sum the two parts; a plain moment has no second part."""
    m = _MOMENT.match(tok.strip())
    if not m: raise ValueError("unparseable moment %r" % tok)
    return float(m.group(1)) + (float(m.group(2)) if m.group(2) else 0.0)

def ornament_logs(path):
    """Accept a .notes file, a directory, or a glob and return the log files.

    The listener writes one log PER STAFF, and how many there are depends on the
    engraving -- so a script that hard-codes one filename breaks silently the
    moment a work names its staves differently, and renders without ornaments
    while looking fine. Always point at the work directory.
    """
    import glob as _glob
    if os.path.isdir(path):
        return sorted(_glob.glob(os.path.join(path, "*.notes")))
    hits = sorted(_glob.glob(path))
    return hits if hits else ([path] if os.path.exists(path) else [])


def read_ornament_log(path, TPB, signs=None):
    """Parse event-listener .notes log(s) into [(tick, pitch, dur_ticks, sign)].

    `path` may be a file, a directory of logs, or a glob (see ornament_logs).

    A `script` line refers to the note logged just before it, so we pair each
    sign with the preceding `note`. Log times are in whole notes; ticks are
    4*TPB per whole note. Returns entries in time order.
    """
    signs = signs or ORNAMENT_SIGNS
    out = []
    files = ornament_logs(path)
    if not files:
        raise IOError("no event-listener log found at %r" % path)
    for f_ in files:
        prev = None            # a sign refers to the note before it, in ITS staff
        for line in open(f_):
            f = line.rstrip('\n').split('\t')
            if len(f) < 3: continue
            if f[1] == 'note':
                prev = (_moment(f[0]), int(f[2]),
                        _moment(f[4]) if len(f) > 4 else 0.0)
            elif f[1] == 'script' and f[2] in signs and prev:
                t_wn, pitch, dur_wn = prev
                out.append((int(round(t_wn * 4 * TPB)), pitch,
                            int(round(dur_wn * 4 * TPB)), signs[f[2]]))
    out.sort()
    return out

def realize_ornaments(orns, TPB, scale):
    """[(tick, pitch, dur, sign)] -> [(tick, pitch, [(pitch, dur_ticks), ...])].

    Uses midgrid's kern2midi_ornaments.realize (the C.P.E. Bach engine) so organ
    ornaments match the ones the harpsichord/clavier tooling produces.
    """
    import os, sys
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if root not in sys.path: sys.path.insert(0, root)
    from kern2midi_ornaments import realize
    out = []
    for tick, pitch, dur, sign in orns:
        if dur <= 0: continue
        fig = realize(pitch, Fraction(dur, TPB).limit_denominator(64), sign, scale)
        out.append((tick, pitch, [(p, int(round(float(d) * TPB))) for p, d in fig]))
    return out

def apply_ornaments(notes, figures, TPB, tol=None, verbose=True):
    """Replace each ornamented note (matched by onset+pitch) with its figure.

    `notes` is the [(start, end, pitch, vel)] list of ONE division. An ornament
    whose note is not in this division simply does not match -- that is how a
    manual ornament stays off the pedal -- so unmatched entries are counted, not
    an error. Returns (notes, n_applied).
    """
    tol = TPB // 4 if tol is None else tol
    applied = miss = 0
    for tick, pitch, fig in figures:
        best = None
        for i, (s, e, n, v) in enumerate(notes):
            if n == pitch and abs(s - tick) <= tol and (
                    best is None or abs(s - tick) < abs(notes[best][0] - tick)):
                best = i
        if best is None:
            miss += 1; continue
        s, e, n, v = notes.pop(best)
        t = s
        for p, d in fig:
            notes.append((t, min(t + d, e) if d else e, p, v)); t += d
        applied += 1
    notes.sort()
    if verbose:
        print("  ornaments: %d applied, %d not in this division" % (applied, miss))
    return notes, applied





# --- arpeggiated chords -------------------------------------------------------
# The \arpeggio sign is one more thing MIDI cannot carry. BWV 565 marks its big
# diminished chord in bar 3 and sets connectArpeggios, meaning the roll spans the
# staves as ONE gesture -- so the spread has to be collected across manuals, not
# per channel, or a chord split between divisions rolls twice.

def read_arpeggios(path, TPB):
    """[tick] for every notated \arpeggio, deduplicated across staves."""
    out = set()
    for f_ in ornament_logs(path):
        for line in open(f_):
            g = line.rstrip('\n').split('\t')
            if len(g) >= 2 and g[1].strip() == 'arpeggio':
                out.add(int(round(_moment(g[0]) * 4 * TPB)))
    return sorted(out)


def big_chords(notes, TPB, min_notes=4, min_beats=0.75, lo_tick=0, hi_tick=10**9):
    """Onsets of full sustained chords -- the ones a player spreads.

    Editorial, unlike read_arpeggios: the engraving marks only bar 3, but the
    weighty chords of a toccata are rolled as a matter of course, and a five-note
    chord struck dead flat on an organ sounds like a machine.
    """
    at = {}
    for s, e, p, v in notes:
        if lo_tick <= s < hi_tick and (e - s) >= min_beats * TPB:
            at.setdefault(s, []).append(p)
    return sorted(t for t, ps in at.items() if len(set(ps)) >= min_notes)


def arpeggio_markers(ticks):
    return [(t, mido.MetaMessage('marker', text='arpeggio', time=0)) for t in ticks]

# --- echoes -------------------------------------------------------------------

def find_echoes(notes, BAR, lo_bar=0, hi_bar=10**6, unit=0.5, min_notes=5):
    """Immediate LITERAL restatements: [(stmt0, stmt1, ans0, ans1)] in ticks.

    An echo is a figure played again, unchanged, straight away -- so we compare
    each `unit`-bar window with the next and require identical rhythm AND
    identical pitches. That is what the notation gives us; stems do not mark
    echoes, and neither does anything else in an engraving without registration
    marks. In BWV 565's fugue this finds the half-bar repeats in the right hand
    (bars 62-70) and then in the left (bars 73.5-81) -- the passage where the
    piece is plainly asking for two manuals.
    """
    step = unit * BAR
    def window(b0):
        return tuple(sorted((s - b0, p) for s, e, p, v in notes if b0 <= s < b0 + step))
    out = []
    b = lo_bar * BAR
    while b < hi_bar * BAR:
        x, y = window(b), window(b + step)
        if len(x) >= min_notes and x == y:
            out.append((int(b), int(b + step), int(b + step), int(b + 2 * step)))
            b += 2 * step
        else:
            b += step
    return out


def split_echoes(notes, pairs):
    """-> (statement_notes, answer_notes, other_notes) for one hand."""
    stmt, ans, other = [], [], []
    for n in notes:
        s = n[0]
        for s0, s1, a0, a1 in pairs:
            if s0 <= s < s1: stmt.append(n); break
            if a0 <= s < a1: ans.append(n); break
        else:
            other.append(n)
    return stmt, ans, other

# --- fermatas -----------------------------------------------------------------
# A fermata is the most basic timing instruction notation has, and MIDI cannot
# carry it either -- so, like the ornaments, it survives only in the listener log
# and we were ignoring all of them. In BWV 565 that is not a detail: the opening
# gesture is built on fermatas, and the last three articulate the whole close.
#
# We pass them to the performer as MIDI MARKERS in the conductor track, so they
# ride along inside the file itself -- through the movement split and anything
# else -- instead of in a sidecar that can go missing.

def read_fermatas(path, TPB):
    """[(tick, dur_ticks)] for every fermata, deduplicated across staves.

    A fermata over a chord is logged once per staff and once per note, all at the
    same moment; the hold belongs to the longest of them, and it applies to the
    whole texture, so collapse them by onset.
    """
    best = {}
    for f_ in ornament_logs(path):
        prev = None
        for line in open(f_):
            g = line.rstrip('\n').split('\t')
            if len(g) < 3: continue
            if g[1] == 'note':
                prev = (_moment(g[0]), _moment(g[4]) if len(g) > 4 else 0.0)
            elif g[1] == 'script' and g[2].strip() == 'fermata' and prev:
                t = int(round(prev[0] * 4 * TPB)); d = int(round(prev[1] * 4 * TPB))
                best[t] = max(best.get(t, 0), d)
    return sorted(best.items())


def fermata_markers(fermatas):
    """Fermatas as (tick, MetaMessage) pairs, ready for a conductor track."""
    return [(t, mido.MetaMessage('marker', text='fermata:%d' % d, time=0))
            for t, d in fermatas]

# --- stop masks ---------------------------------------------------------------
# Flue (prog 19): 0=8' 1=4' 2=2' 3=2-2/3' 4=16' 5=5-1/3' 6=Flute 7=Mixtur
# Reed (prog 20): 0=8' 1=16' 2=4' 3=Trumpet
F8, F4, F2, F223, F16, F513, FLUTE, MIXTUR = (1 << i for i in range(8))
R8, R16, R4, TRUMPET = (1 << i for i in range(4))

PLENUM      = F8 | F4 | F2 | F223           # Organo pleno
PLENUM_16   = PLENUM | F16                  # ...with gravity
FULL        = PLENUM_16 | MIXTUR            # the crown: add the Mixtur
PEDAL_FOUND = F8 | F16                      # pedal foundation, 16'+8'
