# Second Species Examples

These examples use two voices: `V0` is counterpoint above, `V1` is cantus below. Integer beats are strong positions; half-beats are weak positions.

## Positive Example

```text
# Title: Second Species Positive Example
# tempo 80

0 | E4:0.5@80 | C3:0.5@70
0.5 | F4:0.5@80 | -
1 | F4:0.5@80 | D3:0.5@70
1.5 | G4:0.5@80 | -
2 | G4:0.5@80 | E3:0.5@70
2.5 | A4:0.5@80 | -
3 | A4:0.5@80 | F3:0.5@70
3.5 | G4:0.5@80 | -
4 | B4:0.5@80 | G3:0.5@70
4.5 | C5:0.5@80 | -
5 | C5:0.5@80 | A3:0.5@70
5.5 | B4:0.5@80 | -
6 | D5:0.5@80 | G3:0.5@70
6.5 | E5:0.5@80 | -
7 | C5:1@80 | C3:1@70
```

Why it works:

- The held cantus is visible as note-plus-hold pairs in V1.
- Every integer-beat downbeat is consonant against the cantus.
- Weak half-beats include passing tension, but the upper line remains stepwise or locally controlled.
- The final uses a single cadence note instead of adding a weak note after closure.

## Negative Example: Strong-Beat Dissonance

```text
# Title: Second Species Negative Example
# tempo 80

0 | D4:0.5@80 | C3:0.5@70
0.5 | E4:0.5@80 | -
1 | E4:0.5@80 | D3:0.5@70
1.5 | F4:0.5@80 | -
```

Problem:

- Beat 0 places D over C on a strong position, producing interval class 2.
- In second species, dissonance belongs on weak positions and should be approached and left by step.

## Corrected Version

```text
# Title: Second Species Corrected Example
# tempo 80

0 | E4:0.5@80 | C3:0.5@70
0.5 | F4:0.5@80 | -
1 | F4:0.5@80 | D3:0.5@70
1.5 | G4:0.5@80 | -
```

Repair:

- Move the strong-beat upper notes to consonant thirds or tenths.
- Keep the weak half-beat as linear motion rather than a structural interval.

## Exercise Prompt

Complete V0 while preserving the held cantus in V1:

```text
# Title: Second Species Above Exercise 001
# tempo 80

0 | . | C3:0.5@70
0.5 | . | -
1 | . | D3:0.5@70
1.5 | . | -
2 | . | E3:0.5@70
2.5 | . | -
3 | . | F3:0.5@70
3.5 | . | -
4 | . | G3:0.5@70
4.5 | . | -
5 | . | A3:0.5@70
5.5 | . | -
6 | . | G3:0.5@70
6.5 | . | -
7 | . | C3:1@70
```

## Procedure: Solving A Second-Species Exercise

1. Preserve the cantus voice and all `-` hold cells exactly.
2. Fill the counterpoint voice on every row.
3. Treat integer beats as strong positions.
4. On strong positions, use consonant interval classes: `0`, `3`, `4`, `7`, `8`, or `9`.
5. Use weak-position dissonance only as passing or neighboring motion.
6. End with one final cadence note rather than a post-cadence weak note.
7. Run `python3 midgrid_exercise.py evaluate second-species-above-001 attempt.midgrid --fail-on none`.
8. Repair `exercise_downbeat_dissonance`, `parallel_perfect`, and spacing warnings before recording.

## Worked Exercise Solution: Second Species Above 001

```text
# Title: Second Species Above 001 Solution
# tempo 80

0 | E4:0.5@80 | C3:0.5@70
0.5 | F4:0.5@80 | -
1 | F4:0.5@80 | D3:0.5@70
1.5 | G4:0.5@80 | -
2 | G4:0.5@80 | E3:0.5@70
2.5 | A4:0.5@80 | -
3 | A4:0.5@80 | F3:0.5@70
3.5 | G4:0.5@80 | -
4 | B4:0.5@80 | G3:0.5@70
4.5 | C5:0.5@80 | -
5 | C5:0.5@80 | A3:0.5@70
5.5 | B4:0.5@80 | -
6 | D5:0.5@80 | G3:0.5@70
6.5 | E5:0.5@80 | -
7 | C5:1@80 | C3:1@70
```

Lesson:

- The grid makes strong and weak positions explicit.
- Downbeat consonance can be checked deterministically with `exercise_checks.interval_rules`.
- The harmonic report shows continuous active pairs because V1 hold cells are treated as sustained notes.

## Recorded Training Example: Second Species Above 001

Recorded source:

```text
training_examples/second-species-above-001/20260704T034113Z/
```

Evaluator diagnosis on the blank attempt:

- `exercise_unfilled_voice` appears on every row because V0 is required.
- `exercise_interval_rest` appears on integer beats because no downbeat interval is sounding.

Correction strategy:

- Fill V0 with one note per half-beat through beat 6.5.
- Use a single final note at beat 7.
- Keep all V1 cantus and hold cells unchanged.
- Make every integer-beat V0-V1 interval consonant.
