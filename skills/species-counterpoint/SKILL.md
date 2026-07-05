---
name: species-counterpoint
description: Teach, compose, or repair Fux-style species counterpoint using MidGrid examples, exercises, diagnostics, and corrections. Use when working on first through fifth species, cantus-firmus exercises, consonance and dissonance treatment, melodic discipline, cadence formation, or example-oriented LLM counterpoint training.
---

# Species Counterpoint

## Workflow

Teach by examples first, then rules. Use MidGrid to show the vertical interval at each beat and the horizontal motion of each voice.

1. Select the species. Default to first species if the user does not specify one.
2. Start from examples: run or request `python3 midgrid_examples.py --target-exercise-id EXERCISE_ID --format markdown` when working from the local curriculum; this includes nearby examples and excludes the target solution by default. Otherwise read `references/species-curriculum.md` for the stage, objective, and evaluation focus.
3. Read the species-matched reference: `references/first-species-examples.md`, `second-species-examples.md`, `third-species-examples.md`, `fourth-species-examples.md`, or `fifth-species-examples.md`; for more than two voices, `three-voice-species.md`.
4. Use `$midgrid-strict-output` conventions: no prose inside cells, fixed voice columns, parser-safe notes.
5. Compose or repair locally by beat: identify the bad interval, motion, leap, or cadence; change as few notes as possible.
6. Prefer worked triples: positive example, negative example, corrected version.
7. When `midgrid_exercise.py evaluate` or parser/report output is available, use it to confirm intervals, motion, and perceptual shape.

## Rule Priority

Prioritize in this order:

1. Parser-valid MidGrid.
2. Correct species rhythm.
3. Legal vertical intervals for the species.
4. No forbidden parallel perfect fifths or octaves.
5. Independent melodic lines with singable ranges.
6. Cadence and tonal clarity.
7. Aesthetic contour from the harmonic report.

## Output Pattern

For exercises, use this compact form:

```text
Objective: first species above a cantus in C.
Attempt:
[MidGrid]
Diagnosis:
[beat-level issues]
Correction:
[MidGrid]
```

If the user requests only notation, output only the corrected MidGrid.
