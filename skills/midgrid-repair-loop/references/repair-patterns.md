# MidGrid Repair Patterns

Use these transformations in generate-analyze-revise loops. When available, start from `midgrid_eval.py --json` diagnostics with `code`, `beat`, `voice_pair`, and `message` fields.

## Syntax Repairs

Bad:

```text
4 | (free canon)B4@84 | D3@70
```

Good:

```text
4 | B4@84 | D3@70 // free canon entry
```

Bad:

```text
4 | Bb4@84 | D3@70
```

Good:

```text
4 | A#4@84 | D3@70
```

Bad:

```text
4 | C4@80:1 | E3@70
```

Good:

```text
4 | C4:1@80 | E3@70
```

## Parallel Perfect Repair

Before:

```text
0 | G4:1@80 | C3:1@70
1 | A4:1@80 | D3:1@70
```

Diagnosis:

- Similar stepwise motion preserves a compound perfect fifth.

After:

```text
0 | G4:1@80 | C3:1@70
1 | F4:1@80 | D3:1@70
```

Repair:

- Change only the upper voice at beat 1.
- Convert similar motion into contrary motion.

## Dissonance Resolution Repair

Before:

```text
0 | C5:1@80 | D4:1@70
1 | E5:1@80 | E4:1@70
```

Diagnosis:

- Beat 0 is a dissonant seventh-like sonority without preparation/resolution.

After:

```text
0 | B4:1@80 | D4:1@70
1 | C5:1@80 | E4:1@70
```

Repair:

- Replace the exposed dissonance with consonance.
- Keep the phrase direction by step.

## Report-Driven Effect Repair

If complexity is high where repose is requested:

- Prefer consonant thirds/sixths for inner phrase stability.
- Use perfect fifth/octave mainly for cadential arrival.
- Reduce active voices or widen cluttered close intervals if many pair scores spike at once.

If the passage sounds inert:

- Add controlled contrary motion.
- Let complexity rise before a cadence, then fall at the arrival.


## Recorded Training Example: parallel-perfect-repair-001

This example was recorded by `midgrid_exercise.py record` and is suitable as a compact before/after repair pattern.

Attempt:

```text
# Title: Parallel Perfect Repair 001 Attempt
# tempo 80

0 | G4:1@80 | C3:1@70
1 | A4:1@80 | D3:1@70
2 | B4:1@80 | E3:1@70
3 | C5:1@80 | F3:1@70
```

Evaluator diagnosis:

- `parallel_perfect` appears because the upper and lower voices move by similar stepwise motion through repeated compound perfect fifths.
- `exercise_checks.locked_voices=[1]` means the lower voice must remain unchanged.

Correction:

```text
# Title: Parallel Perfect Repair 001 Corrected
# tempo 80

0 | G4:1@80 | C3:1@70
1 | F4:1@80 | D3:1@70
2 | G4:1@80 | E3:1@70
3 | A4:1@80 | F3:1@70
```

Lesson:

- Change the movable upper voice, not the locked cantus.
- A one-beat contrary-motion repair can break the parallel-perfect chain while preserving the lower line.
- Re-evaluate after the repair; this correction has zero evaluator errors and zero exercise-specific issues.
