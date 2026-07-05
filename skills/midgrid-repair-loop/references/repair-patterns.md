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

## Recorded Training Example: fugue-episode-parallel-fifths

From a full three-voice fugue (episode, D minor moving toward the dominant). The evaluator reported `parallel_perfect (beat 58, V0-V1)`: soprano and alto descend together from a perfect fifth into another perfect fifth.

Attempt (V0 soprano, V1 alto; V2 bass omitted, descending G-F-E):

```text
56 | B-4:1@76 | D4:1@74
57 | A4:1@76  | D4:1@74
58 | G4:1@76  | C4:1@74
```

Evaluator diagnosis:

- `parallel_perfect` V0-V1 from beat 57 to 58: A4/D4 is a perfect fifth, G4/C4 is a perfect fifth, both voices descending.

Correction (re-route the alto so the second fifth arrives by oblique motion):

```text
56 | B-4:1@76 | B-3:1@74
57 | A4:1@76  | C4:1@74
58 | G4:1@76  | C4:1@74
```

Lesson:

- When two voices land on consecutive perfect intervals, hold the inner voice's shared tone so the second perfect interval arrives obliquely.
- Rewriting three alto notes preserved both outer lines; prefer re-routing the freest inner voice.

## Recorded Training Example: fugue-offbeat-parallel-fifths

Same fugue, bass subject entry with countersubject in the alto. The parallel hid in an eighth-note offbeat: `parallel_perfect (beat 67, V0-V1) from beat 66.5 to 67`.

Attempt (V0 soprano free line, V1 alto countersubject):

```text
66    | F4:0.5@78 | D4:0.5@76
66.50 | G4:0.5@78 | C4:0.5@76
67    | F4:1@78   | B-3:1@76
```

Evaluator diagnosis:

- G4/C4 at 66.5 and F4/B-3 at 67 are consecutive perfect fifths; the checker compares attack to attack, including half-beat rows.

Correction (hold the soprano through the beat; the fifth at 67 arrives obliquely):

```text
66    | F4:1@78   | D4:0.5@76
66.50 | .         | C4:0.5@76
67    | F4:1@78   | B-3:1@76
```

Lesson:

- Parallels hide in offbeat eighths; check every attack transition, not just downbeats.
- Removing motion is a legal repair: sustaining one voice converts a parallel into oblique motion at zero melodic cost.

## Recorded Training Example: chorale-six-pair-parallels

From a four-voice brass chorale. First draft was checked by hand against outer pairs only; the evaluator found parallel octaves between inner and bass voices (V1-V3, beats 8-10) and parallel fifths between the top pair (V0-V1, beats 17-18).

Attempt (beats 8-10, V1 horn doubling V3 tuba in octaves):

```text
8  | B4:1@82  | D4:1@78  | F#3:1@78 | D3:1@80
9  | C#5:1@82 | F#4:1@78 | A3:1@78  | F#3:1@80
10 | B4:1@80  | G4:1@76  | B3:1@76  | G3:1@78
```

Evaluator diagnosis:

- `parallel_perfect` V1-V3 from 8 to 9 (D4/D3 to F#4/F#3) and from 9 to 10 (to G4/G3): the alto tracked the bass line in octaves for three beats.

Correction (soprano takes the peak, alto moves contrary to the bass):

```text
8  | D5:1@82  | F#4:1@78 | F#3:1@78 | B2:1@80
9  | C#5:1@82 | F#4:1@78 | A3:1@78  | F#2:1@80
10 | B4:1@80  | D4:1@76  | B3:1@76  | G2:1@78
```

Lesson:

- Four voices means six voice pairs; hand-checking soprano-bass is not enough. Run the evaluator before trusting any homophonic texture.
- The strongest repair reshaped the phrase (soprano leap to a peak, alto contrary to the bass) rather than nudging single notes.
