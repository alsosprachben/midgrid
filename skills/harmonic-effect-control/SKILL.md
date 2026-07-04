---
name: harmonic-effect-control
description: Use MidGrid harmonic analysis reports to target and revise musical effects such as repose, tension, release, brightness, density, austerity, and contrapuntal clarity. Use when interpreting perceptual_complexity, interval names, phase alignment, or motion fields from MidGrid reports to shape composition choices.
---

# Harmonic Effect Control

## Workflow

Use the report as an effect predictor, not as a complete music judge.

1. Read `references/effect-targets.md` when the task names an aesthetic target or provides a `.report.txt`/`.report.json` report.
2. Prefer `.report.json` for automation; extract beat-level interval class, motion, and perceptual complexity.
3. Summarize each phrase by trend: stable, rising pressure, release, color change, or clutter.
4. Revise MidGrid locally: change the fewest notes needed to produce the intended effect.
5. Re-run `midgrid_exercise.py evaluate`, `midgrid_eval.py`, or the parser/report when available.
6. Preserve strict MidGrid syntax.

## Interpretation

Treat the report as one lens:

- Low complexity can support repose, clarity, or emptiness.
- Moderate imperfect consonance can support flow and warmth.
- High complexity can support pressure, roughness, or expressive color.
- A drop in complexity after a dissonant or dense beat can support release.
- Similar or parallel motion can smooth texture, but perfect parallel motion remains contrapuntally risky.
- Contrary motion often improves independence.

## Output Pattern

When asked to diagnose an effect, respond with:

```text
Target:
Observed report pattern:
Likely heard effect:
Local MidGrid repair:
Expected report change:
```
