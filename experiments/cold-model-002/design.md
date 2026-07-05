# Cold-Model Experiment 002 — Hard Difficulty

Follow-up to 001, testing its registered prediction: at the all-pairs
difficulty where every warm first draft erred, controls should produce
parallels in the least-watched pair, and the curriculum's pair-discipline
material should reduce them.

## Tasks

- **h1**: three-voice first species around the A-minor cantus (V1 middle,
  compose BOTH outer voices; all three pairs carry error-level consonance and
  parallel rules; `tasks/cold2-three-voice-first.json`, strict parallels).
  Reference solution verifies clean; seeded negative (outer-pair parallels,
  each voice clean against the cantus) fails with 3 errors.
- **h2**: free three-voice fugue exposition, D minor, 24 beats, three entries
  (subject alone; answer + countersubject; subject an octave lower under two
  counterpointing voices). Scored by `midgrid_eval.py --strict-parallels`.

## Conditions

Same scaffold as 001. A: format contract only. B adds, for h1: species
example pack + three-voice-species reference; for h2: fugue pack +
exposition-patterns + three-voice pair discipline + recorded
parallel-perfect repairs. Three replicates per cell, twelve agents.
