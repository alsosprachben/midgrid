# Cold-Model Experiment 001 — Results

Run 2026-07-05. Twelve fresh agents (no session context), 3 tasks x 2 conditions
x 2 replicates. Protocol and frozen materials in `design.md` / `materials/`.

## Primary result

| task | A (contract only) | B (contract + curriculum) |
|---|---|---|
| t1 first species | 0, 0 errors | 0, 0 errors |
| t2 fourth species | 0, 0 errors | 0, 0 errors |
| t3 free exposition | 0, 0 errors | 0, 0 errors |

Lint: 0 errors in all 12 (one control run used empty cells instead of '.',
drawing style warnings only). Phase 2 (repair round) was moot: no run had
anything to repair.

**The machine-scored metric is a null result: at these task sizes, the base
model is at ceiling cold, control condition included.**

## Secondary observations

- The format contract alone fully transmits MidGrid syntax: every submission
  parsed, respected the seed lattice, and used '-' holds correctly, including
  the syncopated fourth-species lattice.
- Fourth-species suspension grammar is present in the base model without the
  curriculum: both control runs chained genuine suspensions (sevenths and
  fourths struck on downbeats, each resolving down by step) and cadenced with
  G# as instructed.
- Structural checklist on the expositions tied exactly: 3.75/4 mean per
  condition. The single best submission (explicit tonal answer, C# cadence,
  full close) was a CONTROL run.
- Curriculum influence is visible qualitatively but not in scores: the B
  expositions echo the pack's worked D-minor exposition (one subject nearly
  quotes it). Imitation happened; it was not needed for correctness.

## Interpretation

This experiment does not show the curriculum is worthless; it shows the tasks
were too easy to discriminate at this model tier. The warm-session error data
(2, 2, 2 first-draft parallels) all came from three- and four-voice textures
of 67-131 beats, where the voice-pair count and long-range form create the
failure surface. The cold tasks were two-voice and 11-16 beats — below the
difficulty where errors ever occurred, even warm.

Two falsifiable follow-ups for cold-model-002:

1. **Harder tasks, same model**: three- or four-voice texture at 24+ beats
   (the all-pairs regime where every warm first draft erred). Prediction from
   this session's data: controls will produce parallels in the least-watched
   pair; the curriculum's pair-discipline and fusion lessons should reduce
   them.
2. **Same tasks, smaller models**: run the identical frozen prompts against
   smaller model tiers (the Agent tool supports model override). The
   curriculum plausibly matters most where base competence is weakest; that is
   also the realistic deployment target for training material.

Caveats: N=2 per cell; agents share the base model of the session author, so
this measures "does this model tier need the curriculum for small tasks"
(answer: no) rather than curriculum value in general.
