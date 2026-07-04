# MidGrid Exercise Runner

`midgrid_exercise.py` runs example-oriented composition exercises. It is the first local training loop for Fux-style MidGrid learning.

## Commands

```bash
python3 midgrid_exercise.py list
python3 midgrid_exercise.py show first-species-above-001
python3 midgrid_exercise.py evaluate first-species-above-001 attempt.midgrid
python3 midgrid_exercise.py record first-species-above-001 attempt.midgrid corrected.midgrid --lesson "Changed beat 1 to contrary motion."
python3 midgrid_examples.py --skill species-counterpoint --format markdown
```

## Exercise Schema

Exercises live in `exercises/*.json` and use this shape:

```json
{
  "id": "first-species-above-001",
  "title": "First Species Above a Cantus",
  "skill": "species-counterpoint",
  "species": "first",
  "objective": "Complete a strict first-species counterpoint above the cantus.",
  "prompt": "Replace rests in V0...",
  "seed_midgrid": "# Title...",
  "success_criteria": ["No evaluator error issues remain."],
  "evaluation_defaults": {
    "fail_on": "error",
    "high_complexity_threshold": 30.0,
    "wide_spacing_threshold": 19
  },
  "exercise_checks": {
    "locked_voices": [1],
    "filled_voices": [0],
    "interval_rules": [
      {
        "label": "Downbeats must be consonant",
        "voice_pair": "V0-V1",
        "beat_filter": "integer",
        "allowed_interval_classes": [0, 3, 4, 7, 8, 9],
        "code": "exercise_downbeat_dissonance",
        "severity": "error"
      }
    ]
  },
  "recording": {
    "corrected_fail_on": "error"
  }
}
```

## Evaluation Behavior

`evaluate` runs `midgrid_eval.py` with the exercise's `evaluation_defaults` unless CLI flags override them, then appends exercise-specific structural checks.

`record` requires:

- attempt and corrected files pass `midgrid_lint.py` through evaluator lint results,
- corrected file passes evaluator plus exercise checks under `recording.corrected_fail_on`, defaulting to `error`,
- all artifacts are copied to `training_examples/<exercise-id>/<timestamp>/`.

Each record contains:

```text
attempt.midgrid
corrected.midgrid
attempt.eval.json
corrected.eval.json
attempt.report.txt/json when available
corrected.report.txt/json when available
record.json
```

## Current Exercises

- `first-species-above-001`
- `first-species-below-001`
- `parallel-perfect-repair-001`
- `complexity-release-repair-001`
- `second-species-above-001`

## Exercise Checks

`exercise_checks.locked_voices` lists voice columns that must match the seed MidGrid exactly. Use this for cantus firmus or preserved bass lines.

`exercise_checks.filled_voices` lists voice columns that must contain note cells on every grid row. Rests, holds, and empty cells fail this check.

Exercise check failures are appended to evaluator `issues` with codes such as `exercise_locked_voice_changed`, `exercise_unfilled_voice`, `exercise_beat_changed`, `exercise_row_count`, `exercise_interval_rest`, and custom interval-rule codes.

`exercise_checks.interval_rules` lists report-driven vertical interval checks. Each rule can specify:

- `voice_pair`: a report label such as `V0-V1`.
- `beat_filter`: `all`, `integer`, or `non_integer`.
- `beats`: an explicit beat list, used instead of `beat_filter` when present.
- `exclude_beats`: beats to skip.
- `allowed_interval_classes`: semitone classes modulo 12.
- `code`, `severity`, and `label`: diagnostic metadata.

For example, second-species exercises can enforce consonant downbeats with allowed interval classes `[0, 3, 4, 7, 8, 9]` on integer beats.


Related: `midgrid_examples.py` turns recorded training examples into prompt-ready example packs. See `midgrid_examples.md`.
