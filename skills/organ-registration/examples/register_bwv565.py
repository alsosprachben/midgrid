#!/usr/bin/env python3
"""Registration of Bach, Toccata and Fugue in D minor, BWV 565.

Source: the Mutopia LilyPond engraving, compiled by mutopia_to_midi.py -- clean
notation, three staves (RH / LH / pedal), one tempo event, no doublings. Being
notation it takes the FULL treatment: registration here, then baroque-agogics.

The most famous organ piece there is, and the registration problem is its ARC.
The opening is a declamation and wants presence immediately -- but if the whole
piece is played on full organ (the popular-culture reading) there is nowhere to
go, and the fugue's counterpoint is buried. So: a bold-but-incomplete plenum for
the toccata, the fugue re-entering LEAN and building (parsimony), and everything
saved for the coda.

Structure (beats at the engraving's 4/4; bar = beat/4 + 1), from a density and
texture analysis of the source:
  bars   1-16   toccata, manuals declaim; pedal enters ~bar 15
  bars  17-29   toccata's big chords, pedal established
  bars  30-126  FUGUE -- long manualiter stretches (bars 30-52, 57-86, 97-109)
  bars 109-111  a genuine PEDAL SOLO (7 beats, manuals silent)
  bars 128-143  coda/recitative -> the peroration

  Great   ch0 p19 flue  <- RH+LH   8+4+2 -> +2 2/3+16 | 8+4 (fugue) -> +2 -> +2 2/3 | FULL+Mixtur
  Pedal   ch1 p19 flue  <- pedal   16+8; brightened for the solo; +5 1/3' in the coda
  Posaune ch2 p20 reed  <- pedal   the toccata's chords, the pedal solo, the coda
  Trompet ch3 p20 reed  <- RH+LH   Great Trompette, coda only
"""
import mido, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reglib import (read_tracks, read_notes, make_channel_track, conductor,
                    read_ornament_log, realize_ornaments, apply_ornaments,
                    F8, F4, F2, F223, F16, F513, MIXTUR, R8, R16, TRUMPET,
                    PLENUM, PEDAL_FOUND)

SRC = os.environ.get("BWV565_SRC",
                     os.path.expanduser("~/Downloads/mutopia-bach-midi/ToccataFugue.mid"))
DST = os.path.expanduser("~/Downloads/bwv565_organ.mid")
# The event-listener log carries the ornament signs, which LilyPond's MIDI drops.
# 565 has 7: the \prall on the opening `a` (the single most recognisable ornament
# in organ music) and its recurrences, plus a cadential \trill in the fugue.
ORN_LOG = os.environ.get("BWV565_NOTES", os.path.expanduser(
    "~/Downloads/mutopia-bach-midi/ToccataFugue.work/ev_ToccataFugue-unnamed-staff.notes"))

# D minor, HARMONIC -- the leading tone is C#, which the opening flourish itself
# spells (a g f e d cis d). The upper neighbour that matters here is A's, which is
# Bb in either form; using the harmonic set keeps ornaments on C#/D correct too.
D_MINOR = {2, 4, 5, 7, 9, 10, 1}

MANUAL_TRACKS = [1, 2]     # RH, LH
PEDAL_TRACK   = 3

# --- section beats -----------------------------------------------------------
T_CHORDS = 64      # bar 17 -- the toccata's weighty chords
FUGUE    = 116     # bar 30 -- subject enters; drop back to a lean chorus.
                   # split_at warns that this seam shortens one note (a G3 pickup
                   # in the cadence, 0.75 -> 0.25 beats). Accepted deliberately:
                   # the nearest clean cuts are 114.5 and 118.0, and either would
                   # push part of the toccata's cadence into the fugue's faster
                   # tempo -- a worse musical error than one clipped passing note.
F_BUILD1 = 228     # bar 57 -- second large manualiter span
F_BUILD2 = 352     # bar 89 -- density rises toward the close of the fugue
PSOLO_IN = 435     # bars 109-111, manuals silent: brighten the pedal (Biggs)
PSOLO_OUT= 441     # ...and retract BEFORE the manuals return at 442
CODA     = 508     # bar 128 -- recitative into the peroration

GREAT = [(0,        F8|F4|F2),                 # bold declamation, not yet complete
         (T_CHORDS, F8|F4|F2|F223|F16),        # the toccata's chords: add gravity
         (FUGUE,    F8|F4),                    # LEAN -- the subject must read
         (F_BUILD1, F8|F4|F2),
         (F_BUILD2, PLENUM),
         (CODA,     PLENUM|F16|MIXTUR)]        # the crown

PEDAL = [(0,         PEDAL_FOUND),
         (PSOLO_IN,  PEDAL_FOUND|F4|F2),       # the solo line must sing out
         (PSOLO_OUT, PEDAL_FOUND),             # retract in the gap, before the manuals
         (CODA,      PEDAL_FOUND|F513)]

POSAUNE = [(0,         0),
           (T_CHORDS,  R8|R16),                # weight under the toccata's chords
           (FUGUE,     0),                     # out of the fugue: keep it transparent
           (PSOLO_IN,  R8|R16),                # the pedal solo blazes
           (PSOLO_OUT, 0),
           (CODA,      R8|R16)]

TROMPETTE = [(0, 0), (CODA, TRUMPET)]          # Great Trompette, peroration only


def main():
    src = mido.MidiFile(SRC); TPB = src.ticks_per_beat
    manual = read_tracks(src, MANUAL_TRACKS)
    pedal  = read_notes(src, PEDAL_TRACK)

    # Ornaments BEFORE registration (the order the skill prescribes: notation ->
    # ornaments -> registration -> agogics). All 7 signs are in the manuals, so
    # they match against `manual` and simply miss the pedal.
    if os.path.exists(ORN_LOG):
        figs = realize_ornaments(read_ornament_log(ORN_LOG, TPB), TPB, D_MINOR)
        manual, _ = apply_ornaments(manual, figs, TPB)
    else:
        print("  !! no ornament log at %s -- rendering WITHOUT ornaments" % ORN_LOG)

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    out.tracks.append(conductor("BWV565 Toccata and Fugue (organ)", src=src))
    out.tracks.append(make_channel_track(0, 19, manual, GREAT,     TPB, unit='beat'))
    out.tracks.append(make_channel_track(1, 19, pedal,  PEDAL,     TPB, unit='beat'))
    out.tracks.append(make_channel_track(2, 20, pedal,  POSAUNE,   TPB, unit='beat'))
    out.tracks.append(make_channel_track(3, 20, manual, TROMPETTE, TPB, unit='beat'))
    out.save(DST)
    print("wrote %s | TPB %d | %.0fs | manual %d, pedal %d"
          % (DST, TPB, out.length, len(manual), len(pedal)))


if __name__ == "__main__":
    main()
