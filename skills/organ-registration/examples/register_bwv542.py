#!/usr/bin/env python3
"""Re-registration of BWV 542 from Martin Robinson's MIDI, for the ONE organ.

Keep his manual choreography (which division plays each passage) but extract the
8'-pitch musical lines, discard his octave-doubling tracks (4'/16'/32'), and
re-voice each division with my own stops. Everything is GM 19, the church
organ's single console: flue ranks on bits 0-7, the reeds on 8-11 and the
Bourdon 16' on 12, drawn with the 14-bit stop word (CC11 low seven, CC43 high).
His 'Trumpets' were GM prog 30, a distortion guitar here; they get the console's
trumpet stop, a brass spectrum on a reed pipe.

  Great    ch0 <- src ch0   Principal 8+4+2+2 2/3; +16' and the Mixtur for the close
  Positive ch1 <- src ch6   Flute 8', soft
  Pedal    ch2 <- src ch2   ONE division, flue and reed drawn together:
                            Principal 16+8 with the Posaune (reed 16+8);
                            the chorales: Bourdon 16' + Flute 8', reed off;
                            +5 1/3' for the close
  Trumpets ch3 <- src ch8   Trumpet 8'

THE PEDAL IS ONE DIVISION NOW. It was two channels playing the same notes --
flue on 19, Posaune on 20 -- because the reeds had their own program then. On
the console the Posaune is a stop of the pedal, so the notes are played once
and the stop word draws both families.

THE CHORALE PEDAL GETS THE BOURDON. The two walking-bass chorales need the
pedal soft; it used to be a bare 8' flute, for want of a soft 16'. The stopped
Bourdon 16' (bit 12) under the flute is the classic soft pedal.

The conductor/tempo track (rubato, 32 tempo events) is copied verbatim.
"""
import mido, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reglib import (read_channel, make_channel_track as track_from, CONSOLE_PROGRAM,
                    CONSOLE_REED_SHIFT, F8, F4, F2, F223, F16, F513, FLUTE, MIXTUR,
                    BOURDON16, R8, R16, TRUMPET)

SRC = "/home/ben/Downloads/midi/bwv542.mid"
DST = "/home/ben/Downloads/bwx-renders/bwv542/bwv542_console.mid"
TPB = 480
CLIMAX = 720 * TPB   # the final G-minor peroration draws everything

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
    # per-division stop words: (tick, mask), sorted. REED(x) moves the old
    # 4-bit reed word onto the console's reed bits.
    REED = lambda m: m << CONSOLE_REED_SHIFT
    GREAT = [(0, F8 | F4 | F2 | F223),                       # Organo pleno
             (CLIMAX, F8 | F4 | F2 | F223 | F16 | MIXTUR)]   # +16' and the Mixtur for the close
    POS   = [(0, FLUTE)]                                     # soft 8' flute
    PED_PLENO = F16 | F8 | REED(R16 | R8)                    # principals 16+8, Posaune 16+8
    PED_SOFT  = BOURDON16 | FLUTE                            # the chorales: Subbass + Gedackt
    PEDAL = [(0, PED_PLENO),
             (C1a, PED_SOFT), (C1b, PED_PLENO),              # chorale 1
             (C2a, PED_SOFT), (C2b, PED_PLENO),              # chorale 2
             (CLIMAX, PED_PLENO | F513)]                     # +5 1/3' for the close
    TRUMPETS = [(0, REED(TRUMPET))]

    out.tracks.append(track_from(0, CONSOLE_PROGRAM, great, GREAT))
    out.tracks.append(track_from(1, CONSOLE_PROGRAM, positive, POS))
    out.tracks.append(track_from(2, CONSOLE_PROGRAM, pedal, PEDAL))
    out.tracks.append(track_from(3, CONSOLE_PROGRAM, trumpets, TRUMPETS))
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    out.save(DST)
    print("wrote", DST, "| tracks", len(out.tracks), "| len %.1fs" % out.length,
          "| great", len(great), "pos", len(positive), "ped", len(pedal), "trump", len(trumpets))

if __name__ == "__main__":
    main()
