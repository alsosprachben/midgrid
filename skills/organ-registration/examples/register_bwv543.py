#!/usr/bin/env python3
"""Considerate registration of Bach, Prelude & Fugue in A minor, BWV 543, organ.

Source: the IMSLP LilyPond organ engraving (lekro, after Rust/BGA), compiled to
clean notation-derived MIDIs -- manual (right+left staves) and pedal cleanly
separated, no performance doublings. Two movements, registered separately then
concatenated for the P&F.

This is the "great" A minor -- brilliant and virtuosic, so unlike Contrapunctus 1
it wants a real plenum and reeds at the peaks. The special device is E. Power
Biggs's PEDAL-SOLO registration: when the pedal is exposed alone, draw brighter
pipes (4'+2') and the Posaune onto it so the line blazes, then push them back the
instant the manuals return -- timed into the gap, like the chorale switches.

  Great ch0 p19 flue  <- manuals (right+left)
  Pedal ch1 p19 flue  <- pedal        16+8 foundation, brightened for the solos
  Posaune ch2 p20 reed <- pedal       pedal-solo reed + fugue climax
  Trompette ch3 p20 reed <- manuals   fugue final cadence only

Prelude pedal solos (beats): 99-111 and 181-187 -- brighten, then RETRACT before
the manuals re-enter (111 / 187). Fugue ending solo 421-433 -- brighten, and let
it flow INTO the final plenum (manuals return full at 434, so no retract).
Stop word is 14-bit: CC11 = bits 0-6, CC43 = bits 7-13.
Flue bits: 0=8' 1=4' 2=2' 3=2 2/3' 4=16' 5=5 1/3' 6=Flute 7=Mixtur;
reed: 0=8' 1=16' 2=4' 3=Trumpet.

Sources: set BWV543_DIR to the directory holding ly543/ (the compiled LilyPond
MIDIs + the event-listener .notes log). See references/registration-bwv543.md
for the acquisition pipeline (IMSLP .ly -> lilypond -> ornaments -> register).
"""
import mido, os, sys
from fractions import Fraction
sys.path.insert(0, "/home/ben/repos/midgrid")
from kern2midi_ornaments import realize, MAJOR_STEPS   # shared C.P.E. Bach engine

SP = os.environ.get("BWV543_DIR", os.path.dirname(os.path.abspath(__file__)))
PREL_SRC  = os.path.join(SP, "ly543/bach_bwv543.midi")
FUGUE_SRC = os.path.join(SP, "ly543/bach_bwv543-1.midi")
NOTES     = os.path.join(SP, "ly543/ev543-unnamed-staff.notes")  # LilyPond event-listener log
PREL_DST  = "/home/ben/Downloads/bwv543_prelude_organ.mid"
FUGUE_DST = "/home/ben/Downloads/bwv543_fugue_organ.mid"

# The Fugue's 9 ornaments (mordent/prall/upprall) live only in the manuals. We take
# each ornament's exact (time, pitch, dur) from the event-listener log -- movement 1
# after the timeline reset -- and realize it with YOUR engine (every wavy sign -> a
# Bach trill-from-above, appui on long notes, on the beat), then splice the figure
# into the Great note list, replacing the plain principal.
A_MINOR = {(0 + s) % 12 for s in MAJOR_STEPS}      # fifths=0: C-major pc set == A natural minor
ORN = {'mordent': 'm', 'prall': 'w', 'upprall': 'w'}

def fugue_ornaments(TPB):
    rows = [l.rstrip('\n').split('\t') for l in open(NOTES)]
    mv = 0; hi = 0.0; prev = None; out = []
    for f in rows:
        if len(f) < 2: continue
        t = float(f[0])
        if f[1] == 'note':
            if t < hi - 5: mv += 1; hi = 0.0     # the 52.5 -> 0 reset = prelude|fugue
            hi = max(hi, t); prev = (t, int(f[2]), float(f[4]))
        elif f[1] == 'script' and f[2] in ORN and prev and mv == 1:  # fugue only
            t_wn, pitch, dur_wn = prev
            fig = realize(pitch, Fraction(dur_wn * 4).limit_denominator(64), ORN[f[2]], A_MINOR)
            tick = int(round(t_wn * 4 * TPB))
            out.append((tick, pitch, [(p, int(round(float(d) * TPB))) for p, d in fig]))
    return out

def apply_ornaments(notes, orns, TPB):
    """Replace each ornamented Great note (matched by onset+pitch) with its figure."""
    tol = TPB // 4
    for tick, pitch, fig in orns:
        best = None
        for i, (s, e, n, v) in enumerate(notes):
            if n == pitch and abs(s - tick) <= tol and (best is None or abs(s - tick) < abs(notes[best][0] - tick)):
                best = i
        if best is None:
            print("  !! ornament unmatched: tick", tick, "pitch", pitch); continue
        s, e, n, v = notes.pop(best); t = s
        for p, d in fig:
            notes.append((t, t + d, p, v)); t += d
    return notes

GREAT_TRACKS = [1, 2]   # right + left manual staves
PEDAL_TRACK  = 3        # pedal staff

# --- PRELUDE: bright toccata plenum + two pedal-solo brightenings (retracted) ---
# The manual plays ALONE for the first 9 bars (the pedal rests: R1 x8 in the
# source), so that opening flourish belongs on a light POSITIVE, not the full
# Great -- the Great takes over when the pedal enters at beat 36 and the texture
# fills out. Registering the solo opening on a plenum is far too heavy.
P_SOLO_END = 36
P_POS   = [(0, 0b000001), (P_SOLO_END, 0)]                # light 8' Positive, then tacet
P_GREAT = [(0, 0), (P_SOLO_END, 0b000011), (48, 0b000111)]  # silent, then 8+4 -> 8+4+2
P_PEDF  = [(0, 0b010001),                                 # 16+8 foundation
           (99, 0b010111), (110, 0b010001),               # solo 1: +4'+2', retract
           (181, 0b010111), (186, 0b010001)]              # solo 2: +4'+2', retract
P_PEDR  = [(0, 0),
           (99, 0b000011), (110, 0),                      # Posaune during solo 1
           (181, 0b000011), (186, 0)]                     # Posaune during solo 2

# --- FUGUE: parsimony build + ending pedal solo flowing into the plenum --------
MIX = 1 << 7   # Mixtur III (flue bit 7) -- crowns the fugue's final plenum
F_GREAT   = [(0, 0b000001), (90, 0b000011),               # 8' -> 8+4 (after exposition)
             (250, 0b000111), (400, 0b011111 | MIX)]      # 8+4+2 -> full+16+Mixtur (final)
F_PEDF    = [(0, 0b010001), (420, 0b010111)]              # 16+8 -> +4'+2' (ending solo -> plenum)
F_PEDR    = [(0, 0), (400, 0b000011)]                     # Posaune from the final section
F_TRUMPET = [(0, 0), (434, 0b001000)]                     # Great Trompette, final cadence

def read_notes(mid, ti):
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

def get_tempo(mid):
    for tr in mid.tracks:
        for x in tr:
            if x.type == 'set_tempo': return x.tempo
    return 500000

def make_channel_track(ch, prog, notes, mask_events, TPB):
    ev = [(0, 0, mido.Message('program_change', channel=ch, program=prog, time=0))]
    for beat, mask in mask_events:
        # 14-bit stop word: CC11 = bits 0-6, CC43 = bits 7-13 (the Mixtur is bit 7)
        ev.append((int(beat * TPB), 1, mido.Message('control_change', channel=ch, control=11, value=mask & 0x7F)))
        ev.append((int(beat * TPB), 1, mido.Message('control_change', channel=ch, control=43, value=(mask >> 7) & 0x7F)))
    for s, e, n, v in notes:
        ev.append((s, 2, mido.Message('note_on',  channel=ch, note=n, velocity=max(v, 40), time=0)))
        ev.append((e, 3, mido.Message('note_off', channel=ch, note=n, velocity=0, time=0)))
    ev.sort(key=lambda x: (x[0], x[1]))
    tr = mido.MidiTrack(); last = 0
    for tick, _, msg in ev:
        msg.time = tick - last; last = tick
        tr.append(msg)
    tr.append(mido.MetaMessage('end_of_track', time=0))
    return tr

def build(src, dst, GREAT, PEDF, PEDR, TRUMPET, name, orns=None, POSITIVE=None):
    m = mido.MidiFile(src); TPB = m.ticks_per_beat
    great = []
    for ti in GREAT_TRACKS: great += read_notes(m, ti)
    pedal = read_notes(m, PEDAL_TRACK)
    if orns:
        great = apply_ornaments(great, orns, TPB)
        print("  applied %d ornaments" % len(orns))
    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    cond = mido.MidiTrack()
    cond.append(mido.MetaMessage('set_tempo', tempo=get_tempo(m), time=0))
    for tr in m.tracks:                       # carry the time signature (meter) for agogics
        ts = next((x for x in tr if x.type == 'time_signature'), None)
        if ts: cond.append(ts.copy(time=0)); break
    cond.append(mido.MetaMessage('track_name', name=name, time=0))
    cond.append(mido.MetaMessage('end_of_track', time=0))
    out.tracks.append(cond)
    if POSITIVE is not None:
        # split the manual line: the solo opening to the Positive, the rest to the Great
        pos = [n for n in great if n[0] < P_SOLO_END * TPB]
        gre = [n for n in great if n[0] >= P_SOLO_END * TPB]
        out.tracks.append(make_channel_track(0, 19, gre, GREAT, TPB))
        out.tracks.append(make_channel_track(4, 19, pos, POSITIVE, TPB))
    else:
        out.tracks.append(make_channel_track(0, 19, great, GREAT, TPB))
    out.tracks.append(make_channel_track(1, 19, pedal, PEDF, TPB))
    out.tracks.append(make_channel_track(2, 20, pedal, PEDR, TPB))
    out.tracks.append(make_channel_track(3, 20, great, TRUMPET, TPB))
    out.save(dst)
    print("wrote", dst, "| TPB", TPB, "| len %.1fs" % out.length, "| great", len(great), "pedal", len(pedal))

if __name__ == "__main__":
    build(PREL_SRC, PREL_DST, P_GREAT, P_PEDF, P_PEDR, [(0, 0)], "BWV543 Prelude (organ)",
          POSITIVE=P_POS)
    fug_orns = fugue_ornaments(mido.MidiFile(FUGUE_SRC).ticks_per_beat)
    build(FUGUE_SRC, FUGUE_DST, F_GREAT, F_PEDF, F_PEDR, F_TRUMPET, "BWV543 Fugue (organ)", orns=fug_orns)
