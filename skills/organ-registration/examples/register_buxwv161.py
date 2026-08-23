#!/usr/bin/env python3
"""CC-driven registration of Buxtehude's Passacaglia in D minor, BuxWV 161.

A passacaglia is the ideal PARSIMONY piece (Geer / European voicing): start on a
single rank and let the registration grow with the variations, a slow inevitable
crescendo over the ground, cresting only at the d-minor return. So the manual
opens on a lone 8' principal and adds 4' -> 2' -> 2 2/3' across the F- and
a-sections; the pedal ground starts light (8') and gains its 16' gravity early;
and the reeds crown the return in two stages -- the Posaune anticipates, then the
full plenum + 16' + Great Trompette arrive together at the d-return (beat 540).
(NOT a plenum from bar 1 -- that is the treble-heavy habit parsimony rejects.)

  Great   ch0 p19 flue  <- tr2,3,4   8' -> 8+4 -> +2 -> +2 2/3 -> full+16 (return)
  Pedal   ch1 p19 flue  <- tr5        8' -> 16+8 (gravity) -> +5 1/3' (return)
  Posaune ch2 p20 reed  <- tr5        16+8, enters just before the return (stage 1)
  Trompet ch3 p20 reed  <- tr2,3,4    Great Trompette, the d-return arrival (stage 2)

Reeds/Trumpet ride the balanced ReedOrgan voicing + the per-rank spatial layout
now in tonelib; render with examples/render_organ.sh for the cathedral.
CC11 flue bits: 0=8' 1=4' 2=2' 3=2 2/3' 4=16' 5=5 1/3';  reed: 0=8' 1=16' 2=4' 3=Trumpet.
"""
import mido, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reglib import read_notes, make_channel_track

SRC = "/home/ben/Downloads/buxtehude_passacaglia.mid"
DST = "/home/ben/Downloads/buxtehude_passacaglia_registered.mid"
TPB = 1024
B = TPB
GREAT_TRACKS = [2, 3, 4]
PEDAL_TRACK  = 5

MIX = 1 << 7    # Mixtur III (flue bit 7) -- crowns the d-return climax only

# per-channel (beat, stop-mask) build -- a cumulative crescendo, not fixed sections.
GREAT   = [(0, 0b000001), (90, 0b000011), (210, 0b000111),   # 8' -> 8+4 -> 8+4+2
           (450, 0b001111), (540, 0b011111 | MIX)]           # +2 2/3' -> full+16'+Mixtur (return)
PEDAL   = [(0, 0b000001), (90, 0b010001), (540, 0b110001)]   # 8' -> 16+8 -> +5 1/3'
POSAUNE = [(0, 0), (450, 0b000011)]                          # 16+8 reed, anticipates the return
TRUMPET = [(0, 0), (540, 0b001000)]                          # Great Trompette at the arrival

def main():
    src = mido.MidiFile(SRC)
    great = []
    for ti in GREAT_TRACKS: great += read_notes(src, ti)
    pedal = read_notes(src, PEDAL_TRACK)

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    cond = mido.MidiTrack()
    cond.append(mido.MetaMessage('set_tempo', tempo=454545, time=0))   # 132 bpm, matches source
    cond.append(mido.MetaMessage('track_name', name='BuxWV161 registered', time=0))
    cond.append(mido.MetaMessage('end_of_track', time=0))
    out.tracks.append(cond)
    out.tracks.append(make_channel_track(0, 19, great, GREAT, TPB=B, unit='beat'))
    out.tracks.append(make_channel_track(1, 19, pedal, PEDAL, TPB=B, unit='beat'))
    out.tracks.append(make_channel_track(2, 20, pedal, POSAUNE, TPB=B, unit='beat'))
    out.tracks.append(make_channel_track(3, 20, great, TRUMPET, TPB=B, unit='beat'))   # Great Trompette (d-return)
    out.save(DST)
    print("wrote", DST, "| tracks", len(out.tracks), "| len %.1fs" % out.length,
          "| great", len(great), "pedal", len(pedal))

if __name__ == "__main__":
    main()
