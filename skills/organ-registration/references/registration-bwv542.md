# Worked example — Bach, Fantasia & Fugue in G minor (BWV 542)

Re-registering a MIDI that already carries the *maker's* registration (Martin
Robinson, 1997), and the fullest showcase of the CC-driven system: one
console, flues and reeds and the Bourdon on a single stop word, terraced by
section, with a real trap in the *timing* of the switches. Generator: `examples/register_bwv542.py`.

## 1. Read the source

Robinson gave it a full console: named tracks `Great 8'/4'`, `Positive 8'/4'`,
`Ped 8'`, `Ped 16 Flue`, `Ped 16 Reed`, `Ped 32 Reed`, `Trumpets 8+4`. The
footages are baked in by **octave-transposing** a track (Great 4′ is Great 8′
+12). Balance is by **CC7** per stop, division placement by **CC10 pan**, and
there are 32 tempo events (rubato). This is a *registration*, expressed in GM.

Two things don't survive the GM→physical-model jump: his `Trumpets` use prog 30
(distortion guitar) → our plucked-string voice (they twang), and his flue/reed
CC7 becomes our live swell. So a faithful "as-is" render is close but not right.

## 2. Extract the voices, keep his choreography

His tracks are **stops, not voices** — but *which division plays each passage* is
a real musical decision (Great for the tuttis, Positive for the two chorale
episodes, Trumpets for their passage, Pedal throughout). Keep that. Extract the
**8′-pitch line** of each division (Great ch0, Positive ch6, Pedal ch2, Trumpets
ch8), **discard the octave-doubling tracks** (4′/16′/32′ — we re-create footages
with our own stops), and copy the tempo track verbatim.

## 3. The registration (all on 19, the one console)
```text
Piece: Bach, Fantasia & Fugue in G minor, BWV 542
Design: terraced Werkprinzip; the two walking-bass chorales drop to soft
        flutes over a Bourdon; 16' and the Mixtur crown the final peroration.
Division   Channel  Body                        Chorales (Great tacet)     Close
---------  -------  --------------------------  -------------------------  ---------------------
Great      ch0 p19  Principal 8+4+2+2 2/3       (silent)                   +Principal 16, Mixtur
Positive   ch1 p19  --                          Flute 8'                   --
Pedal      ch2 p19  Principal 16+8, Posaune     Bourdon 16 + Flute 8,      +Quint 5 1/3
                    16+8 (reed 16+8)            reed off
Trumpets   ch3 p19  Trumpet 8'                  --                         (their own passage)
```
### One console, one pedal
The reeds used to be their own program (20), so the pedal was **two channels
playing the same notes** -- flue on 19, Posaune on 20. Once the reeds became
stops of the church organ (bits 8-11), the pedal is one division again: the
notes are played once, and the stop word draws principals and Posaune
together, as a player's pedal does.
### The stops that make it work
- **Positive = the Flute stop (bit 6)**, a stopped-pipe spectrum on the flue's
  pipe, so it locks to hybrid.
- **The chorale pedal = Bourdon 16' + Flute 8'.** It was a bare 8' flute, for
  want of a soft 16'; the stopped Bourdon (bit 12) is the classic Subbass
  under a Gedackt, gravity without weight.
- **Trumpets = the console's Trumpet (bit 11)**, a brass spectrum on the reed
  pipe, flagged `dynamic` so it takes the flue stretch and **locks** -- a
  harmonic reed would beat against the stretched flue as a slow phaser.

## 4. The trap: *when* the registration switches

The two walking-bass chorales (Great tacet, soft) are at beats **57–94.5** and
**166–210.6** (the Great-silence gaps). Getting the *stops* right isn't enough —
the **switch has to land between notes**, or the gate's ~15 ms ramp catches a
note's attack:
- Switch on the *first* chorale note's attack → it "starts loud then goes soft."
- Switch back before the *last* chorale note ends → its tail "goes loud."
So put each switch **inside the Great-silence gap**, and watch for **held notes**:
chorale 1 ends on a long **pedal point** (A2 held to 94.48) while the Great
re-enters at 94.52 — the switch-back must sit in that 94.48–94.52 sliver so the
pedal point finishes soft. (Diagnose with note on/off times, not just onsets.)

## 5. Render & check

tuning's `examples/organ.py`: `hybrid` at A415, the **church** room for both
the early reflections and the tail, −12 dB of headroom for the tail, then
normalized to −1 dBFS. (Earlier renders used a post-render `sox reverb`; the
renderer has its own rooms now.) Ear metric: the chorales enter *and*
exit soft with no swell on the boundary notes; the Trompette blazes without a
phaser; the plenum lands cleanly as the Great re-enters.

## Do not shape its timing

Robinson's file carries **32 tempo events** — his rubato, his sectional tempi, his
written-out closing ritardando. That is an interpretation, and it is the reason
the conductor track is copied verbatim. Do **not** run `baroque-agogics` over this
piece: the transform would replace his phrasing with generated shaping, losing a
performance to gain nothing. Register it, render it, leave the timing alone.

(BWV 543 is the opposite case — compiled from an engraving, so it carries no
interpretation and wants the full agogics treatment. Check a source's tempo map
before shaping it: one tempo event means notation, many means a performance.)

## Lesson

Re-registering someone's registration is: keep *what they decided* (the manual
choreography) and change *how it sounds* (your stops). The cross-family stops let
you do it all on the one console and stay hybrid-locked. And registration is **timing** as
much as stops — switch in the gaps, and respect held notes (pedal points).
