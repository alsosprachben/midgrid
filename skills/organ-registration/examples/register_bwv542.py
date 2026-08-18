#!/usr/bin/env python3
"""Re-registration of BWV 542 from Martin Robinson's MIDI.

Keep his manual choreography (which division plays each passage) but extract the
8'-pitch musical lines, discard his octave-doubling tracks (4'/16'/32'), and
re-voice each division with my own stops via the CC11 bitfield -- all on the two
registerable organ voices (19 flue, 20 reed), using the cross-family FLUTE and
TRUMPET stops so everything stays hybrid-locked (his 'Trumpets' were GM prog 30,
which maps to a plucked string here).

  Great    ch0 p19 flue  <- src ch0   Principal 8+4+2+2 2/3, +16' for the close
  Positive ch1 p19 flue  <- src ch6   FLUTE stop (bit6) -- soft 8' flute
  Pedal    ch2 p19 flue  <- src ch2   16+8; bare 8' flute in the chorales; +5 1/3' close
  Ped reed ch3 p20 reed  <- src ch2   Posaune 16+8 (off in the chorales)
  Trumpets ch4 p20 reed  <- src ch8   TRUMPET stop (bit3), dynamic-locking chorus reed

The conductor/tempo track (rubato, 32 tempo events) is copied verbatim.
CC11 flue bits: 0=8' 1=4' 2=2' 3=2 2/3' 4=16' 5=5 1/3' 6=Flute;  reed: 0=8' 1=16' 2=4' 3=Trumpet.
"""
import mido

SRC = "/home/ben/Downloads/midi/bwv542.mid"
DST = "/home/ben/Downloads/bwv542_registered.mid"
TPB = 480
CLIMAX = 720 * TPB   # the final G-minor peroration draws everything

def read_channel(mid, chan):
    notes = []; on = {};
    for tr in mid.tracks:
        t = 0
        for x in tr:
            t += x.time
            if x.type == 'note_on' and x.velocity > 0 and x.channel == chan:
                on.setdefault(x.note, []).append((t, x.velocity))
            elif (x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0)) and x.channel == chan:
                q = on.get(x.note)
                if q: s, v = q.pop(0); notes.append((s, t, x.note, v))
    return notes

def track_from(ch, prog, notes, mask_events, transpose=0, cc7=None):
    ev = [(0, 0, mido.Message('program_change', channel=ch, program=prog, time=0))]
    # CC7 sets the level of NON-registerable voices (flute/brass), where
    # channel_volume = (CC7*CC11)^2; never send CC11 to them (CC11 is the stop
    # bitfield only for flue/reed, and CC11=0 would zero their volume -> silent).
    if cc7 is not None:
        ev.append((0, 0, mido.Message('control_change', channel=ch, control=7, value=cc7)))
    for tick, mask in mask_events:
        ev.append((tick, 1, mido.Message('control_change', channel=ch, control=11, value=mask)))
    for s, e, n, v in notes:
        nn = n + transpose
        if not (0 <= nn <= 127): continue
        ev.append((s, 2, mido.Message('note_on',  channel=ch, note=nn, velocity=v, time=0)))
        ev.append((e, 3, mido.Message('note_off', channel=ch, note=nn, velocity=0, time=0)))
    ev.sort(key=lambda x: (x[0], x[1]))
    tr = mido.MidiTrack(); last = 0
    for tick, _, msg in ev:
        msg.time = tick - last; last = tick
        tr.append(msg)
    tr.append(mido.MetaMessage('end_of_track', time=0))
    return tr

def main():
    src = mido.MidiFile(SRC)
    great = read_channel(src, 0); positive = read_channel(src, 6)
    pedal = read_channel(src, 2); trumpets = read_channel(src, 8)

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    out.tracks.append(src.tracks[0])   # conductor/tempo (rubato) verbatim

    # The two walking-bass chorale sections (Great rests, soft Positive over a
    # walking pedal) must stay SOFT: drop the Positive to a light chorus and pull
    # the pedal to a bare 8' with the reed off.  C1: beats 59-93, C2: 168-208.
    # Registration switches during the Great-silence GAP that IS the chorale, so
    # the change lands between notes -- not on the first/last chorale note's attack.
    # (gaps 57.1-94.5 and 165.7-210.6; Positive notes run to 94.3 / 209.9.)
    # C1b sits in the 94.48-94.52 gap: after the long pedal point (A2, held to
    # 94.48) finishes soft, just before the Great re-enters pleno at 94.52 -- so
    # the pedal point doesn't get loud at its tail.
    C1a, C1b = int(57.3*TPB), int(94.5*TPB)
    C2a, C2b = int(166.0*TPB), int(210.4*TPB)
    # per-section CC11 masks: (tick, mask), sorted.
    GREAT = [(0, 0b001111), (CLIMAX, 0b011111)]      # 8+4+2+2 2/3 ; +16' for the close
    POS   = [(0, 0b000011)]                          # soft chorale: 8+4 only
    PEDF  = [(0, 0b010001),                          # 16+8 (flue foundation)
             (C1a, 0b1000000), (C1b, 0b010001),      # chorale 1: bare 8' FLUTE (soft, flue-like)
             (C2a, 0b1000000), (C2b, 0b010001),      # chorale 2: bare 8' FLUTE
             (CLIMAX, 0b110001)]                     # +5 1/3' for the close
    PEDR  = [(0, 0b000011),                          # Posaune 8+16
             (C1a, 0), (C1b, 0b000011),              # reed off in chorale 1
             (C2a, 0), (C2b, 0b000011)]              # reed off in chorale 2

    out.tracks.append(track_from(0, 19, great, GREAT))
    out.tracks.append(track_from(1, 19, positive, [(0, 0b1000000)]))   # flue, FLUTE stop only (bit6) -- soft 8' flute, hybrid-locked
    out.tracks.append(track_from(2, 19, pedal, PEDF))
    out.tracks.append(track_from(3, 20, pedal, PEDR))
    out.tracks.append(track_from(4, 20, trumpets, [(0, 0b0001000)]))   # reed, TRUMPET stop (bit3) -- bright, consistent
    out.save(DST)
    print("wrote", DST, "| tracks", len(out.tracks), "| len %.1fs" % out.length,
          "| great", len(great), "pos", len(positive), "ped", len(pedal), "trump", len(trumpets))

if __name__ == "__main__":
    main()
