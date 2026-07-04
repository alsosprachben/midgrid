# Training Example Promotion

Use this workflow after `midgrid_exercise.py record` creates a reviewed example under `training_examples/`.

The goal is not to paste full logs into a skill. Promote only the compact lesson that will help the next composition attempt.

## Source Material

For a recorded example directory such as:

```text
training_examples/parallel-perfect-repair-001/20260703T035620Z/
```

inspect:

- `record.json` for exercise id, lesson, paths, and evaluation summaries.
- `attempt.midgrid` for the failed or incomplete draft.
- `corrected.midgrid` for the repaired passage.
- `attempt.eval.json` and `corrected.eval.json` for issue-code changes.
- `corrected.report.json` when the harmonic effect or beat-level diagnostics matter.

## Promotion Shape

Add a short section to the most relevant skill reference:

```text
## Recorded Training Example: exercise-id

Attempt:
[small MidGrid excerpt]

Evaluator diagnosis:
- issue code, beat, voice pair, and cause

Correction:
[small MidGrid excerpt]

Lesson:
- one or two reusable composition actions
```

Keep examples small enough to fit inside future prompts. A good promoted example lets a model imitate the repair without reading the full training directory.

## What To Preserve

- The spatial beat grid.
- Locked or cantus voices that must remain unchanged.
- The evaluator issue code that motivated the repair.
- The smallest musical change that fixed the issue.
- Any aesthetic-effect target, such as reducing complexity before cadence.

## What To Omit

- Full parser logs unless syntax is the lesson.
- Long reports with no changed conclusion.
- Duplicate examples of the same repair pattern.
- Unreviewed attempts that happen to pass mechanically but sound weak.

## Promotion Targets

- Syntax and notation repairs: `skills/midgrid-strict-output/references/`.
- Species exercises: `skills/species-counterpoint/references/`.
- Harmonic effect shaping: `skills/harmonic-effect-control/references/`.
- Fugue exposition examples: `skills/fugue-exposition/references/`.
- General generate-analyze-revise repairs: `skills/midgrid-repair-loop/references/repair-patterns.md`.

## Acceptance Check

After promotion, the skill should contain:

- a before/after MidGrid pair,
- a named evaluator or exercise issue,
- a concrete local repair,
- a one-sentence lesson that can be reused in a new composition.
