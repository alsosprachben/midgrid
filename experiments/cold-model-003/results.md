# Cold-Model Experiment 003 — Results

Run 2026-07-05. Eight fresh agents, one task (three-voice exposition with a
MANDATORY syncopated countersubject carrying at least three suspensions),
2 conditions x 4 replicates. Suspension grammar scored by a deterministic
checker (`check_suspensions.py`) calibrated against the warm ground truth
(it finds exactly the three suspensions in the D Dorian fugue's
countersubject).

## Primary result

| run | eval errors | valid suspensions | grammar violations | budget met |
|---|---|---|---|---|
| A-1 | 0 | 4 | 0 | yes |
| A-2 | 0 | 4 | 0 | yes |
| A-3 | 0 | 3 | 0 | yes |
| A-4 | 0 | 4 | 0 | yes |
| B-1 | 0 | 5 | 0 | yes |
| B-2 | 0 | 3 | 0 | yes |
| B-3 | 0 | 4 | 0 | yes |
| B-4 | 0 | 5 | 0 | yes |

**The registered prediction failed again.** Forced to spend dissonance,
every control executed suspension grammar flawlessly: chains of ninths (or
close-position seconds) prepared as consonances and resolved down by step,
several exceeding the warm capstone's own three. One control derived the
real-answer rule unprompted ("opens 1-3 so real answer applies"); another
annotated its suspension plan in comments. B runs average marginally more
suspensions (4.25 vs 3.75) - within noise at this N.

## Synthesis across experiments 001-003

1. **001**: cold agents at ceiling on two-voice drills; the format contract
   alone transmits the notation.
2. **002**: cold agents at ceiling on hard-legality tasks - by writing
   dissonance-free music (zero syncopes in six free expositions). The
   curriculum does not change default disposition.
3. **003**: when the task SPEC demands dissonance, cold agents execute the
   full grammar with zero training examples.

The conclusion the three failures converge on: at this model tier, neither
capability nor knowledge was ever missing. **The governing variable is the
specification.** A precisely worded constraint ("attacked on the half-beat,
sustained across the downbeat, dissonant, prepared as a consonance,
resolved down by step, at least three") is a complete transmitter, exactly
as the format contract was in 001. The example packs are redundant with
explicit constraints plus base competence.

What the session's apparatus actually produced, then, is not primarily
training material - it is the **machine-checkable specification language**
of this counterpoint practice: the evaluator, the exercise checks, the
fusion and displaced-root meta-analysis, and the precise constraint
vocabulary the task prompts borrowed. The curriculum compiles to the spec.
The warm-session improvement curve (2, 2, 2, 0, 0) is better read as the
spec being internalized and sharpened than as example-driven learning.

The dissonance-first thesis survives intact and sharpened: 002 showed that
by default a correctness-optimizing composer writes the null hypothesis
(counterpoint with its content removed); 003 shows dissonance appears
exactly when demanded, with full grammar. Disposition is a prompt variable,
not a knowledge variable.

## Remaining open axis

Smaller model tiers, where base competence thins and worked examples may
stop being redundant - the one place the packs' training-material claim is
still falsifiable. The frozen prompts from all three experiments rerun
unchanged with a model override.
