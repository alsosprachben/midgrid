# Canon Patterns

Work these with `canon-at-octave-001`. A canon is self-imitation under a fixed rule: follower = leader delayed by d beats, transposed by interval t. It is the strictest form of the imitation family that also contains stretto (see `stretto-and-episodes.md`); a subject that canons well strettos well.

## Composing Forward Against Your Own Past

At every new leader beat b you are writing two-voice counterpoint against a note you already chose: the follower is sounding leader(b-d) transposed. So the discipline is local and mechanical:

1. Before choosing leader(b), read your own note from d beats ago and transpose it: that is the bass you are harmonizing.
2. Check the new vertical (consonant on integer beats) and the motion from the previous pair (no parallel perfects).
3. The sequence trap: if leader(b-1) to leader(b) repeats the same melodic interval as leader(b-d-1) to leader(b-d), both voices move identically and every perfect interval becomes parallel. Change direction or interval size at least every second note.
4. Triadic openings canon easily (each note consonant with the note two back); scalewise runs canon in parallel imperfect intervals, which is legal but best in thirds/sixths territory.

## Cadence License

Strict canon has no ending; the tradition is to break the imitation for the final cadence. In `canon-at-octave-001` the follower keeps the canon through its echo of the leader's beat-8 note, then both voices cadence freely: leading tone rising against 2-1, closing on the octave.

## Recorded Training Example: canon-at-octave-001

Attempt (leader continues the rising sequence mechanically):

```text
2 | A4:1@80 | D3:1@76
3 | C5:1@80 | F3:1@76
4 | B4:1@80 | A3:1@76
```

Evaluator diagnosis:

- `parallel_perfect` from 2 to 3: A4 over D3 and C5 over F3 are both twelfths, and both voices rose by the same minor third — the leader's echo copied its own motion.
- `exercise_downbeat_dissonance` at beat 4: B4 over A3 is a ninth; the leader forgot to harmonize its own note from two beats before.

Correction:

```text
2 | A4:1@80 | D3:1@76
3 | D5:1@80 | F3:1@76
4 | C5:1@80 | A3:1@76
```

Lesson:

- In canon you counterpoint your own past; break your own sequences before your echo turns them into parallels.
