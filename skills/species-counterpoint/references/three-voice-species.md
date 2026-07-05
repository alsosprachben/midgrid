# Three-Voice Species

Work these with `three-voice-first-species-001`. The rules of two-voice species still hold per pair; what changes is that the number of pairs grows faster than the number of voices:

| Voices | Pairs to check |
|---|---|
| 2 | 1 |
| 3 | 3 |
| 4 | 6 |

Three consecutive capstone compositions in this repo failed their first drafts with parallel perfects, each time in the newest least-watched pair (soprano-alto, then soprano-bass, then soprano-tenor). This drill targets exactly that failure: the cantus sits in the middle voice, both outer voices are composed, and all three pairs carry error-level consonance and parallel checks.

## Guidance

- Prefer complete triads; when a tone must be omitted, keep root and third and let the fifth go.
- Fourths are consonant between upper voices when the lowest voice supports them (6-3 sonorities); against the lowest voice they remain dissonant.
- Approach perfect intervals by contrary or oblique motion in EVERY pair. The pair between your two composed voices deserves the most attention precisely because neither line is the cantus.
- Avoid 6-4 sonorities on the beat in first species.
- The cadence retains the two-voice formulas stacked: leading tone rising in one voice, 2-1 in the cantus, and the lowest voice cadencing by fifth. The bass falling a fifth into the final octave produces one `direct_perfect` warning; it is the traditional close and is acceptable.

## Recorded Training Example: three-voice-first-species-001

Attempt (beats 6-8; V0 and V2 each correct against the middle cantus, parallel with each other):

```text
6 | C5:1@80  | A4:1@70 | F3:1@76
7 | B4:1@80  | G4:1@70 | E3:1@76
8 | A4:1@80  | F4:1@70 | D3:1@76
```

Evaluator diagnosis:

- `parallel_perfect` V0-V2 from 6 to 7 and 7 to 8: the outer voices descend in parallel twelfths while both make perfect thirds and tenths against the cantus.

Correction (upper voice repeats, then moves contrary to the bass):

```text
6 | C5:1@80  | A4:1@70 | F3:1@76
7 | C5:1@80  | G4:1@70 | E3:1@76
8 | D5:1@80  | F4:1@70 | D3:1@76
```

Lesson:

- Correctness against the cantus proves nothing about the third pair. Repetition and contrary motion are the cheapest repairs: hold one voice, or send the outer voices apart.
