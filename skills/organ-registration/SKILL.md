---
name: organ-registration
description: Choose organ registration (stops, footages, divisions, terraced color) for a piece and realize it in the ../tuning physical-model renderer. Grounded in E. Harold Geer's "Organ Registration in Theory and Practice." Use when registering an organ score/MIDI, translating stop-lists into GM programs and octave-transposed ranks, building a Principal chorus / plenum / solo-and-accompaniment, giving the pedal gravity, or terracing color by section (esp. Baroque / North-German praeludia and fugues).
---

# Organ Registration

Registration is the choice of *tone colour* — which pipes speak for each note.
On a real organ you draw stops (ranks of pipes at named pitches); here you
have a monotimbral physical-model synth, so a "stop" is a **voice class + a
pitch transposition**, and a chorus is several such ranks sounding together.
This skill turns Geer's pedagogy into decisions you can execute in `../tuning`.

## Workflow

Design the *sound* first, then draw stops to realize it — never pick stops at
random and listen to what happens.

1. **Read the music.** Idiom & date (Latin vs North-German vs Romantic —
   `references/geer-framework.md` Pt IV), form and its **sections**, texture
   (how many independent voices), and which line is the *bass/pedal*.
2. **Choose the design** (Geer Pt III: colour, mood, sequential design):
   one mood per section, and a *terraced* plan across sections — where the
   plenum is bold, where a solo colour or a lighter chorus should read.
3. **Assign divisions.** Bass/pedal line → **Pedal** (gravity: a 16′ + 8′,
   optionally a reed 16′). Upper voices → a manual (**Great** for plenum,
   **Positiv** for lighter/solo). Keep divisions independent — that is what
   makes counterpoint legible.
4. **Draw the chorus** (`references/stop-families-and-footage.md`): build up
   by pitch — 8′ foundation, add 4′, then 2′ and a quint/mixture for a full
   *Organo Pleno*; keep upper ranks softer than the 8′ so blend stays pyramidal.
5. **Realize it** (`references/renderer-palette.md`): put one organ channel per
   division (flue prog 19, reed prog 20) and **draw the stops with a CC11
   bitfield** per section (the engine stacks the ranks itself and they lock to
   `hybrid`); add **CC7** for a live swell and **CC4** for a crescendo pedal.
   velocity sets static level.
6. **Render and check** (`$tuning-render` conventions): `hybrid` tuning for
   Baroque, organ **hall** reverb, and **verify `sox FILE -n stats` → Flat
   factor 0.00** (dense plena clip — drop `vol` or thin the upperwork).
7. **Judge by ear against the metric.** Does the subject read? Does the pedal
   have gravity? Does each section's colour change where intended?

## Rule Priority

Prioritize in this order (Geer's Pt II precedes his Pt III — you cannot colour
what cannot be heard or does not blend):

1. **Audibility** — every intended line is present and not masked.
2. **Blend / pyramid** — 8′ foundation loudest, upperwork progressively
   softer; no rank sticks out of the chorus unless it is a *solo*.
3. **Pedal gravity & independence** — the bass has a 16′ and reads as its own
   division, not a doubling of the manual.
4. **Terraced design** — colour and weight change *by section*, deliberately;
   Baroque registration is set per section, not continuously crescendoed.
5. **Colour & mood** — the family (principal / flute / string / reed) fits the
   affect and the idiom.
6. **Historical idiom** — North-German Werkprinzip plenum, French *grand jeu*,
   etc., when the piece asks for it.
7. **Headroom** — the realized stack must not clip (Flat factor 0.00).

## Output Pattern

State the registration as a table before realizing it — section → division →
drawn stops → footages → renderer realization:

```text
Piece: <name / key / form>
Design: <one line — the terraced plan>

Section        Division  Stops (footages)          Channel  CC11 mask
-------------  --------  ------------------------  -------  ---------
Prelude        Great     Principal 8+4+2+2 2/3     ch0 p19  0b1111  (15)
               Pedal     Principal 16+8            ch1 p19  0b10001 (17)
Fugue (expo)   Great     Principal 8+4             ch0 p19  0b11    (3)
               Pedal     Principal 16+8            ch1 p19  0b10001 (17)
Close          Great     full pleno + 16'          ch0 p19  0b11111 (31)
               Pedal     16+8 + reed Posaune       ch1/ch2  ...
```

Then realize with one channel per division and a CC11 event at each section tick
(program-change first, then CC11). If the user wants only the plan, output only
the table.

## References

- `references/geer-framework.md` — Geer's five-part pedagogy (the conceptual
  backbone: acoustics → blend → design → history → practice).
- `references/stop-families-and-footage.md` — flue vs reed families, the
  footage/pitch system, building choruses, divisions, couplers, terracing.
- `references/renderer-palette.md` — the executable bridge: stop family → GM
  program / voice class + octave-transposition recipe for footages & mixtures,
  with worked recipes and the density/clipping caveat.
- `references/registration-buxwv140.md` — a full worked example (Buxtehude
  Prelude & Fugue in D minor): flat coupled original → terraced re-registration.
- `references/registration-bwv542.md` — re-registering a MIDI that already
  carries the *maker's* registration (Bach, Fantasia & Fugue in G minor): the
  fullest showcase — cross-family flute + trumpet stops on 19/20, soft
  walking-bass chorales, and the *timing* of the switches (land them in the gaps).
- `references/registration-bwv543.md` — worked example (Bach, A minor P&F):
  getting a **notated** source (IMSLP LilyPond → MIDI), realizing its ornaments
  with our C.P.E. Bach engine, and the **pedal-solo registration** (brighten the
  exposed pedal, retract before the manuals return).
- `examples/` — the generator scripts for the worked examples
  (`register_bwv542.py`, `register_bwv543.py`, `register_buxwv140.py`,
  `register_buxwv161.py`): one organ channel per division, stop masks per
  section. Plus `render_organ.sh IN.mid [tuner]` — the full pipeline in one
  command (block-render with headroom → cathedral reverb → normalise → mp3).

**Related skill:** `baroque-agogics` shapes the *time* (tempo, articulation,
agogic breath, cadential rubato) — the expression a fixed-volume instrument makes
instead of dynamics. Apply it **after** registration; it warps the CC events along
with the notes. Order: notation → ornaments → registration → agogics → render.
