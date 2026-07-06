---
name: figurae
description: Compose florid, independent counterpoint from directional interval cells (figurae) with metric placement rules. Use when a passage needs more rhythmic energy than note-against-note writing without collapsing voices into one stream, when decorating a species framework into florid texture, when building episodes from sequenced cells, or when repairing melodic_fusion and parallel findings inside fast figuration.
---

# Figurae: Directional Cells

## The principle

A figura is a short cell defined by its interval derivative (d1) and its
metric placement, not by its pitches. The cell's direction is a contract:
the listener extrapolates where the line is going, so a dissonance inside
the cell is heard as in transit — already resolved by the promised motion.
Dissonance is licensed by trajectory. This is the same grammar at every
tempo: Fux's weak-beat passing tone and the bebop enclosure both commit a
dissonance to a target tone on the next strong beat.

The converse is the failure mode: figuration without directional identity
is fill, and two voices running the same contour fuse into one stream —
that is where fast-texture parallels live. Voice independence in florid
writing is directional independence.

## Workflow

1. Read `references/figurae-patterns.md` for the cell vocabulary, each with
   its d1 signature, metric placement, and a worked MidGrid pair.
2. Start from a correct simple framework (first-species skeleton or the
   existing voice pair) and decorate it cell by cell; every added dissonance
   must sit inside a named cell whose strong-beat boundary tones are
   consonant against the other voices.
3. Keep the voices directionally complementary: while one voice runs a
   descending cell, give the other an ascending, contrary, or oblique cell
   (a held tone is oblique). Never let a pair share prevailing direction
   for more than about 4 beats.
3b. Keep the voices rhythmically stratified (the Contrapunctus IX rule):
   a countersubject or counter-line lives at a DIFFERENT rate than the
   subject — double-speed cells or half-speed syncopated lines — and
   attacks in the other voice's gaps, not on its beats. A counter-line
   that shares the subject's attack clock is a harmonization, not
   counterpoint.
4. Build episodes by sequencing one cell at a constant diatonic offset;
   the repetition is the engine, the offset is the harmony.
5. Verify: `python3 midgrid_eval.py FILE` must show no `melodic_fusion`
   warnings and no fusion/parallel findings inside the decorated region;
   `python3 midgrid_motif.py FILE --compare SEG SEG` confirms two
   statements of a cell are the same figura (diatonic d1 match).

## Rule priority

1. Parser-valid MidGrid.
2. Strong-beat tones consonant (cell boundaries carry the harmony).
3. Every dissonance inside a named cell, resolved where the cell promises.
4. Directional complementarity between voices (no shared prevailing
   direction beyond ~4 beats; no locked rhythm+direction).
5. Cell coherence: prefer sequencing one cell to stringing unrelated fill.
6. Contour with one peak per phrase; land the phrase on a chord tone.

## Output pattern

```text
Objective: decorate the pair into florid texture with N cells.
Attempt:
[MidGrid]
Diagnosis:
[cells named per beat; melodic_fusion / interval findings]
Correction:
[MidGrid]
```

If the user requests only notation, output only the corrected MidGrid.
