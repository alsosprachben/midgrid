# Figurae Patterns

Each figura is defined by its interval derivative and its metric placement,
not by its pitches. Notation: `d1` sequences are diatonic scale steps per
attack (chromatic in parentheses where the distinction matters). "Strong"
means an integer beat; "weak" means a half-beat position. Cells are shown
as two-voice MidGrid fragments with the cell voice in V0.

The governing rule for every cell: **the boundary tones on strong beats
carry the harmony and must be consonant; the interior tones are licensed
by the cell's direction.** A dissonance inside a cell is heard as in
transit because the contour predicts its resolution. A dissonance outside
a cell is just noise.

## 1. Passing cell (P) — d1: +1 +1 (or -1 -1)

Fills a third. Interior tone dissonant on the weak position, both
boundaries consonant.

```text
0   | E4:0.5@76 | C3:1@72
0.5 | F4:0.5@74 | -
1   | G4:1@78   | C3:1@72
```

F4 over C3 is a fourth — dissonant, weak, and committed by direction to
G4 (a fifth). The same cell at quarter-beat durations is third species.

## 2. Neighbor cell (N) — d1: -1 +1 (or +1 -1)

Leaves a consonance by step and returns to it.

```text
0   | G4:0.5@76 | C3:1@72
0.5 | F4:0.5@74 | -
1   | G4:1@78   | E3:1@72
```

## 3. Cambiata (C) — d1: -1 -2 +1

Down a step onto the dissonance, down a third, recover a step. The leap
FROM a dissonance is legal here precisely because the cell is a fixed
shape the ear completes: the skipped tone (A4 below) arrives one note
late.

```text
0   | C5:0.5@76 | C4:2@72
0.5 | B4:0.5@74 | -
1   | G4:0.5@76 | -
1.5 | A4:0.5@76 | -
2   | B4:1@76   | G4:1@72
```

Octave, seventh (weak, in the cell), fifth, sixth, then a third at the
next strong beat.

## 4. Enclosure / turn (E) — d1: -2 +1 (chromatic: -3 +1)

Approach the target from above, then from below, then land. This is the
bebop approach-tone pair: the lower tone may be chromatic (F#4 here)
because both neighbors point at the same target — direction, not scale
membership, licenses it.

```text
0   | A4:0.5@76 | C4:1@72
0.5 | F#4:0.5@74 | -
1   | G4:1@78   | E4:1@72
```

The evaluator's vertical layer flags the interior F#4 over C4 as
`high_complexity` — that is the point. The cell spends a vertical
dissonance and the direction redeems it; the warning marks a deliberate
expenditure, not a mistake.

## 5. Escape tone (e) — d1: +1 -3

Step away from a consonance, leap back into one. The dissonance is weak
and brief; the leap lands on a strong consonance.

```text
0   | E4:0.5@76 | C3:1@72
0.5 | F4:0.5@74 | -
1   | C4:1@76   | A2:1@72
```

## 6. Suspension cell (S) — rhythm-domain figura

The one cell whose signature is metric rather than intervallic: attack on
the weak half with duration crossing the strong beat (prep consonant),
dissonant against the new strong-beat harmony, resolve DOWN one step at
the next weak position. d1 after the hold: -1.

```text
0   | A3:0.5@74 | F3:1@72
0.5 | C4:1@78   | -
1   | -         | D3:1@72
1.5 | B3:0.5@76 | -
2   | G3:1@76   | E3:1@74
```

Prep: C4 over F3 is a fifth. The held C4 over D3 is a seventh on the
downbeat — the spent dissonance — resolving to B3, a sixth. Chain
suspensions by making each resolution the next preparation. This is the
cell that distinguishes counterpoint from decorated homophony: it puts
the dissonance ON the strong beat, on purpose, prepaid.

## 7. Sequence rule: cells are episode engines

A cell repeated at a constant diatonic offset is a sequence; the
repetition is the identity, the offset is the harmony. Worked example in
the repo — `fugue_contrapunctus.midgrid` beats 32-39 (Episode 1): a
falling-third cell (d1: -2) alternates between V0 and V1 (each resting
while the other speaks — oblique by construction) over a
descending-fifths bass:

```text
32    | F4:0.5@78  | .          | D3:1@76
32.50 | D4:0.5@76  | .          |
33    | .          | D4:0.5@78  | G2:1@76
33.50 | .          | B-3:0.5@76 |
34    | E4:0.5@78  | .          | C3:1@76
34.50 | C4:0.5@76  | .          |
```

Same cell, sequenced down one step per bar, three voices, zero fusion:
the alternation makes the pair's prevailing motion oblique even though
every cell descends. That is the pattern: sequence the CELL, offset the
HARMONY, alternate the VOICES.

## 8. Compound melody: one voice, two streams

Alternating registers with contrary cell directions makes a single line
imply two voices (solo-cello / bebop texture):

```text
0   | D4:0.5@76 | .
0.5 | B4:0.5@78 | .
1   | C4:0.5@76 | .
1.5 | C5:0.5@78 | .
2   | B3:0.5@76 | .
2.5 | D5:0.5@80 | .
```

Lower stream D4-C4-B3 descends while upper stream B4-C5-D5 ascends: two
contrary predictors in one column. Use it to keep energy up while another
voice carries a suspension chain.

## 9. Directional complementarity (the anti-pattern)

Two voices running the same contour share one predictor and fuse — this
is where fast-texture parallels live, and the evaluator's
`melodic_fusion` warning measures exactly it. Worked negative, adapted
from a cold fugue's outer pair (both voices in locked descent, parallel
fifths at beats 51-51.5):

```text
50   | G4:1@78    | C3:1@78
51   | E-4:0.5@74 | A-2:0.5@78
51.5 | D4:0.5@74  | G2:0.5@78
52   | E-4:1@76   | C3:1@78
```

Correction: give the bass oblique motion and let the upper figure become
a neighbor cell over it. One voice moves, one holds; the dissonant D4 on
the weak half is now licensed by the cell:

```text
50   | G4:1@78    | C3:1@78
51   | E-4:0.5@74 | C3:1@78
51.5 | D4:0.5@74  | -
52   | E-4:1@76   | C3:1@78
```

Budget rule of thumb: within any 4-beat window, a voice pair should show
contrary or oblique motion at least as often as similar motion. The
evaluator flags sustained violations; don't wait for it — assign
complementary cell directions when you compose, voice by voice.

## 10. Target-tone logic (why this works at any speed)

Every cell commits its dissonances to a chord tone at the next strong
beat. That is the entire licensing rule, and it scales: at species tempo
it is the weak-beat passing tone; at eighth-note figuration it is the
approach pattern; over changes it is the bebop scale placing chord tones
on downbeats. When you add a tone, ask: what strong-beat target does its
direction promise, and is that target consonant? If there is no answer,
the tone is fill — cut it or put it inside a cell.

## 11. Rhythmic strata (the Contrapunctus IX rule)

Direction is not the only independence axis. Voices that attack at the
same instants share one clock and fuse into harmonized homophony no
matter how their pitches move — a countersubject that shadows the
subject's rhythm note-for-note is a harmony part, not a counter-melody.
The model is Contrapunctus IX: a racing subject in constant eighths
against the main theme in augmentation, an order of magnitude slower.
The two ideas occupy disjoint rhythmic bands, so the ear cannot merge
them even on rooted intervals.

The rule: **put the countersubject at a different rate, attacking in the
other voice's gaps.** Against a quarter-note subject, write the CS in
half-beat cells (double speed) or in long syncopated notes (half speed,
suspension chains); land the CS's strong tones where the subject holds.
Worked pair — the same subject head, first harmonized (the failure), then
stratified (the fix):

Harmonized (one clock, two "voices"; subject in V1):

```text
0   | B-4:1@78 | G3:1@72
1   | F5:1@78  | D4:1@72
2   | D5:1@78  | B-3:1@72
3   | C5:1@78  | A3:1@72
```

Stratified (double-speed cells in the gaps; co-attacks only at phrase
boundaries):

```text
0   | B-4:0.5@78 | G3:1@72
0.5 | C5:0.5@76  | -
1   | A4:0.5@76  | D4:1@72
1.5 | B-4:0.5@76 | -
2   | D5:0.5@78  | B-3:1@72
2.5 | B-4:0.5@76 | -
3   | C5:0.5@76  | A3:1@72
3.5 | A4:0.5@74  | -
```

The evaluator's `rhythmic_homorhythm` finding measures this piece-wide:
per-pair fraction of time on a shared attack clock. Keep the mean below
about 0.8; deliberate chorale homophony is the only texture that should
sit near 1.0.

## Verification

- `python3 midgrid_eval.py FILE --fail-on none` — no `melodic_fusion`
  warnings, no `voice_fusion` runs inside decorated regions.
- `python3 midgrid_eval.py FILE --strict-parallels --fail-on none` — no
  parallel perfects hiding inside figuration.
- `python3 midgrid_motif.py FILE --compare V0:0-2 V0:4-6` — two statements
  of a cell should match at the diatonic layer (a sequence transposes the
  cell diatonically; contour 1.00, diatonic 1.00).
