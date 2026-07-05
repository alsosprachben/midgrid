# Fifth Species Examples

Florid counterpoint on a fixed quarter-beat lattice: mix durations 0.25, 0.5, and 1 with `-` sustain cells, combining suspension, passing, and running figures. Work these with `fifth-species-above-001`.

## Recorded Training Example: fifth-species-above-001

Attempt (beats 2.5-4; V1 cantus E3 F3 G3):

```text
2.5  | A4:0.25@80 | -
2.75 | B4:0.25@80 | -
3    | C5:1@80    | F3:0.25@70
...
4    | D5:0.5@82  | G3:0.25@70
```

Evaluator diagnosis:

- `parallel_perfect` from 2.75 to 3: B4 over E3 is a fifth, C5 over F3 is a fifth, both voices rising as the run lands together with the cantus attack.
- `parallel_perfect` from 3.75 to 4: the sustained C5 over F3 (a fifth) moves to D5 over G3 (a fifth) as both voices attack beat 4.

Correction:

```text
2.5  | A4:0.25@80 | -
2.75 | B4:0.25@80 | -
3    | A4:1@80    | F3:0.25@70   // turn figure lands on the third
...
4    | D5:0.5@82  | G3:0.25@70   // fifth now approached from an imperfect consonance
```

Lesson:

- In florid writing, parallels hide where an ornamental run lands together with a cantus attack. Land runs on imperfect consonances.

## Rhythm Design

Full corrected line (attack points):

```text
(rest) C5:1 | ~ B4:0.5 | G4:0.5 A4:0.25 B4:0.25 | A4:1 | D5:0.5 E5:1 | ~ C5:1 | ~ B4:0.5 | C5:1
```

- Opens like fourth species (suspension 8-7-6), moves through second-species halves into a quarter-beat turn, and cadences with the 4-3 suspension: all prior species audible in one line.
- Longer values sit on structural beats; quarters connect them. Rhythmic variety serves phrase direction, not decoration.
- The E5 peak arrives on an offbeat sixth and sustains through the fifth, binding bars 4-5 across the barline.
