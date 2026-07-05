# Fugue Exposition Patterns

Use examples to teach the model what an exposition must make visible.

## Minimal Four-Voice Entry Skeleton

This is a syntax-safe skeleton, not a finished fugue. It shows staggered entries, rests, and countersubject placement.

```text
# Title: Fugue Exposition Skeleton
# tempo 96
// Patch S: 73
// Patch A: 71
// Patch T: 48
// Patch B: 19

0  | C5:1@82 | .       | .       | .
1  | D5:1@82 | .       | .       | .
2  | E5:1@82 | .       | .       | .
3  | G5:1@82 | .       | .       | .
4  | F5:1@78 | G4:1@80 | .       | .
5  | E5:1@78 | A4:1@80 | .       | .
6  | D5:1@78 | B4:1@80 | .       | .
7  | C5:1@78 | D5:1@80 | .       | .
8  | E5:1@76 | C5:1@76 | G3:1@80 | .
9  | D5:1@76 | B4:1@76 | A3:1@80 | .
10 | C5:1@76 | A4:1@76 | B3:1@80 | .
11 | B4:1@76 | G4:1@76 | D4:1@80 | .
12 | C5:1@74 | E4:1@74 | C4:1@74 | C3:1@78
13 | D5:1@74 | F4:1@74 | D4:1@74 | D3:1@78
14 | E5:1@74 | G4:1@74 | E4:1@74 | E3:1@78
15 | C5:1@74 | E4:1@74 | G3:1@74 | C3:1@78
```

## What To Inspect

Subject visibility:

- Does each entry preserve enough contour to be recognized?
- Are entries separated by rests or lighter counterpoint?

Answer:

- Does the answer preserve contour?
- Does it keep tonal center stable?

Countersubject:

- Does it work above the answer?
- Does it later work below the subject or another entry?
- Does it cause parallel perfect intervals?

Texture:

- Are inactive voices explicit rests?
- Are support voices simple until the exposition is clear?

## Example Exercise

Given a two-bar subject, create only an exposition plan first:

```text
Subject: C5 D5 E5 G5 F5 E5 D5 C5
Voices: S A T B
Task: choose entry order, answer type, and countersubject rhythm before writing full MidGrid.
```

## Recorded Training Example: d-minor-exposition-with-invertible-countersubject

A complete worked exposition (three voices, D minor) that passed the evaluator with no errors. Use it as the model for subject design, tonal answer choice, and countersubject invertibility.

Subject (8 beats): `D4 A4 F4-E4 D4 C#4 D4-E4 F4 E4` — fifth leap up, stepwise descent through the leading tone, rise back to the third.

Tonal answer: the head's 1-to-5 (`D` to `A`) is answered 5-to-1 (`A4` to `D5`); the tail continues as a real transposition up a fifth (`C5-B4 A4 G#4 A4-B4 C5 B4`). The G# effects the modulation to the dominant minor.

Countersubject degrees: `6 7 8-7 6 5 3 5 4` (in A minor: `F G A-G F E C E D`), rhythmically complementary to the subject (quarters against its eighths and vice versa).

Invertibility proof, required before trusting the countersubject:

Below the answer (beats 8-11, CS in alto):

```text
8  | A4:1@86   | F4:1@76
9  | D5:1@86   | G4:1@76
10 | C5:0.5@84 | A4:0.5@76
11 | A4:1@84   | F4:1@76
```

Above the subject (beats 16-19, CS in soprano, subject in bass):

```text
16 | B-4:1@78 | F4:1@72 | D3:1@86
17 | C5:1@78  | E4:1@72 | A3:1@86
18 | D5:0.5@78 | F4:1@72 | F3:0.5@84
19 | B-4:1@78 | F4:1@72 | D3:1@84
```

The thirds below the answer become sixths and tenths above the subject; both positions are consonant, so the countersubject is invertible at the octave.

Lesson:

- Choose a tonal answer when the subject opens with scale-degree 5-to-1 or 1-to-5 motion.
- Prove the countersubject in at least two vertical positions before writing later entries; in the full fugue this countersubject also served in the bass (a third position) without repair.
- Give the countersubject complementary rhythm so each line stays audible in the grid and in the ear.
