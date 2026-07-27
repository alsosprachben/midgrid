#!/usr/bin/env python3
"""kern (N monophonic spines, splits/merges allowed) -> piano MIDI, realizing
ornaments per C.P.E. Bach (Versuch, 1753):
  * trill  (t/T): start ON THE UPPER auxiliary, on the beat, alternate rapidly,
                  end on the principal (so a written termination flows on).
  * mordent(m/M): principal - lower auxiliary - principal, on the beat, snapped.
  * inv.mordent/Schneller (w/W): principal - upper - principal.
  * turn (S/s/$): upper - principal - lower - principal.
Auxiliaries are the DIATONIC neighbours in the parsed key (kern's t/T etc. size
hint is honoured only where it agrees; the diatonic neighbour is musically right,
e.g. Bb's lower neighbour is A -- a semitone -- even though the token is 'M').

Handles **kern spine splits (*^) and merges (*v *v): a voice that divides into a
divisi (e.g. Contrapunctus 11's final cadence) is tracked with absolute time and
emitted as an extra voice. All voices render as one piano (no pan; the synth's
keyboard pan places notes by pitch)."""
import re, sys
from fractions import Fraction
from collections import defaultdict
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

PC = {'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}
MAJOR_STEPS = [0,2,4,5,7,9,11]
NAT_MINOR_STEPS = [0,2,3,5,7,8,10]

def parse_key(lines):
    tonic_pc, minor = 2, True                        # default D minor
    for l in lines:
        if not l.startswith('*'):
            continue
        m = re.match(r'^\*([a-gA-G])([#-]*):', l.split('\t')[0])
        if m:
            tonic_pc = (PC[m.group(1).lower()] + m.group(2).count('#') - m.group(2).count('-')) % 12
            minor = m.group(1).islower()
            break
    steps = NAT_MINOR_STEPS if minor else MAJOR_STEPS
    return {(tonic_pc + s) % 12 for s in steps}

def parse_pitch(tok):
    m = re.search(r'([a-gA-G]+)', tok)
    if not m:
        return None                                  # rest
    letters = m.group(1); low = letters[0].islower(); nlet = len(letters)
    octave = (3 + nlet) if low else (4 - nlet)       # c->C4, C->C3, CC->C2
    return 12*(octave+1) + PC[letters[0].lower()] + tok.count('#') - tok.count('-')

def parse_dur(tok):
    m = re.search(r'(\d+)(\.*)', tok)
    num = int(m.group(1)); dots = len(m.group(2))
    return Fraction(4, num) * (2 - Fraction(1, 2**dots))   # quarter-note units

def neighbor(midi, up, scale):
    pc = midi % 12
    for d in range(1, 13):
        if up and (pc + d) % 12 in scale: return midi + d
        if not up and (pc - d) % 12 in scale: return midi - d
    return midi + (2 if up else -2)

def realize(midi, dur, orn, scale):
    """Return [(midi, dur), ...] filling `dur`, per C.P.E. Bach."""
    g = min(Fraction(1, 8), dur / 4)                 # a 32nd note (quarter units)
    if orn in 'mM':                                  # lower mordent
        return [(midi, g), (neighbor(midi, False, scale), g), (midi, dur - 2*g)]
    if orn in 'wW':                                  # inverted mordent / Schneller
        return [(midi, g), (neighbor(midi, True, scale), g), (midi, dur - 2*g)]
    if orn in 'Ss$':                                 # turn: upper-principal-lower-principal
        hi = neighbor(midi, True, scale); lo = neighbor(midi, False, scale)
        q = min(g, dur/4)
        return [(hi, q), (midi, q), (lo, q), (midi, dur - 3*q)]
    if orn in 'tT':                                  # trill: upper-start, end on principal
        hi = neighbor(midi, True, scale); pair = 2*g
        k = max(1, int(dur / pair)); seq = []
        for _ in range(k):
            seq += [(hi, g), (midi, g)]
        rem = dur - k*pair
        if rem > 0:
            m0, d0 = seq[-1]; seq[-1] = (m0, d0 + rem)
        return seq
    return [(midi, dur)]

def parse_score(lines, scale):
    """Track spine layout (splits/merges) and return {voice_id: [note,...]}."""
    voices = defaultdict(list); pending = {}; layout = None; next_vid = 0
    for l in lines:
        if not l:
            continue
        cols = l.split('\t')
        if l.startswith('**'):                       # exclusive interp: one entry/spine
            layout = [{'vid': i, 'time': Fraction(0)} for i in range(len(cols))]
            next_vid = len(cols); continue
        if layout is None or l[0] == '!':
            continue
        if l[0] == '=':                              # barline
            continue
        if l[0] == '*':                              # spine manipulation
            new = []; i = 0
            while i < len(cols) and i < len(layout):
                t = cols[i]; cur = layout[i]
                if t == '*^':                        # split: child inherits time
                    new.append({'vid': cur['vid'], 'time': cur['time']})
                    new.append({'vid': next_vid, 'time': cur['time']}); next_vid += 1
                    i += 1
                elif t == '*v':                      # merge a run of *v into one
                    new.append({'vid': cur['vid'], 'time': cur['time']})
                    i += 1
                    while i < len(cols) and cols[i] == '*v':
                        i += 1
                elif t == '*-':                      # terminate spine
                    i += 1
                else:
                    new.append({'vid': cur['vid'], 'time': cur['time']}); i += 1
            layout = new; continue
        for ci in range(min(len(cols), len(layout))):     # data line
            tok = cols[ci]
            if tok in ('.', ''):
                continue
            vid = layout[ci]['vid']; t = layout[ci]['time']
            dur = parse_dur(tok); midi = parse_pitch(tok)
            tie = 'start' if '[' in tok else ('end' if ']' in tok else ('mid' if '_' in tok else None))
            orn = next((c for c in tok if c in 'tTmMwWSs$'), None)
            if midi is None:                         # rest
                if pending.get(vid):
                    voices[vid].append(pending.pop(vid))
                layout[ci]['time'] = t + dur; continue
            if 'q' in tok or 'Q' in tok:             # grace note: ZERO metric time
                gd = min(dur, Fraction(1, 8))        # a quick acciaccatura, before the beat
                voices[vid].append({'onset': max(Fraction(0), t - gd), 'dur': gd, 'midi': midi})
                continue                             # do NOT advance the clock
            if pending.get(vid) and tie in ('mid', 'end') and midi == pending[vid]['midi']:
                pending[vid]['dur'] += dur; layout[ci]['time'] = t + dur
                if tie == 'end':
                    voices[vid].append(pending.pop(vid))
                continue
            if pending.get(vid):
                voices[vid].append(pending.pop(vid))
            if tie == 'start':
                pending[vid] = {'onset': t, 'dur': dur, 'midi': midi}
            elif orn:
                at = t
                for m, d in realize(midi, dur, orn, scale):
                    voices[vid].append({'onset': at, 'dur': d, 'midi': m}); at += d
            else:
                voices[vid].append({'onset': t, 'dur': dur, 'midi': midi})
            layout[ci]['time'] = t + dur
    for vid, p in pending.items():
        if p:
            voices[vid].append(p)
    return voices

def main(inp, outp, bpm=144, vel=88):
    lines = [l.rstrip('\n') for l in open(inp)]
    voices = parse_score(lines, parse_key(lines))
    ppq = 480; mid = MidiFile(ticks_per_beat=ppq)
    for vi, vid in enumerate(sorted(voices)):
        tr = MidiTrack(); mid.tracks.append(tr); ch = vi % 16
        if vi == 0:
            tr.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))
        tr.append(Message('program_change', program=0, channel=ch, time=0))
        tr.append(Message('control_change', control=7, value=110, channel=ch, time=0))
        ev = []
        for nt in voices[vid]:
            on = int(round(nt['onset']*ppq)); off = int(round((nt['onset']+nt['dur'])*ppq))
            if off <= on: off = on + 1
            ev.append((on, 1, nt['midi'])); ev.append((off, 0, nt['midi']))
        ev.sort(key=lambda e: (e[0], e[1])); last = 0
        for tick, typ, m in ev:
            tr.append(Message('note_on' if typ else 'note_off', note=m,
                              velocity=vel if typ else 0, channel=ch, time=tick-last))
            last = tick
    mid.save(outp)
    total = max((max((float(n['onset']+n['dur']) for n in v), default=0) for v in voices.values()), default=0)
    print("saved %s  voices=%s  bars~%.0f  dur~%.0fs @ %dbpm"
          % (outp, [len(v) for v in voices.values()], total/4, total*60.0/bpm, bpm))

if __name__ == '__main__':
    a = sys.argv
    main(a[1], a[2], int(a[3]) if len(a) > 3 else 144)
