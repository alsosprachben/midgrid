# Stretto and Episode Patterns

Work these with `stretto-continuation-001` and `episode-sequence-001`. Both exercises derive from the completed D minor fugue whose exposition is documented in `exposition-patterns.md`.

## Stretto Viability

Test overlaps before committing to a stretto. For the D minor subject (`D A F-E D C# D-E F E`):

- At a 2-beat delay at the fifth, the follower's fifth-leap collides with the leader's tail (a seventh on a strong beat). Not viable.
- At a 3-beat delay at the octave, every overlap lands consonant, because the subject's tail is built from the same scale steps as its head. Viable.
- When no full stretto works, stretto on the head alone (first four notes) is the standard fallback; the completed fugue's coda stacks three head entries this way over a dominant pedal.

Viability procedure: write the two entries into a scratch grid at the proposed delay and transposition, run the evaluator, and read the integer-beat intervals. Ten seconds of checking replaces guesswork.

## Recorded Training Example: stretto-continuation-001

The leader (V0) has stated the subject head; the follower (V1) enters at beat 3 an octave below. The task is the leader's continuation.

Attempt (leader shadows the follower):

```text
3 | D4:1@80  | D3:1@76
4 | A4:1@78  | A3:1@76
5 | F4:1@78  | F3:0.5@76
```

Evaluator diagnosis:

- `parallel_perfect` from 3 to 4 and from 4 to 5: the continuation doubled the incoming subject in octaves.

Correction (the subject's own tail, contrary and oblique to the follower):

```text
3 | D4:1@80  | D3:1@76
4 | C#4:1@78 | A3:1@76
5 | D4:1@78  | F3:0.5@76
6 | F4:1@80  | D3:1@76
7 | E4:1@78  | C#3:1@76
8 | D4:1@80  | D3:1@78
```

Lesson:

- Do not shadow the incoming subject; move contrary or oblique against it.
- This subject continues over its own stretto with its own tail figure — a sign of a well-built subject, worth testing on any new one.

## Episode Design

An episode is a sequence: a short model transposed to walk the harmony from one entry key to the next. From the fugue: episode 1 sequenced a suspension figure down to F major; episode 2 descended by fifths through a Neapolitan approach to G minor; episode 3 walked a stepwise bass onto the dominant.

## Recorded Training Example: episode-sequence-001

Over a locked bass (Dm, B-flat, C, arriving on F), state a two-beat model and transpose it down a third, twice.

Attempt (model transposed a step too far):

```text
2   | E4:0.5@80 | B-2:1@72
2.5 | D4:0.5@80 | -
3   | C4:1@80   | D3:1@72
```

Evaluator diagnosis:

- `exercise_downbeat_dissonance` at beat 2 (E4 over B-flat is a tritone) and beat 3 (C4 over D3 is a seventh): every strong beat of the misplaced model is dissonant.

Correction:

```text
2   | F4:0.5@80 | B-2:1@72
2.5 | E4:0.5@80 | -
3   | D4:1@80   | D3:1@72
```

Lesson:

- Transpose the model by the interval the bass dictates and re-check every downbeat against the new bass note.
- A passing tritone on a weak eighth (E4 over B-flat at 2.5) is acceptable and will only warn; the same interval class on a downbeat is an error.
