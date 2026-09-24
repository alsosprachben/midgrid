#!/usr/bin/env python3
"""Re-register BuxWV 140 the CC-driven way (replaces the 8-channel octave hack).

One organ channel per division; the renderer stacks the ranks itself from a
CC11 stop bitfield, terraced per section. Drops the redundant Manual II doubling
and strips the source's old CC7/CC11 automation (repurposed now).

PARSIMONY OF PIPES (Geer / European style): start each section on ONE rank of an
appropriate property and *expand*, rather than opening on a full chorus. The
prelude opens on a single 8' principal; the **fugue enters on a solo 8' reed**
(the subject reads on the reed alone) and only later draws the flue chorus; the
close is the one place everything is pulled.

  Great  ch0  prog 19 (flue)  <- S,A,T   8' -> 8+4+2 (prelude) | tacet in the fugue
                                          until the build (8+4) | full+16 (close)
  P.Reed(Gt) ch3 prog 20 (reed) <- S,A,T  8' reed carries the fugue subject; +Trumpet close
  Pedal  ch1  prog 19 (flue)  <- B        8' -> 16+8; light (8') under the solo reed; +5 1/3' close
  Posaune ch2 prog 20 (reed)  <- B        16+8, reserved for the close peroration only

CC11 bitfield bits: flue 0=8' 1=4' 2=2' 3=2 2/3' 4=16' 5=5 1/3' 6=Flute;
                    reed 0=8' 1=16' 2=4' 3=Trumpet.
"""
import mido, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reglib import read_notes, make_channel_track, console_reed, CONSOLE_PROGRAM

SRC = "/home/ben/Downloads/buxtehude_buxwv140_flat.mid"
DST = "/home/ben/Downloads/buxtehude_buxwv140_registered_cc.mid"
TPB = 480
B = TPB
P_TUTTI = 24  * B    # prelude opens on 8' alone, broadens after the opening flourish
FUGUE   = 120 * B    # fugue enters on a solo 8' reed (Great flue tacet)
F_BUILD = 360 * B    # ~halfway: the flue principal chorus joins the reed
CLOSE   = 636 * B    # peroration: everything

GREAT_VOICES = [1, 2, 3]   # S, A, T
PEDAL_VOICE  = 4           # bass -> pedal

MIX = 1 << 7    # Mixtur III (flue bit 7) -- the crown of a full pleno, close only

# per-channel (tick, stop-mask) events -- a *build*, not a plenum from bar 1.
GREAT = [(0, 0b000011), (P_TUTTI, 0b000111), (FUGUE, 0),          # 8+4 -> 8+4+2 ; tacet in fugue
         (F_BUILD, 0b000011), (CLOSE, 0b011111 | MIX)]            # flue rejoins 8+4 ; +16'+Mixtur close
GREAT_REED = [(0, 0), (FUGUE, 0b000001), (CLOSE, 0b001001)]       # solo 8' reed fugue ; +Trumpet close
PEDAL = [(0, 0b000001), (P_TUTTI, 0b010001), (FUGUE, 0b000001),   # 8' -> 16+8 ; light 8' under the reed
         (F_BUILD, 0b010001), (CLOSE, 0b110001)]                  # 16+8 ; +5 1/3' close
POSAUNE = [(0, 0), (CLOSE, 0b000011)]                             # pedal reed only crowns the close

def main():
    src = mido.MidiFile(SRC)
    great = []
    for ti in GREAT_VOICES: great += read_notes(src, ti)
    pedal = read_notes(src, PEDAL_VOICE)

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    cond = mido.MidiTrack()
    cond.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
    cond.append(mido.MetaMessage('track_name', name='BuxWV140 CC-registered', time=0))
    cond.append(mido.MetaMessage('end_of_track', time=0))
    out.tracks.append(cond)
    out.tracks.append(make_channel_track(0, 19, great, GREAT))
    out.tracks.append(make_channel_track(1, 19, pedal, PEDAL))
    out.tracks.append(make_channel_track(2, CONSOLE_PROGRAM, pedal, console_reed(POSAUNE)))
    out.tracks.append(make_channel_track(3, CONSOLE_PROGRAM, great, console_reed(GREAT_REED)))   # Great reed: fugue subject + close Trompette
    out.save(DST)
    print("wrote", DST, "| type", out.type, "| tracks", len(out.tracks),
          "| len %.1fs" % out.length, "| great", len(great), "pedal", len(pedal))

if __name__ == "__main__":
    main()
