# First Species Examples

These examples use two voices: `V0` is counterpoint above, `V1` is cantus below.

## Positive Example

```text
# Title: First Species Positive Example
# tempo 80

0 | E4:1@80 | C3:1@70
1 | F4:1@80 | D3:1@70
2 | G4:1@80 | E3:1@70
3 | A4:1@80 | F3:1@70
4 | G4:1@80 | G3:1@70
5 | F4:1@80 | A3:1@70
6 | E4:1@80 | G3:1@70
7 | C4:1@80 | C3:1@70
```

Why it works:

- The visible beat grid makes each vertical interval inspectable.
- Most sonorities are imperfect consonances.
- The final resolves to a stable octave compound.
- The upper line is mostly stepwise and settles into the final octave without spacing warnings.

## Negative Example: Parallel Perfect Fifths

```text
# Title: First Species Negative Example
# tempo 80

0 | G4:1@80 | C3:1@70
1 | A4:1@80 | D3:1@70
2 | B4:1@80 | E3:1@70
3 | C5:1@80 | F3:1@70
```

Problem:

- Beats 0 to 1 move from a compound fifth to another compound fifth by similar motion.
- The spatial grid makes the repeated shape obvious: both voices move up by step while preserving the perfect fifth class.

## Corrected Version

```text
# Title: First Species Corrected Example
# tempo 80

0 | G4:1@80 | C3:1@70
1 | F4:1@80 | D3:1@70
2 | G4:1@80 | E3:1@70
3 | A4:1@80 | F3:1@70
```

Repair:

- Beat 1 changes only the upper voice.
- The bad parallel perfect motion is replaced by contrary motion into an imperfect consonance.

## Exercise Prompt

Complete beats 4 to 7 while preserving first-species discipline:

```text
# Title: First Species Exercise
# tempo 80

0 | E4:1@80 | C3:1@70
1 | F4:1@80 | D3:1@70
2 | G4:1@80 | E3:1@70
3 | A4:1@80 | F3:1@70
4 | .       | G3:1@70
5 | .       | A3:1@70
6 | .       | G3:1@70
7 | .       | C3:1@70
```


## Procedure: Solving A First-Species Exercise

Use this procedure when `midgrid_exercise.py show first-species-above-001` or a similar exercise is the prompt.

1. Identify the cantus voice from `exercise_checks.locked_voices`.
2. Identify the target voice from `exercise_checks.filled_voices`.
3. Keep the cantus cells exactly unchanged.
4. Fill every target-voice rest with one note cell of the same duration style.
5. Prefer imperfect consonances inside the phrase: thirds and sixths, including compound forms.
6. Use perfect fifths and octaves mostly at structural start/end points.
7. Avoid moving both voices in the same direction into repeated perfect fifth/octave classes.
8. Run `python3 midgrid_exercise.py evaluate EXERCISE_ID attempt.midgrid --fail-on none`.
9. Repair the smallest beat span that removes `parallel_perfect`, `voice_crossing`, and exercise-specific errors.

## Worked Exercise Solution: First Species Above 001

Exercise seed:

```text
# Title: First Species Above Exercise 001
# tempo 80

0 | E4:1@80 | C3:1@70
1 | F4:1@80 | D3:1@70
2 | G4:1@80 | E3:1@70
3 | A4:1@80 | F3:1@70
4 | .       | G3:1@70
5 | .       | A3:1@70
6 | .       | G3:1@70
7 | .       | C3:1@70
```

One valid completion:

```text
# Title: First Species Above Exercise 001 Solution
# tempo 80

0 | E4:1@80 | C3:1@70
1 | F4:1@80 | D3:1@70
2 | G4:1@80 | E3:1@70
3 | A4:1@80 | F3:1@70
4 | G4:1@80 | G3:1@70
5 | F4:1@80 | A3:1@70
6 | E4:1@80 | G3:1@70
7 | C4:1@80 | C3:1@70
```

Lesson:

- Keep the cantus unchanged and fill the target voice completely.
- The added upper line moves mostly by step and keeps consonant vertical sonorities.
- The final returns to C4 over C3, giving the exercise a stable close without wide-spacing or direct-perfect warnings.

## Recorded Training Example: First Species Above 001

Recorded source:

```text
training_examples/first-species-above-001/20260703T223203Z/
```

Attempt:

```text
4 | .       | G3:1@70
5 | .       | A3:1@70
6 | .       | G3:1@70
7 | .       | C3:1@70
```

Evaluator diagnosis:

- `exercise_unfilled_voice` appears at beats 4, 5, 6, and 7 because V0 is the required filled voice.
- `exercise_checks.locked_voices=[1]` means V1 is the cantus and must remain unchanged.

Correction:

```text
4 | G4:1@80 | G3:1@70
5 | F4:1@80 | A3:1@70
6 | E4:1@80 | G3:1@70
7 | C4:1@80 | C3:1@70
```

Lesson:

- Fill the target voice while copying the locked cantus exactly.
- Prefer a singable local line that reaches the final octave without triggering spacing or direct-perfect warnings.

## Recorded Training Example: First Species Below 001

Recorded source:

```text
training_examples/first-species-below-001/20260704T161337Z/
```

Attempt:

```text
0 | C5:1@80 | C3:1@70
1 | B4:1@80 | .
2 | A4:1@80 | .
3 | G4:1@80 | .
4 | F4:1@80 | .
5 | E4:1@80 | .
6 | D4:1@80 | .
7 | C4:1@80 | C3:1@70
```

Evaluator diagnosis:

- `exercise_unfilled_voice` appears at beats 1 through 6 because V1 is the required lower counterpoint voice.
- `exercise_checks.locked_voices=[0]` means V0 is the upper cantus and must remain unchanged.

Correction:

```text
0 | C5:1@80 | C3:1@70
1 | B4:1@80 | D3:1@70
2 | A4:1@80 | F3:1@70
3 | G4:1@80 | E3:1@70
4 | F4:1@80 | D3:1@70
5 | E4:1@80 | C3:1@70
6 | D4:1@80 | B2:1@70
7 | C4:1@80 | C3:1@70
```

Lesson:

- Fill the lower voice while copying the upper cantus exactly.
- Use contrary and mixed motion so the lower line stays independent, consonant, and below the cantus.
- The corrected passage evaluates with zero errors and zero warnings.

