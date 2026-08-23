#!/usr/bin/env python3
"""Considerate registration of Bach, Die Kunst der Fuge, Contrapunctus 1 (BWV
1080/1), for organ.

Contrapunctus 1 is the plainest, most austere fugue of the cycle -- abstract
four-voice counterpoint where legibility of the voices is everything. So the
registration is a restrained PRINCIPAL CHORUS that never draws attention to
itself: pure octaves (no mutations, no reeds), growing only with the music's own
form. The subject enters alone on a single 8'; the exposition's crescendo comes
for free as the four voices accumulate (no stop change); a 4' warms the texture
when the development begins; a 2' lends silver to the final drive to the close.
The bass goes to the Pedal, entering as clear as the manual subjects (8'), taking
its 16' gravity once the exposition is complete.

  Great ch0 p19 flue  <- upper 3 voices  8' -> 8+4 (development) -> 8+4+2 (close)
  Pedal ch1 p19 flue  <- bass voice      8' (entry) -> 16+8 (gravity)

Structure (beats, 2/2 at quarter=100; 78 bars = 312 beats): entries alto(0),
soprano(16), bass(32), tenor(48); exposition peak bar 16 (~56); development from
bar 17 (64); final drive from bar 65 (256); close bars 73-78. No reeds -- save
those for the dramatic Contrapuncti. Render with render_organ.sh; a slightly
drier cathedral keeps the counterpoint clear (REVERB override below).

CC11 flue bits: 0=8' 1=4' 2=2' 3=2 2/3' 4=16' 5=5 1/3'.
"""
import mido, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reglib import read_notes, make_channel_track

SRC = "/home/ben/Downloads/contrapunctus1_piano.mid"
DST = "/home/ben/Downloads/contrapunctus1_organ.mid"
TPB = 480
B = TPB
# Voice tracks by range (median pitch): tr0 bass -> Pedal; tr1/2/3 -> Great.
GREAT_TRACKS = [1, 2, 3]
PEDAL_TRACK  = 0

# per-channel (beat, CC11 mask) -- a considerate build that follows the form.
GREAT = [(0, 0b000001), (64, 0b000011), (256, 0b000111)]   # 8' -> 8+4 -> 8+4+2
PEDAL = [(0, 0b000001), (64, 0b010001)]                    # 8' (entry) -> 16+8

def main():
    src = mido.MidiFile(SRC)
    great = []
    for ti in GREAT_TRACKS: great += read_notes(src, ti)
    pedal = read_notes(src, PEDAL_TRACK)

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    cond = mido.MidiTrack()
    cond.append(mido.MetaMessage('set_tempo', tempo=600000, time=0))   # quarter=100, matches source
    cond.append(mido.MetaMessage('track_name', name='Contrapunctus 1 (organ)', time=0))
    cond.append(mido.MetaMessage('end_of_track', time=0))
    out.tracks.append(cond)
    out.tracks.append(make_channel_track(0, 19, great, GREAT, TPB=B, unit='beat'))
    out.tracks.append(make_channel_track(1, 19, pedal, PEDAL, TPB=B, unit='beat'))
    out.save(DST)
    print("wrote", DST, "| tracks", len(out.tracks), "| len %.1fs" % out.length,
          "| great", len(great), "pedal", len(pedal))

if __name__ == "__main__":
    main()
