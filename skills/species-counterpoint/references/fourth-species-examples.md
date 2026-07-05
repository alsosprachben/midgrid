# Fourth Species Examples

Syncopated counterpoint: notes of duration 1 attacked on half-beats, sustained across each downbeat with `-` cells. Half-beat attacks (preparations and resolutions) must be consonant; a dissonant downbeat is a suspension and must resolve down by step. Work these with `fourth-species-above-001`.

## Recorded Training Example: fourth-species-above-001

Attempt (beats 5-7; V1 cantus A3 G3 C3):

```text
5   | -         | A3:0.5@70
5.5 | D5:1@80   | -
6   | -         | G3:0.5@70
6.5 | B4:0.5@80 | -
7   | C5:1@82   | C3:1@70
```

Evaluator diagnosis:

- `exercise_offbeat_dissonance` at beat 5.5: D5 over A3 is a fourth; a preparation must be consonant when struck.

Correction:

```text
5.5 | C5:1@80   | -             // third over A3: consonant preparation
6   | -         | G3:0.5@70     // C5 over G3 is now the 4-3 suspension
6.5 | B4:0.5@80 | -             // resolves down by step
7   | C5:1@82   | C3:1@70
```

Lesson:

- Preparations must be consonant on the half-beat before they suspend. The dissonance belongs on the sustained downbeat, never on the attack.

## Chain Design Against an Ascending Cantus

Full corrected line against `C3 D3 E3 F3 G3 A3 G3 C3`:

```text
(rest) C5 | B4 | C5 | D5 | E5 | C5 | B4 | C5
```

- The opening 8-7-6 gesture (C5 prepared as an octave, suspended as a seventh over D3, resolved to B4) is the only true descending suspension the ascending cantus permits.
- Against rising cantus tones the idiom becomes 6-5: each sixth struck on the half-beat becomes a fifth as the cantus steps up beneath it. Successive downbeat fifths separated by oblique syncopation are legal; the evaluator sees only oblique motion because the voices never attack together.
- Close with the 4-3 suspension (C5 prepared over A3, suspended over G3, resolved to B4) into the final octave: the strongest available cadence in this species.

## Minor Mode and the Descending 7-6 Chain: fourth-species-above-002

The ascending C-major cantus only permits the 6-5 idiom (above). The Fux Dorian cantus descends stepwise from beat 6 to the final, which is what a true 7-6 chain requires: prepare a sixth, hold it while the cantus steps down beneath (making a seventh), resolve down by step to the next sixth, which is again the preparation.

Recorded solution, beats 6.5-10 over cantus `A G F E D`:

```text
6.5 | F4:1@80   | -          // sixth over A: preparation
7   | -         | G3:0.5@70  // seventh: suspension
7.5 | E4:1@80   | -          // resolves to the sixth over G, prepares again
8   | -         | F3:0.5@70  // seventh
8.5 | D4:1@80   | -          // sixth over F
9   | -         | E3:0.5@70  // seventh
9.5 | C#4:0.5@80 | -         // resolution IS the leading tone
10  | D4:1@82   | D3:1@70    // final octave
```

The recorded attempt struck the preparations as sevenths (`exercise_offbeat_dissonance` at 5.5 and 6.5) — the passing-tone habit from second species carried into syncopes.

Lesson:

- The chain's final resolution lands on C# by itself: in minor, the 7-6 chain delivers the cadence for free.
