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
- Does it live in its own rhythmic stratum (double speed, half speed, or
  syncopated against the entry), or does it merely shadow the entry's
  attacks? The skeleton above is 1:1 for syntax clarity only — a real
  countersubject must not be.

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

## Recorded Training Example: invertible countersubject in its own rhythmic stratum

The worked model for subject design, tonal answer choice, and
countersubject writing. Full attempt/correction pair recorded under
`invertible-counterpoint-001`; the ATTEMPT there is the old
harmonization-style countersubject, kept as the named negative.

Subject (8 beats): `D4 A4 F4-E4 D4 C#4 D4-E4 F4 E4` — fifth leap up, stepwise descent through the leading tone, rise back to the third.

Tonal answer: the head's 1-to-5 (`D` to `A`) is answered 5-to-1; the tail continues as a real transposition. The raised leading tone (G# against an A entry) effects the modulation to the dominant minor.

Countersubject: **species counterpoint against the answer, in a different
rhythmic stratum** — the answer is a cantus, so write against it exactly
as the species curriculum taught. This one is syncopated second species:
it attacks in the subject's gaps (off-halves), holds tones across the
subject's beats, and never shadows its attack pattern. A countersubject
that attacks wherever the subject attacks is a harmonization, whatever
its intervals (see rhythmic_homorhythm in the evaluator, and the
Contrapunctus IX rule in the figurae reference).

Below the subject (section A; the subject holds while the CS moves, and
vice versa):

```text
0   | D4:1@80   | F3:0.5@72
0.5 | -         | A3:1@72
1   | A4:1@80   | -
1.5 | -         | D4:1@72
2   | F4:0.5@80 | -
2.5 | E4:0.5@80 | C4:0.5@72
3   | D4:1@80   | B-3:0.5@72
3.5 | -         | A3:1@72
4   | C#4:1@80  | -
4.5 | -         | F3:1@72
5   | D4:0.5@80 | -
5.5 | E4:0.5@80 | A3:1@72
6   | F4:1@80   | -
6.5 | -         | C#4:1@72
7   | E4:1@80   | -
7.5 | -         | A3:0.5@72
```

Above the subject an octave lower (section B), the SAME pitches: thirds
become sixths, the octave at beat 1 becomes a unison. Invertibility at
the octave demands that every integer-beat interval be a unison, third,
or sixth — never a fifth, because fifths invert to fourths.

Lesson:

- Choose a tonal answer when the subject opens with scale-degree 5-to-1 or 1-to-5 motion.
- The countersubject is species counterpoint against the answer-as-cantus: pick a species (second, third, or syncopated) and stay in its stratum. Do not harmonize the subject's rhythm note for note.
- Prove the countersubject in at least two vertical positions before writing later entries, on downbeat unisons/thirds/sixths only.
- Verify with the evaluator: no rhythmic_homorhythm finding, no melodic_fusion, no parallels in either position.
