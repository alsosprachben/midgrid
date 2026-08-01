#!/usr/bin/env python3
"""kern (N monophonic spines, splits/merges allowed) -> piano MIDI, realizing
ornaments the BAROQUE / Bach-specific way -- J.S. Bach's own Explication
(Clavier-Buechlein fuer W.F. Bach, 1720) as refined by C.P.E. Bach (Versuch,
1753). Every ornament begins ON THE BEAT.
  Bach's wavy-line sign is an UPPER-note TRILL: it begins on the note ABOVE, so
  the first motion falls to the principal, alternates rapidly, and ends on the
  principal. It is NOT a mordent (a mordent's sign has a vertical stroke through
  it; Bach's here do not -- verified against the Henle urtext of Canon alla
  Ottava). Craig Sapp's AoF kern encodes these signs variously as t/T, m/M, and
  w/W ("mordent"/"inverted mordent" in Humdrum), but they are all the same trill,
  so ALL of t/T/m/M/w/W realize as a trill from above.
  * trill (t/T/m/M/w/W): upper-auxiliary start, on the beat, alternate, end on
                  the principal. Long/cadential notes get a supported (appui)
                  start -- lean on the upper note, then trill (Henle draws these
                  with a prefix hook); short notes give a plain Pralltriller.
  * turn (S/s/$): upper - principal - lower - principal.
  * grace / Vorschlag (q/Q): struck ON THE BEAT of the following note, stealing
                  time from it (Baroque appoggiatura), NOT anticipated before it.
Auxiliaries are the DIATONIC neighbours in the parsed key (so g#'s upper is A, a
semitone; g's upper is A, a whole tone -- musically right regardless of token).

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

def parse_mm(lines, default=144):
    for l in lines:
        if l.startswith('*'):
            m = re.search(r'\*MM(\d+)', l)
            if m:
                return int(m.group(1))
    return default

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
    m = re.search(r'(\d+)(?:%(\d+))?(\.*)', tok)
    numstr = m.group(1); den = m.group(2); dots = len(m.group(3)); num = int(numstr)
    # kern: 1=whole, 2=half, ... ; 0=breve (2 wholes), 00=longa, 000=maxima;
    # N%D is a rational reciprocal duration (e.g. 12%5 -> reciprocal 12/5).
    if num == 0:
        base = Fraction(4 * (2 ** len(numstr)))
    elif den:
        base = Fraction(4) / Fraction(num, int(den))
    else:
        base = Fraction(4, num)
    return base * (2 - Fraction(1, 2**dots))               # quarter-note units

def neighbor(midi, up, scale):
    pc = midi % 12
    for d in range(1, 13):
        if up and (pc + d) % 12 in scale: return midi + d
        if not up and (pc - d) % 12 in scale: return midi - d
    return midi + (2 if up else -2)

def _trill(principal, upper, dur, g, appuy=False):
    """Trill from ABOVE (Bach's wavy sign): begin on the `upper` auxiliary, so the
    first motion falls to the principal, alternate rapidly, END on the principal
    (held for the remainder -> flows into a tie or the next note).  With `appuy`
    (a supported/cadential trill) it leans on the upper note first, then trills --
    the sign drawn in Henle with a prefix hook; self-scaled to longer notes."""
    if appuy:
        lean = min(dur / 3, 3 * g)                   # dwell on the upper note (the "appui")
        rem = dur - lean; pair = 2 * g
        k = max(1, int((rem - g) / pair))            # then trill, resolving DOWN to the principal
        body = []
        for _ in range(k):
            body += [(principal, g), (upper, g)]
        return [(upper, lean)] + body + [(principal, rem - k * pair)]
    pair = 2 * g
    k = max(1, int(dur / pair)); seq = []
    for _ in range(k):
        seq += [(upper, g), (principal, g)]
    rem = dur - k * pair                             # hold the final principal
    if rem > 0:
        m0, d0 = seq[-1]; seq[-1] = (m0, d0 + rem)
    return seq

def realize(midi, dur, orn, scale):
    """Return [(midi, dur), ...] filling `dur`, per J.S. Bach's own Explication
    (Clavier-Buechlein 1720) as refined by C.P.E. Bach (Versuch 1753).  Bach's
    wavy-line sign is an UPPER-note trill (begins above, first motion downward),
    NOT a mordent -- so t/T/m/M/w/W (however the source encodes the sign) all
    realize as a trill from above.  Long/cadential notes get a supported (appui)
    start; short notes a plain Pralltriller.  Every ornament begins on the beat."""
    g = min(Fraction(1, 8), dur / 4)                 # a 32nd-note pulse (quarter units)
    hi = neighbor(midi, True, scale)
    lo = neighbor(midi, False, scale)
    if orn in 'Ss$':                                 # turn: upper-principal-lower-principal
        q = min(g, dur / 4)
        return [(hi, q), (midi, q), (lo, q), (midi, dur - 3 * q)]
    if orn in 'tTmMwW':                              # every wavy sign -> trill from above
        return _trill(midi, hi, dur, g, appuy=(dur >= 1))
    return [(midi, dur)]

def parse_score(lines, scale):
    """Track spine layout (splits/merges) and return {voice_id: [note,...]}."""
    voices = defaultdict(list); pending = {}; graces = defaultdict(list)
    layout = None; next_vid = 0
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
            if 'q' in tok or 'Q' in tok:             # grace note: ZERO metric time, realized
                graces[vid].append({'midi': midi, 'dur': dur})   # ON the beat of the NEXT note
                continue                             # (Baroque Vorschlag) -- do NOT advance the clock
            wdur = dur                               # written value drives the metric clock...
            onset = t                                # ...but a pending grace steals from the sound
            gl = graces.pop(vid, None)
            if gl and tie != 'end':                  # lay the grace(s) on the beat, before the note
                gtot = min(sum(x['dur'] for x in gl), dur / 4)   # a crisp on-beat grace (<= 1/4 note)
                wsum = sum(x['dur'] for x in gl) or 1
                at = t
                for x in gl:
                    gd = gtot * x['dur'] / wsum
                    voices[vid].append({'onset': at, 'dur': gd, 'midi': x['midi']}); at += gd
                onset = t + gtot; dur = dur - gtot   # main note starts after the grace, shortened
            if pending.get(vid) and tie in ('mid', 'end') and midi == pending[vid]['midi']:
                pending[vid]['dur'] += dur; layout[ci]['time'] = t + wdur
                if tie == 'end':
                    voices[vid].append(pending.pop(vid))
                continue
            if pending.get(vid):
                voices[vid].append(pending.pop(vid))
            if tie == 'start' and orn:               # ornament on a tied note: realize it at the
                seq = realize(midi, dur, orn, scale) #   onset, then carry the final principal as the
                at = onset                           #   tie so the held note flows on (was DROPPED)
                for m, d in seq[:-1]:
                    voices[vid].append({'onset': at, 'dur': d, 'midi': m}); at += d
                lm, ld = seq[-1]
                pending[vid] = {'onset': at, 'dur': ld, 'midi': lm}
            elif tie == 'start':
                pending[vid] = {'onset': onset, 'dur': dur, 'midi': midi}
            elif orn:
                at = onset
                for m, d in realize(midi, dur, orn, scale):
                    voices[vid].append({'onset': at, 'dur': d, 'midi': m}); at += d
            else:
                voices[vid].append({'onset': onset, 'dur': dur, 'midi': midi})
            layout[ci]['time'] = t + wdur
    for vid, p in pending.items():
        if p:
            voices[vid].append(p)
    return voices

def main(inp, outp, bpm=None, vel=88):
    lines = [l.rstrip('\n') for l in open(inp)]
    if bpm is None:
        bpm = parse_mm(lines)                        # honour the score's *MM (quarter BPM)
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
    main(a[1], a[2], int(a[3]) if len(a) > 3 else None)
