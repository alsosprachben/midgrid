#!/usr/bin/env python3
"""Registration of Bach, Passacaglia and Thema fugatum in C minor, BWV 582.

Source: the Mutopia LilyPond engraving via mutopia_to_midi.py. Its MIDI score
also carries partial recorder doublings for consort playability (tracks 2 and 4);
they overlap the organ staves only in places, so the automatic +-octave de-doubler
correctly leaves them alone and we simply do not select them here. The organ
texture is tracks 1 (right:), 3 (left:), 5 (pedal -- the ground bass).

This engraving notates the whole work, fugue included, in 3/4: the Thema fugatum
enters at bar 170 as `g2 es4`, three beats. (Editions differ; this one is
internally consistent, so the agogic grid follows it.)

The registration is the piece's own logic: a passacaglia is a cumulative form, so
this is the parsimony case in its purest shape.

  bars   1-8    the ground ALONE in the pedal -- 16+8, grave, nothing else
  bars   9-103  variations accumulate: the manuals enter on a single 8' and grow
  bars 104-128  MANUALITER variations (the pedal falls silent) -- lighten
  bars 129-169  pedal returns; the passacaglia drives to its close
  bars 170+     Thema fugatum: re-lean, then build to the Neapolitan peroration

  Great   ch0 p19 flue  <- right:+left:   8' -> 8+4 -> +2 -> plenum | lean | FULL+Mixtur
  Pedal   ch1 p19 flue  <- pedal          16+8 throughout; +5 1/3' at the close
  Posaune ch2 p20 reed  <- pedal          from the fugue's build
  Trompet ch3 p20 reed  <- manuals        the peroration only
"""
import mido, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reglib import (read_tracks, read_notes, make_channel_track, conductor,
                    read_ornament_log, realize_ornaments, apply_ornaments,
                    read_fermatas, read_slurs,
                    F8, F4, F2, F223, F16, F513, MIXTUR, R8, R16, TRUMPET,
                    PLENUM, PEDAL_FOUND)

SRC = os.environ.get("BWV582_SRC",
                     os.path.expanduser("~/Downloads/mutopia-bach-midi/bwv582.mid"))
DST = os.path.expanduser("~/Downloads/bwv582_organ.mid")
# LilyPond's MIDI backend expands no ornament sign, so the 19 in this engraving
# (16 \prall, 3 \mordent -- including the long trill over the fugue's close)
# reach us only through the event-listener log.
ORN_LOG = os.environ.get("BWV582_NOTES", os.path.expanduser(
    "~/Downloads/mutopia-bach-midi/bwv582.work"))

C_MINOR = {0, 2, 3, 5, 7, 8, 11}      # harmonic: B natural is the leading tone

MANUAL_TRACKS = [1, 3]     # right: and left: -- NOT 2/4, which are consort doublings
PEDAL_TRACK   = 5

# --- section beats (3/4, so bar = beat/3 + 1) --------------------------------
MAN_IN   = 24     # bar   9 -- the manuals join the ground
V_GROW1  = 96     # bar  33
V_GROW2  = 192    # bar  65
V_FULL   = 288    # bar  97 -- plenum before the manualiter group
MANUALIT = 311    # bar 105 -- pedal tacet: lighten and let the counterpoint speak
PED_BACK = 384    # bar 129 -- the pedal returns
FUGUE    = 505    # "Thema fugatum" -- the subject's g2 enters HERE, as a
                  # two-beat anacrusis into bar 170. The source's %% Takt 170
                  # comment sits AFTER it; taking the barline (507) instead cut
                  # the subject's opening G off into the previous movement.
F_BUILD  = 600    # bar 201
F_WEIGHT = 700    # bar 234 -- 16' and the Posaune
CODA     = 820    # bar 274 -- the Neapolitan close

GREAT = [(0,        0),                  # the ground speaks alone
         (MAN_IN,   F8),                 # one rank
         (V_GROW1,  F8|F4),
         (V_GROW2,  F8|F4|F2),
         (V_FULL,   PLENUM),
         (MANUALIT, F8|F4),              # pedal out: keep it transparent
         (PED_BACK, PLENUM),
         (FUGUE,    F8|F4),              # the subject must read
         (F_BUILD,  F8|F4|F2),
         (F_WEIGHT, PLENUM|F16),
         (CODA,     PLENUM|F16|MIXTUR)]

PEDAL = [(0,        PEDAL_FOUND),        # 16+8: the theme grave and clear
         (CODA,     PEDAL_FOUND|F513)]

POSAUNE = [(0, 0), (F_WEIGHT, R8|R16)]   # reed weight only for the last third
TROMPETTE = [(0, 0), (CODA, TRUMPET)]


def main():
    src = mido.MidiFile(SRC); TPB = src.ticks_per_beat
    manual = read_tracks(src, MANUAL_TRACKS)
    pedal  = read_notes(src, PEDAL_TRACK)

    # Ornaments before registration. They are manual signs, so they match against
    # `manual` and miss the pedal -- which is what we want.
    if os.path.exists(ORN_LOG):
        figs = realize_ornaments(read_ornament_log(ORN_LOG, TPB), TPB, C_MINOR)
        manual, _ = apply_ornaments(manual, figs, TPB)
    else:
        print("  !! no ornament log at %s -- rendering WITHOUT ornaments" % ORN_LOG)

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    ferm = read_fermatas(ORN_LOG, TPB)
    print("  fermatas: %d, at bars %s" % (len(ferm), [round(t/(3.0*TPB)+1, 1) for t, _ in ferm]))
    slur = read_slurs(ORN_LOG, TPB)
    print("  slurs: %d notes marked legato" % len(slur))

    out.tracks.append(conductor("BWV582 Passacaglia (organ)", src=src, fermatas=ferm, slurs=slur))
    out.tracks.append(make_channel_track(0, 19, manual, GREAT,     TPB, unit='beat'))
    out.tracks.append(make_channel_track(1, 19, pedal,  PEDAL,     TPB, unit='beat'))
    out.tracks.append(make_channel_track(2, 20, pedal,  POSAUNE,   TPB, unit='beat'))
    out.tracks.append(make_channel_track(3, 20, manual, TROMPETTE, TPB, unit='beat'))
    out.save(DST)
    print("wrote %s | TPB %d | %.0fs | manual %d, pedal %d"
          % (DST, TPB, out.length, len(manual), len(pedal)))


if __name__ == "__main__":
    main()
