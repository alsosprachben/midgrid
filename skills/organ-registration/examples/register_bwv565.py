#!/usr/bin/env python3
"""Registration of Bach, Toccata and Fugue in D minor, BWV 565 -- TWO MANUALS.

Source: the Mutopia LilyPond engraving, compiled by mutopia_to_midi.py. Being
notation it takes the FULL treatment: ornaments and fermatas recovered from the
event-listener log, registration here, then baroque-agogics.

WHY TWO MANUALS, AND HOW THE DIVISION WAS DECIDED. The engraving separates the
hands properly -- `\\context Staff = "RH"` and `= "LH"` -- and the earlier version
of this file merged both onto one Great channel, discarding that. What it does
NOT contain is any manual indication: no Oberwerk, no Rueckpositiv, no
registration marks of any kind, and its own header names its source as the
Bach-Gesellschaft Ausgabe of 1867. BWV 565 has no autograph at all (the earliest
source is Ringk's copy), so manual changes in it are editorial by nature.

Stem direction does not supply them either, though it was worth checking: all
3433 manual stems in this engraving are explicit, and in the RH staff the
stem-DOWN notes have a HIGHER median pitch than the stem-up ones (73 vs 69),
which is the ordinary rule of pointing stems away from the middle staff line --
layout, not voicing.

So the two-manual plan is derived from the notes themselves, and only where they
actually ask for it:

  * The ECHO at bars 14-15. The RH figure of bar 14 returns in bar 15 transposed
    exactly -12 semitones, over an LH figure that repeats note for note. That is
    a written echo, and the one place in the piece where the notation itself asks
    for a manual change. Both hands drop to a bare 8' for bar 15 and return.
  * The 28-bar MANUALITER span, bars 58-85, where the pedal is silent and the
    hands genuinely alternate (RH alone bars 60-69, LH alone bars 74-77). The
    manuals UNCOUPLE here: the Rueckpositiv takes its own flute colour so the two
    lines are told apart by timbre as well as register. This is where two manuals
    earn their keep -- Geer's point that independent divisions are what make
    counterpoint legible.
  * Everywhere else the manuals carry the SAME registration, which is what
    coupling is. Two manuals is not the same as two colours all evening; the
    toccata's chords and the peroration want one weight, not a dialogue.

  Oberwerk    ch0 p19 flue  <- RH     8+4+2 -> chords -> lean (fugue) -> plenum
  Rueckpositiv ch1 p19 flue <- LH     coupled, except the echo and the manualiter
  Pedal       ch2 p19 flue  <- pedal  16+8; brightened for the pedal solo
  Posaune     ch3 p20 reed  <- pedal  toccata chords, pedal solo, coda
  Trompette   ch4 p20 reed  <- RH+LH  Great Trompette, peroration only
"""
import mido, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reglib import (read_notes, make_channel_track, conductor,
                    read_ornament_log, realize_ornaments, apply_ornaments,
                    read_fermatas,
                    F8, F4, F2, F223, F16, F513, FLUTE, MIXTUR, R8, R16, TRUMPET,
                    PLENUM, PEDAL_FOUND)

SRC = os.environ.get("BWV565_SRC",
                     os.path.expanduser("~/Downloads/mutopia-bach-midi/ToccataFugue.mid"))
DST = os.path.expanduser("~/Downloads/bwv565_organ.mid")
# Ornaments AND fermatas live only here -- MIDI carries neither.
ORN_LOG = os.environ.get("BWV565_NOTES", os.path.expanduser(
    "~/Downloads/mutopia-bach-midi/ToccataFugue.work"))

RH_TRACK, LH_TRACK, PEDAL_TRACK = 1, 2, 3

# D minor, HARMONIC -- the leading tone is C#, which the opening flourish spells
# out itself (a g f e d cis d).
D_MINOR = {2, 4, 5, 7, 9, 10, 1}

# --- section beats (4/4, so bar = beat/4 + 1) --------------------------------
ECHO_IN   = 56     # bar 15: the RH repeats bar 14 an octave lower -- the echo
ECHO_OUT  = 60     # bar 16: back to the main manual
T_CHORDS  = 64     # bar 17: the toccata's weighty chords
FUGUE     = 116    # bar 30: subject enters; drop back to a lean chorus.
                   # split_at warns that this seam shortens one note (a G3 pickup
                   # in the cadence, 0.75 -> 0.25 beats). Accepted deliberately:
                   # the nearest clean cuts are 114.5 and 118.0, and either would
                   # push part of the toccata's cadence into the fugue's faster
                   # tempo -- a worse musical error than one clipped passing note.
DIALOG_IN = 228    # bar 58: pedal silent for 28 bars, hands alternate -> UNCOUPLE
DIALOG_OUT= 340    # bar 86: pedal returns -> couple again
F_BUILD   = 352    # bar 89: density rises toward the close of the fugue
PSOLO_IN  = 435    # bars 109-111, manuals silent: brighten the pedal (Biggs)
PSOLO_OUT = 441    # ...and retract BEFORE the manuals return at 442
CODA      = 508    # bar 128: recitative into the peroration

LEAN = F8 | F4                                  # the fugue subject must read
OBERWERK = [(0,         F8|F4|F2),              # bold declamation, not yet complete
            (ECHO_IN,   F8),                    # the echo: a bare 8'
            (ECHO_OUT,  F8|F4|F2),
            (T_CHORDS,  F8|F4|F2|F223|F16),     # the chords: add gravity
            (FUGUE,     LEAN),
            (F_BUILD,   PLENUM),
            (CODA,      PLENUM|F16|MIXTUR)]     # the crown

RUCKPOSITIV = [(0,         F8|F4|F2),           # coupled with the Oberwerk
               (ECHO_IN,   F8),                 # ...and echoes with it
               (ECHO_OUT,  F8|F4|F2),
               (T_CHORDS,  F8|F4|F2|F223|F16),
               (FUGUE,     LEAN),
               (DIALOG_IN, F8|FLUTE),           # UNCOUPLED: its own flute colour
               (DIALOG_OUT,LEAN),               # coupled again when the pedal returns
               (F_BUILD,   PLENUM),
               (CODA,      PLENUM|F16|MIXTUR)]

PEDAL = [(0,         PEDAL_FOUND),
         (PSOLO_IN,  PEDAL_FOUND|F4|F2),        # the solo line must sing out
         (PSOLO_OUT, PEDAL_FOUND),              # retract in the gap, before the manuals
         (CODA,      PEDAL_FOUND|F513)]

POSAUNE = [(0,         0),
           (T_CHORDS,  R8|R16),                 # weight under the toccata's chords
           (FUGUE,     0),                      # out of the fugue: keep it transparent
           (PSOLO_IN,  R8|R16),                 # the pedal solo blazes
           (PSOLO_OUT, 0),
           (CODA,      R8|R16)]

TROMPETTE = [(0, 0), (CODA, TRUMPET)]           # Great Trompette, peroration only


def main():
    src = mido.MidiFile(SRC); TPB = src.ticks_per_beat
    rh    = read_notes(src, RH_TRACK)
    lh    = read_notes(src, LH_TRACK)
    pedal = read_notes(src, PEDAL_TRACK)

    # Ornaments BEFORE registration (notation -> ornaments -> registration ->
    # agogics). Each hand is matched separately, so a sign lands on the division
    # that actually plays it.
    figs = realize_ornaments(read_ornament_log(ORN_LOG, TPB), TPB, D_MINOR)
    rh, n_rh = apply_ornaments(rh, figs, TPB, verbose=False)
    lh, n_lh = apply_ornaments(lh, figs, TPB, verbose=False)
    print("  ornaments: %d on the RH, %d on the LH (of %d)" % (n_rh, n_lh, len(figs)))

    ferm = read_fermatas(ORN_LOG, TPB)
    print("  fermatas: %d, at bars %s" % (len(ferm), [round(t/(4.0*TPB)+1, 1) for t, _ in ferm]))

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    out.tracks.append(conductor("BWV565 Toccata and Fugue (organ, 2 man.)",
                                src=src, fermatas=ferm))
    out.tracks.append(make_channel_track(0, 19, rh,    OBERWERK,    TPB, unit='beat'))
    out.tracks.append(make_channel_track(1, 19, lh,    RUCKPOSITIV, TPB, unit='beat'))
    out.tracks.append(make_channel_track(2, 19, pedal, PEDAL,       TPB, unit='beat'))
    out.tracks.append(make_channel_track(3, 20, pedal, POSAUNE,     TPB, unit='beat'))
    out.tracks.append(make_channel_track(4, 20, rh + lh, TROMPETTE, TPB, unit='beat'))
    out.save(DST)
    print("wrote %s | TPB %d | %.0fs | RH %d, LH %d, pedal %d"
          % (DST, TPB, out.length, len(rh), len(lh), len(pedal)))


if __name__ == "__main__":
    main()
