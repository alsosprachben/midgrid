---
name: midgrid-repair-loop
description: Revise MidGrid compositions using parser errors, lint failures, harmonic analysis reports, and beat-level counterpoint diagnostics. Use when an LLM-generated MidGrid passage must be repaired with minimal changes, when a composition loop needs generate-analyze-revise behavior, or when preserving successful material while fixing local defects.
---

# MidGrid Repair Loop

## Workflow

Repair locally and preserve what already works.

1. Prefer recorded examples first: use `python3 midgrid_examples.py --skill midgrid-repair-loop --format markdown` when examples exist; then read `references/repair-patterns.md`; read `references/training-promotion.md` when turning recorded examples into skill material; read `../../midgrid_eval.md` when issue-code semantics are needed.
2. For exercise work, run `python3 midgrid_exercise.py evaluate EXERCISE_ID attempt.midgrid`; otherwise run `python3 midgrid_eval.py passage.midgrid --json --fail-on none`, then separate failures into syntax, species/counterpoint, form, and aesthetic-effect issues.
3. Fix syntax first; do not analyze music that cannot parse.
4. Map each musical issue to beat, voice, and voice pair.
5. Change the smallest region that can fix the issue.
6. Preserve subject entries, cadences, and already-successful counterpoint unless they are the defect.
7. Re-run `midgrid_lint.py` after syntax repair; re-run `midgrid_eval.py` after musical repair and prefer `.report.json` diagnostics when MIDI dependencies are installed.
8. Distill the lesson as an example pair: before, diagnosis, after; for exercise work, save it with `midgrid_exercise.py record`.

## Repair Priorities

1. Parseability.
2. Voice-column consistency.
3. Beat order and duration clarity.
4. Hard counterpoint errors.
5. Form-specific obligations.
6. Aesthetic effect targets.

## Output Pattern

```text
Issues:
- Beat:
  Voice/pair:
  Cause:
  Repair:

Patched MidGrid:
[only the changed passage or full grid, as requested]
```
