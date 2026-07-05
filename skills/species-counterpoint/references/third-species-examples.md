# Third Species Examples

Four quarter-beat notes against each cantus note. Integer downbeats must be consonant; quarter-beat dissonances must be passing or neighbor tones approached and left by step. Work these with `third-species-above-001`.

## Recorded Training Example: third-species-above-001

Attempt (beats 0-1 and 6; V1 cantus C3 D3 ... G3 locked):

```text
0    | G4:0.25@80 | C3:0.25@70
0.25 | A4:0.25@80 | -
0.5  | B4:0.25@80 | -
0.75 | C5:0.25@80 | -
1    | D5:0.25@80 | D3:0.25@70
...
6    | C5:0.25@80 | G3:0.25@70
```

Evaluator diagnosis:

- `parallel_perfect` from beat 0.75 to 1: C5 over C3 is an octave, D5 over D3 is an octave, both voices ascending.
- `exercise_downbeat_dissonance` at beat 6: C5 over G3 is a fourth on an integer beat.

Correction:

```text
0.75 | C5:0.25@80 | -
1    | A4:0.25@80 | D3:0.25@70    // skip down to the fifth; octave arrives obliquely or not at all
...
6    | B4:0.25@80 | G3:0.25@70    // third on the downbeat; C5 becomes the weak passing tone
6.25 | C5:0.25@80 | -
```

Lesson:

- Check every quarter-to-downbeat attack pair for parallels, and put a consonance on every integer beat.

## Line Design

The corrected solution's full line, one bar per cantus note:

```text
G4 A4 B4 C5 | A4 B4 C5 D5 | G4 F4 E4 G4 | A4 G4 F4 A4 | B4 A4 G4 B4 | E5 D5 C5 A4 | B4 C5 D5 B4 | C5
```

- One peak (E5) placed at the golden-ratio bar, approached by leap to a consonance, left by step.
- Sequences (bars 1-2) give direction; the repeated-bar trap (bar 3 copying bar 1) is avoided by inverting the contour.
- Cadence formula: `B4 C5 D5 B4 | C5` places the leading tone on the last quarter before the final.
