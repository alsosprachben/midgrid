# MidGrid Example Pack

Use these as few-shot learning material: imitate the attempt, diagnosis, correction, and lesson pattern. Rules are included only as diagnostic labels and validation checks.

## Example 1: Canon at the Octave, Two Beats Delay

Exercise: `canon-at-octave-001`
Skill: `fugue-exposition`
Species: `canon`
Record: `training_examples/canon-at-octave-001/20260705T040216Z/record.json`

Objective:
Continue a two-voice canon at the octave: the follower (V1) sings exactly what the leader (V0) sang two beats earlier, an octave lower. The seed gives the leader's first two notes and their echoes.

Prompt:
Fill both voices through beat 10. Canon constraint: every leader note at beat b must reappear in V1 at beat b+2 transposed down an octave, through the follower's beat 8. The last two beats are a free cadence in both voices (traditional license): close leading-tone to final over 5-1. Composing forward means every new leader note must be consonant with your own note of two beats ago; integer-beat intervals must be consonant and no parallel perfects. Watch sequences: transposing your last two notes up or down by the same interval creates parallel motion with your own echo.

Attempt issue codes:
exercise_downbeat_dissonance=1, parallel_perfect=1

Diagnosis excerpt:
- error parallel_perfect (beat 3, V0-V1): Parallel perfect interval in V0-V1 from beat 2 to 3.
- error exercise_downbeat_dissonance (beat 4, V0-V1): Canon intervals must be consonant: V0-V1 interval class 2 is not allowed at beat 4.

Attempt:
```text
# Title: Canon at the Octave Exercise 001
# tempo 80

0 | D4:1@80 | .
1 | F4:1@80 | .
2 | A4:1@80 | D3:1@76
3 | C5:1@80 | F3:1@76
4 | B4:1@80 | A3:1@76
5 | A4:1@80 | C4:1@76
6 | G4:1@80 | B3:1@76
7 | F4:1@80 | A3:1@76
8 | E4:1@80 | G3:1@76
9 | C#4:1@80 | A3:1@76
10 | D4:1@80 | D3:1@76
```

Correction:
```text
# Title: Canon at the Octave Exercise 001
# tempo 80

0 | D4:1@80 | .
1 | F4:1@80 | .
2 | A4:1@80 | D3:1@76
3 | D5:1@80 | F3:1@76
4 | C5:1@80 | A3:1@76
5 | B4:1@80 | D4:1@76
6 | A4:1@80 | C4:1@76
7 | G4:1@80 | B3:1@76
8 | E4:1@80 | A3:1@76
9 | C#4:1@80 | A3:1@76
10 | D4:1@80 | D3:1@76
```

Result:
errors=0, warnings=0, beats=11, mean_complexity=6.222

Lesson:
In canon you counterpoint your own past: transposing your previous two-note step by the same interval moves in exact parallel with your echo, so change direction or interval size at least every second note.

## Example 2: Sequence a Two-Beat Model Over a Descending Bass

Exercise: `episode-sequence-001`
Skill: `fugue-exposition`
Species: `episode`
Record: `training_examples/episode-sequence-001/20260705T031032Z/record.json`

Objective:
Over the locked bass (D minor, B-flat, C, arriving on F), compose an upper voice built from one two-beat melodic model stated at beats 0-1 and transposed down a third at 2-3 and again at 4-5, then cadence into the F arrival.

Prompt:
Fill V0: state a two-beat model (for example eighth-eighth-quarter) at beats 0-1, transpose the same model down a third for beats 2-3 and again for beats 4-5 so it follows the bass, then close freely over beats 6-7. Adjust the transposition to the harmony, not mechanically: every integer-beat interval must be consonant. Weak-eighth dissonances are acceptable when stepwise and brief.

Attempt issue codes:
exercise_downbeat_dissonance=2, high_complexity=1

Diagnosis excerpt:
- warning high_complexity (beat 2, V0-V1): V0-V1 reaches perceptual complexity 38.5 at beat 2.
- error exercise_downbeat_dissonance (beat 2, V0-V1): Episode downbeats must be consonant: V0-V1 interval class 6 is not allowed at beat 2.
- error exercise_downbeat_dissonance (beat 3, V0-V1): Episode downbeats must be consonant: V0-V1 interval class 10 is not allowed at beat 3.

Attempt:
```text
# Title: Episode Sequence Exercise 001 Attempt
# tempo 84

0 | A4:0.5@80 | D3:1@72
0.5 | G4:0.5@80 | -
1 | F4:1@80 | F3:1@72
2 | E4:0.5@80 | B-2:1@72
2.5 | D4:0.5@80 | -
3 | C4:1@80 | D3:1@72
4 | E4:0.5@80 | C3:1@72
4.5 | D4:0.5@80 | -
5 | C4:1@80 | E3:1@72
6 | C4:1@78 | F3:2@72
7 | A3:1@78 | -
```

Correction:
```text
# Title: Episode Sequence Exercise 001 Solution
# tempo 84

0 | A4:0.5@80 | D3:1@72
0.5 | G4:0.5@80 | -
1 | F4:1@80 | F3:1@72
2 | F4:0.5@80 | B-2:1@72
2.5 | E4:0.5@80 | -
3 | D4:1@80 | D3:1@72
4 | E4:0.5@80 | C3:1@72
4.5 | D4:0.5@80 | -
5 | C4:1@80 | E3:1@72
6 | C4:1@78 | F3:2@72
7 | A3:1@78 | -
```

Result:
errors=0, warnings=1, beats=11, mean_complexity=8.091

Lesson:
Transpose the sequence model by the interval the bass pattern dictates, checking every downbeat against the new bass note; a mechanical transposition one step too far turns every strong beat dissonant.

## Example 3: Continue the Subject Over Its Own Stretto Entry

Exercise: `stretto-continuation-001`
Skill: `fugue-exposition`
Species: `stretto`
Record: `training_examples/stretto-continuation-001/20260705T031032Z/record.json`

Objective:
The leader states the subject head in V0; at beat 3 the follower enters in V1 with the subject an octave below. Compose the leader's continuation (beats 4-8) over the incoming subject, closing on the final octave.

Prompt:
Fill V0 beats 4-8 with a continuation line against the locked follower. Do not alter the given subject notes in either voice. Integer-beat intervals must be consonant; move contrary or oblique against the follower and do not shadow it in parallel perfect intervals. End beat 8 on D4 over the follower's final D3. Note: this subject admits an octave stretto at a 3-beat delay; a 2-beat delay at the fifth fails on beat 3.

Attempt issue codes:
parallel_perfect=2

Diagnosis excerpt:
- error parallel_perfect (beat 4, V0-V1): Parallel perfect interval in V0-V1 from beat 3 to 4.
- error parallel_perfect (beat 5, V0-V1): Parallel perfect interval in V0-V1 from beat 4 to 5.

Attempt:
```text
# Title: Stretto Continuation Exercise 001 Attempt
# tempo 84

0 | D4:1@80 | .
1 | A4:1@80 | .
2 | F4:0.5@80 | .
2.5 | E4:0.5@80 | .
3 | D4:1@80 | D3:1@76
4 | A4:1@78 | A3:1@76
5 | F4:1@78 | F3:0.5@76
5.5 | - | E3:0.5@76
6 | D4:1@78 | D3:1@76
7 | E4:1@78 | C#3:1@76
8 | D4:1@80 | D3:1@78
```

Correction:
```text
# Title: Stretto Continuation Exercise 001 Solution
# tempo 84

0 | D4:1@80 | .
1 | A4:1@80 | .
2 | F4:0.5@80 | .
2.5 | E4:0.5@80 | .
3 | D4:1@80 | D3:1@76
4 | C#4:1@78 | A3:1@76
5 | D4:1@78 | F3:0.5@76
5.5 | - | E3:0.5@76
6 | F4:1@80 | D3:1@76
7 | E4:1@78 | C#3:1@76
8 | D4:1@80 | D3:1@78
```

Result:
errors=0, warnings=0, beats=11, mean_complexity=6.571

Lesson:
Do not shadow the incoming subject in octaves; the leader's continuation should move contrary or oblique against the follower, and this subject's own tail (C# D F E D) already harmonizes its head at the octave.
