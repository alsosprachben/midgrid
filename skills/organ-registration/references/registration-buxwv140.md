# Worked example — Buxtehude, Prelude & Fugue in D minor (BuxWV 140)

A full re-registration, start to finish, applying this skill's workflow. The
source is a MIDI realization (a MacLean/Kunst-der-Fuge transcription); the goal
is my own expert North-German registration in the `../tuning` renderer.

## 1. Read the music

- **Idiom/date:** North-German *stylus phantasticus*, later 17th c. →
  Werkprinzip organ, Great pleno + independent 16′ Pedal (Geer Pt IV, Northern).
- **Form/sections** (from the MIDI's texture profile, tpb 480, ~665 beats):
  - **Prelude** beats 0–120 — free, toccata-like, 2–3 voices.
  - **Fugue** beats 120–636 — subject entries, building; the working core.
  - **Close** beats 636–end — texture thickens to 6 voices onto a **Picardy
    D-major** final chord.
- **Texture/bass:** four real voices (S A T B). The realization *doubled* them
  across two manuals (a fixed 8′ flue + 8′ reed coupling) — a single flat
  colour for the whole piece, no terracing, and the bass buried in the manual.

## 2–3. Design & divisions

Diagnosis: the flat coupled plenum wastes the form and gives the pedal no
gravity. Re-registration:

- Drop the redundant Manual II doubling; rebuild from the four clean voices.
- **S A T → Great** (principal chorus). **B → Pedal** (its own division:
  16′ + 8′, Posaune 16′ at the pillars) — the single biggest improvement.
- **Terrace:** bold pleno in the Prelude → a clearer 8′+4′ chorus for the Fugue
  so entries read → full pleno + Trompette + Posaune for the closing Picardy.

## 4–5. The registration (Output Pattern)

```text
Piece: Buxtehude, Prelude & Fugue in D minor, BuxWV 140
Design: terraced Werkprinzip — pleno / lighter fugal chorus / grand close;
        independent 16' pedal throughout.

Section (beats)   Division  Stops (footages)            Renderer (prog @ xpose, vel×)
----------------  --------  --------------------------  -----------------------------
Prelude 0-120     Great     Principal 8+4+2 2/3+2       FLUE 19 @0(1.0)/+12(.85)/+19(.62)/+24(.62)
                  Pedal     Principal 16+8 + Posaune16  FLUE 19 @-12(1.0)/0(.90); DARK 58 @-12(.72)
Fugue 120-636     Great     Principal 8+4              FLUE 19 @0(1.0)/+12(.80)
                  Pedal     Principal 16+8            FLUE 19 @-12(.90)/0(.85)
Close 636-end     Great     full pleno + Trompette 8  FLUE 19 @0/+12/+19/+24 + BRIGHT 56 @0(.55)
                  Pedal     16+8 + Posaune 16         FLUE 19 @-12/0 ; DARK 58 @-12(.78)
```

Realized with **one rank per channel** (ch0–7), each program set once; ranks
drawn/retired at the section ticks (57600 / 305280). Low pedal ranks
(16′/Posaune) **gated to source note ≤ G3 (55)** so high bass flourishes in the
toccata don't pick up a subsonic doubling. Generator:
`scratchpad/reregister_140.py` (declarative `SECTIONS` table mirroring the
Output Pattern above).

## 6–7. Render, check, judge

- **Tuning** `hybrid`; **reverb** organ hall `vol 0.5 pad 0 5 reverb 100 20 100
  100 0 -9` (dense pleno → `vol 0.5` for headroom).
- **Clipping check:** `sox …_hall.wav -n stats` → **Flat factor 0.00**. At
  `vol 0.5` the pleno rendered clean but conservative (Pk −6.6 dB, RMS −26);
  peak-normalized to −1 dBFS (`gain -n -1`) → Pk −1.0 dB, RMS −20.4, Flat
  factor still 0.00 — full loudness without clipping. (Loud comes from the
  pyramid + reed, not from a hot `vol`.)
- **Ear metric:** subject reads in the fugue (upperwork dropped there); the
  pedal has real 16′ gravity where before it was buried; colour steps up
  audibly at the Prelude→Fugue and Fugue→Close boundaries; the Picardy close
  gets the Trompette + Posaune it wants.

## Lesson

The original wasn't *wrong* — it was *flat*: one coupled colour, no form, no
pedal. Expert registration is mostly (a) giving the bass its own division with
a 16′, and (b) terracing colour to the sections so the counterpoint's shape and
the piece's rhetoric come through. Everything else (mixtures, the closing reed)
serves those two moves.
