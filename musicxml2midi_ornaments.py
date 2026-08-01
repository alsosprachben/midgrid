#!/usr/bin/env python3
"""MusicXML -> piano MIDI, realizing ornaments per C.P.E. Bach -- the same engine
as kern2midi_ornaments.py, with a MusicXML reader in front (for pieces that exist
only as MusicXML, e.g. the keyboard toccatas). Reuses realize()/neighbor().

Handles: multi-part, multi-staff, multi-voice (<backup>/<forward>), chords,
grace notes (struck ON THE BEAT of the following note -- Baroque appoggiatura),
ties, and <notations><ornaments> markup (trill-mark, mordent=lower,
inverted-mordent=upper short trill / Pralltriller, turn, inverted-turn).
All voices render as one piano; the synth's keyboard pan places notes by pitch.

Accepts .musicxml/.xml (plain) or .mxl (zipped container)."""
import sys, zipfile
import xml.etree.ElementTree as ET
from fractions import Fraction
from collections import defaultdict
from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from kern2midi_ornaments import realize, MAJOR_STEPS   # shared C.P.E. Bach engine

STEP = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
# MusicXML ornament element -> our realize() code (auxiliaries stay diatonic):
ORN = {'trill-mark':'t', 'mordent':'m', 'inverted-mordent':'w',
       'turn':'S', 'inverted-turn':'$', 'delayed-turn':'S'}

def load_root(path):
    if path.endswith('.mxl'):                                  # zipped container
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.endswith('.xml') and not n.startswith('META')]
            # the container points at the rootfile; fall back to first score xml
            main = names[0]
            try:
                cont = ET.fromstring(z.read('META-INF/container.xml'))
                rf = cont.find('.//{*}rootfile')
                if rf is not None:
                    main = rf.get('full-path')
            except KeyError:
                pass
            return ET.fromstring(z.read(main))
    return ET.parse(path).getroot()

def local(tag):
    return tag.rsplit('}', 1)[-1]

def scale_from_fifths(fifths):
    mt = (7 * fifths) % 12                                      # major tonic pc for this signature
    return {(mt + s) % 12 for s in MAJOR_STEPS}                 # natural-minor shares the set

def pitch_midi(note):
    p = note.find('{*}pitch')
    if p is None:
        return None                                            # rest
    step = p.findtext('{*}step'); octave = int(p.findtext('{*}octave'))
    alter = int(p.findtext('{*}alter') or 0)
    return 12 * (octave + 1) + STEP[step] + alter

def note_ornament(note):
    orn = note.find('.//{*}ornaments')
    if orn is None:
        return None
    for child in orn:
        code = ORN.get(local(child.tag))
        if code:
            return code
    return None

GRACE_TYPE = {'half': Fraction(2), 'quarter': Fraction(1), 'eighth': Fraction(1, 2),
              '16th': Fraction(1, 4), '32nd': Fraction(1, 8), '64th': Fraction(1, 16)}

def parse_musicxml(root):
    """Return (voices dict {vid:[{onset,dur,midi}]}, scale, quarter_bpm)."""
    voices = defaultdict(list); pending = {}; pend_grace = defaultdict(list)
    scale = {0,2,4,5,7,9,11}; bpm = None
    for part in root.findall('{*}part'):
        pid = part.get('id'); divisions = 1; measure_start = Fraction(0)
        for measure in part.findall('{*}measure'):
            cursor = Fraction(0); max_cursor = Fraction(0)
            for el in measure:
                tag = local(el.tag)
                if tag == 'attributes':
                    d = el.findtext('{*}divisions')
                    if d: divisions = int(d)
                    f = el.find('{*}key/{*}fifths')
                    if f is not None: scale = scale_from_fifths(int(f.text))
                elif tag == 'direction':
                    sound = el.find('.//{*}sound[@tempo]')
                    if sound is not None and bpm is None:
                        bpm = float(sound.get('tempo'))
                elif tag == 'backup':
                    cursor -= Fraction(int(el.findtext('{*}duration')), divisions)
                elif tag == 'forward':
                    cursor += Fraction(int(el.findtext('{*}duration')), divisions)
                elif tag == 'note':
                    is_chord = el.find('{*}chord') is not None
                    is_grace = el.find('{*}grace') is not None
                    voice = el.findtext('{*}voice') or '1'
                    staff = el.findtext('{*}staff') or '1'
                    vid = '%s.%s.%s' % (pid, staff, voice)
                    dur_el = el.findtext('{*}duration')
                    dur = Fraction(int(dur_el), divisions) if dur_el else Fraction(0)
                    midi = pitch_midi(el)
                    tie = None
                    for t in el.findall('{*}tie'):
                        tie = 'start' if t.get('type') == 'start' else 'end'
                    onset = measure_start + (cursor if not is_chord else prev_onset_rel)
                    if is_chord:
                        cursor_advance = Fraction(0)                # chord: same onset, no advance
                    else:
                        prev_onset_rel = cursor; cursor_advance = dur
                    if midi is None:                                # rest
                        if pending.get(vid): voices[vid].append(pending.pop(vid))
                    elif is_grace:                                  # zero metric time, realized
                        gtype = el.findtext('{*}type')             # ON the beat of the next note
                        gnom = GRACE_TYPE.get(gtype, Fraction(1, 4))
                        pend_grace[vid].append({'midi': midi, 'dur': gnom})
                        cursor_advance = Fraction(0)
                    elif pending.get(vid) and tie == 'end' and pending[vid]['midi'] == midi:
                        pending[vid]['dur'] += dur
                        voices[vid].append(pending.pop(vid))
                    else:
                        if pending.get(vid): voices[vid].append(pending.pop(vid))
                        gl = pend_grace.pop(vid, None)             # lay grace(s) on the beat
                        if gl and not is_chord:
                            gtot = min(sum(x['dur'] for x in gl), dur / 4)  # crisp on-beat grace
                            wsum = sum(x['dur'] for x in gl) or 1
                            at = onset
                            for x in gl:
                                gd = gtot * x['dur'] / wsum
                                voices[vid].append({'onset': at, 'dur': gd, 'midi': x['midi']}); at += gd
                            onset = onset + gtot; dur = dur - gtot  # main note shortened, starts after
                        orn = note_ornament(el)
                        if tie == 'start' and orn:                 # ornament on a tied note: realize
                            seq = realize(midi, dur, orn, scale)   #   at onset, carry final principal
                            at = onset                             #   as the tie (was DROPPED)
                            for m, d in seq[:-1]:
                                voices[vid].append({'onset': at, 'dur': d, 'midi': m}); at += d
                            lm, ld = seq[-1]
                            pending[vid] = {'onset': at, 'dur': ld, 'midi': lm}
                        elif tie == 'start':
                            pending[vid] = {'onset': onset, 'dur': dur, 'midi': midi}
                        else:
                            if orn:
                                at = onset
                                for m, d in realize(midi, dur, orn, scale):
                                    voices[vid].append({'onset': at, 'dur': d, 'midi': m}); at += d
                            else:
                                voices[vid].append({'onset': onset, 'dur': dur, 'midi': midi})
                    if not is_chord:
                        cursor += cursor_advance
                    max_cursor = max(max_cursor, cursor)
            measure_start += max_cursor
    for vid, p in pending.items():
        voices[vid].append(p)
    return voices, scale, bpm

def main(inp, outp, bpm=None, vel=88):
    voices, scale, xbpm = parse_musicxml(load_root(inp))
    if bpm is None:
        bpm = xbpm or 100
    ppq = 480; mid = MidiFile(ticks_per_beat=ppq)
    for vi, vid in enumerate(sorted(voices)):
        tr = MidiTrack(); mid.tracks.append(tr); ch = vi % 16
        if vi == 0:
            tr.append(MetaMessage('set_tempo', tempo=bpm2tempo(int(bpm)), time=0))
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
    print("saved %s  voices=%d notes=%s  bars~%.0f  dur~%.0fs @ %dbpm"
          % (outp, len(voices), sum(len(v) for v in voices.values()), total/4, total*60.0/bpm, bpm))

if __name__ == '__main__':
    a = sys.argv
    main(a[1], a[2], int(a[3]) if len(a) > 3 else None)
