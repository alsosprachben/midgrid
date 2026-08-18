# Worked example — Bach, Fantasia & Fugue in G minor (BWV 542)

Re-registering a MIDI that already carries the *maker's* registration (Martin
Robinson, 1997), and the fullest showcase of the CC-driven system: cross-family
stops (flute + trumpet on 19/20), terraced by section, with a real trap in the
*timing* of the switches. Generator: `examples/register_bwv542.py`.

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

## 3. The registration (all on 19/20)

```text
Piece: Bach, Fantasia & Fugue in G minor, BWV 542
Design: terraced Werkprinzip; the two walking-bass chorales drop to a soft flute;
        a Trompette + 16'/5 1/3' crown the final peroration.

Division   Channel  Body                    Chorales (Great tacet)   Close
---------  -------  ----------------------  -----------------------  ------------------
Great      ch0 p19  Principal 8+4+2+2 2/3   (silent)                 +16'  (CC11 15->31)
Positive   ch1 p19  --                      Flute 8' (bit6, 0b1000000)  --
Pedal      ch2 p19  16'+8'                  bare 8' FLUTE (bit6)     +5 1/3'
Pedal reed ch3 p20  Posaune 16'+8'          OFF                      Posaune
Trumpets   ch4 p20  Trumpet stop (bit3)     --                       (their own passage)
```

### The cross-family stops (the point)
There is no flute or bright chorus-reed among the *principal* stops, so before
this they'd need a separate BlownPipe/brass channel. Now:
- **Positive & chorale pedal = the Flute stop on 19 (bit 6)** — BlownPipe
  spectrum, but flue **dynamic** inharmonicity, so it locks to hybrid.
- **Trumpets = the Trumpet stop on 20 (bit 3)** — BrightBrass spectrum. A
  *harmonic* reed beats against the stretched flue (a slow **phaser**); the
  trumpet stop is flagged **`dynamic`** so it takes the flue stretch and **locks**.

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

`hybrid` tuning; organ **hall** `vol 0.5 … reverb 100 20 100 100 0 -9`,
normalized to −1 dBFS; **Flat factor 0.00**. Ear metric: the chorales enter *and*
exit soft with no swell on the boundary notes; the Trompette blazes without a
phaser; the plenum lands cleanly as the Great re-enters.

## Lesson

Re-registering someone's registration is: keep *what they decided* (the manual
choreography) and change *how it sounds* (your stops). The cross-family stops let
you do it all on 19/20 and stay hybrid-locked. And registration is **timing** as
much as stops — switch in the gaps, and respect held notes (pedal points).
