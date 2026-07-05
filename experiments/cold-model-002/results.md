# Cold-Model Experiment 002 — Results

Run 2026-07-05. Twelve fresh agents, 2 tasks x 2 conditions x 3 replicates.

## Primary result

| task | A (contract only) | B (contract + curriculum) |
|---|---|---|
| h1 three-voice species | 0, 0, 0 errors | 0, 0, 0 errors |
| h2 three-voice exposition | 0, 0, 0 errors | 0, 0, 0 errors |

**The registered prediction failed.** No cold agent produced a single
parallel-perfect error, in any pair, at either task. The only warnings were
the traditional cadence formula (one `direct_perfect` per h1 run, bass
falling a fifth into the final octave — the same one the reference solution
carries). Twelve of twelve structurally correct: three entries, answers at
the fifth, countersubjects present, no crossings.

## The finding hiding under the ceiling: safety, not skill parity

Texture metrics, cold h2 submissions versus the warm expositions (first 24
beats of the four session fugues):

| metric | cold h2 (mean of 6) | warm expositions |
|---|---|---|
| attacks per beat | 2.17 | 1.96 - 2.46 |
| eighth-note attack fraction | 0.09 | 0.14 - 0.40 |
| syncopated attacks (suspension figures) | **0 in all six runs** | up to 14 (Dorian: syncopated CS) |
| distinct durations | 2-3 | 2 |

Every cold agent — condition B included, with suspension chains worked out
in front of it — composed dissonance-minimal counterpoint: quarter-note
homophony-adjacent lines, tenths and sixths, not one suspension attempted in
any free composition. The evaluator cannot fail a piece that never spends
dissonance. In the session's own terms: **the cold agents composed the null
hypothesis** — counterpoint with its content removed, the same music the
dynamic tuner produces by solving dissonance away.

This also relocates the warm-error data: the 2, 2, 2 first-draft errors
never came from expositions either. They came from developments — modulating
episodes, section seams, syncopated countersubjects, four-voice textures at
beats 48-78. Errors are a product of competence times ambition, and one-shot
tasks let cold agents set ambition to zero.

## Conclusions across 001 + 002

1. Machine-scored correctness is at ceiling for this model tier at every
   difficulty poseable as a one-shot task. The curriculum shows no delta on
   correctness because there is no headroom.
2. What actually separates warm from cold is not error rate but **dissonance
   deployment** — willingness to spend suspensions, syncopation, and
   sequences and then survive them. That is an intent, not a rule, and the
   example packs did not transmit it: condition B imitated pack material in
   001 but attempted zero suspensions in free composition here.
3. The curriculum's demonstrated in-session value (repair loop, promoted
   lessons, pair vigilance) operates on errors that only ambitious writing
   produces. Cold agents avoid the regime where it matters.

## Falsifiable follow-up (cold-model-003)

Force the ambition, measure the survival: same exposition task plus a
required dissonance budget ("the countersubject must be syncopated,
carrying a chain of at least three suspensions prepared and resolved by
step"). Prediction: errors finally appear in the control condition —
suspension grammar under multi-voice pressure is where fourth-species
lessons should earn a measurable delta. Alternative axis unchanged from
001: rerun against smaller model tiers.
