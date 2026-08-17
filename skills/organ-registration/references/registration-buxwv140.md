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

Section (beats)   Division  Stops (footages)          Channel  CC11 mask
----------------  --------  ------------------------  -------  -----------------
Prelude 0-120     Great     Principal 8+4+2+2 2/3     ch0 p19  0b001111 (15)
                  Pedal     Principal 16+8            ch1 p19  0b010001 (17)
                  Pedal rd  reed Posaune 16+8         ch2 p20  0b000011 (3)
Fugue 120-636     Great     Principal 8+4            ch0 p19  0b000011 (3)
                  Pedal     Principal 16+8          ch1 p19  0b010001 (17)
                  Pedal rd  (reed rests)            ch2 p20  0b000000 (0)
Close 636-end     Great     full pleno + 16'        ch0 p19  0b011111 (31)
                  Pedal     Principal 16+8          ch1 p19  0b010001 (17)
                  Pedal rd  reed Posaune 16+8       ch2 p20  0b000011 (3)
```

Realized natively with the organ registration engine: **one channel per
division**, and a **CC11 stop-bitfield** event at each section tick (57600 /
305280). The renderer stacks the ranks internally on the note's stretched grid
(so they lock to `hybrid`) — no octave-duplicated note tracks, no per-rank
channels. The pedal reed simply mutes its stops (mask 0) through the fugue and
draws again for the close. Generator: `scratchpad/reregister_140_cc.py`
(declarative per-section masks). Contrast the earlier hand-authored version
(`reregister_140.py`), which emulated the same registration by duplicating
transposed note events across eight channels — the engine now does that job.

## 6–7. Render, check, judge

- **Tuning** `hybrid`; **reverb** organ hall `vol 0.5 pad 0 5 reverb 100 20 100
  100 0 -9` (dense pleno → `vol 0.5` for headroom), then peak-normalized to
  −1 dBFS (`gain -n -1`).
- **Clipping check:** `sox …_hall.wav -n stats` → **Flat factor 0.00**
  (see the render log). Loudness comes from the drawn pyramid, not a hot `vol`.
- **Ear metric:** the subject reads in the fugue (upperwork dropped to 8′+4′);
  the pedal has real 16′ gravity where before it was buried; colour steps up
  audibly at the Prelude→Fugue and Fugue→Close boundaries; the reed Posaune
  enters for the two tutti pillars and rests through the fugal core.

## Lesson

The original wasn't *wrong* — it was *flat*: one coupled colour, no form, no
pedal. Expert registration is mostly (a) giving the bass its own division with
a 16′, and (b) terracing colour to the sections so the counterpoint's shape and
the piece's rhetoric come through. Everything else (mixtures, the closing reed)
serves those two moves.
