# MidGrid Composition Skills

This repo now treats composition knowledge as small, example-oriented skills. The intended loop is:

```text
show exercise -> draft strict MidGrid -> evaluate -> repair -> record example -> distill lesson
```

## Skill Map

- `skills/midgrid-strict-output`: enforce parser-valid notation.
- `skills/species-counterpoint`: teach Fux-style species through worked examples.
- `skills/harmonic-effect-control`: use harmonic report metrics to shape aesthetic effects.
- `skills/fugue-exposition`: build and inspect subject-answer-countersubject openings.
- `skills/midgrid-repair-loop`: revise generated passages from `midgrid_eval.py` diagnostics with minimal edits.
- `skills/tuning-render`: render finished MIDI to audio with the adaptive-tuning synthesizer in `../tuning`, choosing a temperament.

## Recommended Curriculum

1. First species above and below a cantus.
2. Second and third species dissonance control.
3. Fourth species suspension preparation and resolution.
4. Fifth species florid line building.
5. Imitation and invertible counterpoint.
6. Fugue exposition.
7. Episode sequencing.
8. Full fugue with report-driven revision.

## Design Principle

Keep rules close to examples. Each successful training cycle should save:

- the prompt or exercise,
- the attempted MidGrid,
- `midgrid_eval.py` output plus `.report.txt`/`.report.json` diagnostics,
- the diagnosis,
- the corrected MidGrid,
- one compact lesson extracted from the correction.

## Exercise Runner

Use `midgrid_exercise.py` as the default local curriculum loop:

```bash
python3 midgrid_exercise.py list
python3 midgrid_exercise.py show first-species-above-001
python3 midgrid_exercise.py evaluate first-species-above-001 attempt.midgrid
python3 midgrid_exercise.py record first-species-above-001 attempt.midgrid corrected.midgrid --lesson "Short repair lesson."
```

Recorded examples are stored under `training_examples/` and can be promoted back into skill references after review.

## Promotion Loop

Treat `training_examples/` as the raw practice journal and `skills/*/references/` as distilled technique.

1. Record a failed attempt and corrected passage with `midgrid_exercise.py record`.
2. Inspect `record.json`, the before/after MidGrid, and the evaluator JSON.
3. Extract the smallest reusable lesson: issue code, local cause, local repair, and resulting effect.
4. Add the compact before/after pair to the relevant skill reference.
5. Prefer several short examples over one long transcript.

This matches Fux's example-first teaching style: the model sees a concrete passage, a diagnosis, a corrected passage, and the compositional principle implied by the correction.

## Example-First Boundary

Rules are guardrails, not the composition skill itself. A new rule is useful only when it helps create, diagnose, or verify better examples.

Prefer this order when teaching a model:

1. Export relevant examples with `midgrid_examples.py --target-exercise-id EXERCISE_ID`.
2. Put the generated pack before the model; it excludes the target solution by default.
3. Let the model imitate the before/diagnosis/after pattern.
4. Run `midgrid_exercise.py evaluate` to get feedback.
5. Record the successful correction and export a better pack next time.

Use `midgrid_examples.py --skill species-counterpoint --format markdown` to build prompt-ready few-shot material from `training_examples/`.

