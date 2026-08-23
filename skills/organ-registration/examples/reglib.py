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
import mido


# --- reading a source ---------------------------------------------------------

def read_notes(mid, ti):
    """Notes of track `ti` as [(start_tick, end_tick, note, velocity)]."""
    t = 0; on = {}; out = []
    for msg in mid.tracks[ti]:
        t += msg.time
        if msg.type == 'note_on' and msg.velocity > 1:
            on.setdefault(msg.note, []).append((t, msg.velocity))
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity <= 1):
            q = on.get(msg.note)
            if q:
                s, v = q.pop(0); out.append((s, t, msg.note, v))
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


def conductor(name, tempo=None, src=None, time_signature=True):
    """The meta track. Carries the source's tempo and -- importantly -- its
    TIME SIGNATURE: baroque-agogics derives the metric grid from it, and a
    missing one silently makes a 6/8 fugue breathe in 4/4."""
    tr = mido.MidiTrack()
    if tempo is None and src is not None:
        tempo = get_tempo(src)
    tr.append(mido.MetaMessage('set_tempo', tempo=tempo or 500000, time=0))
    if time_signature and src is not None:
        ts = get_time_signature(src)
        if ts is not None:
            tr.append(ts.copy(time=0))
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
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
    A = mido.MidiFile(type=1, ticks_per_beat=TPB)
    B = mido.MidiFile(type=1, ticks_per_beat=TPB)
    for tr in m.tracks:
        ta, tb = mido.MidiTrack(), mido.MidiTrack()
        t = 0; lastA = 0; lastB = 0
        prog = {}; cc = {}; ts = None; tempo = None; open_notes = {}; pend = []
        for x in tr:
            t += x.time
            if t < cut:      # state must reflect the CUT, not the end of the piece
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


# --- stop masks ---------------------------------------------------------------
# Flue (prog 19): 0=8' 1=4' 2=2' 3=2-2/3' 4=16' 5=5-1/3' 6=Flute 7=Mixtur
# Reed (prog 20): 0=8' 1=16' 2=4' 3=Trumpet
F8, F4, F2, F223, F16, F513, FLUTE, MIXTUR = (1 << i for i in range(8))
R8, R16, R4, TRUMPET = (1 << i for i in range(4))

PLENUM      = F8 | F4 | F2 | F223           # Organo pleno
PLENUM_16   = PLENUM | F16                  # ...with gravity
FULL        = PLENUM_16 | MIXTUR            # the crown: add the Mixtur
PEDAL_FOUND = F8 | F16                      # pedal foundation, 16'+8'
