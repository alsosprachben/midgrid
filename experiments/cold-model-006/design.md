# Cold-Model Experiment 006 — The Stratification Test

Ben's diagnosis after hearing 005: the countersubjects are "almost always
simpler harmonizations, rather than half or double speed counter-melodies
... like a country song." Measurement agreed brutally: co-attack rate in
the answer+CS bars is 89-100% everywhere in the corpus except the warm
D-dorian fugue (12%, syncopated CS); piece-level homorhythm means are
0.86-0.97 for the cold pack-style runs against 0.51-0.70 for the warm
stratified fugues. The missing dimension is rate stratification — the
Contrapunctus IX regime (running eighths against the theme in
augmentation). 006 tests whether the new strata layer transmits it.

## Conditions

Same one-sentence G-minor fugue task as 004/005, three replicates each:

- **C — figurae (005)**: `materials/prompt-f-C.txt`, byte-identical to
  005's (102 KB). Baseline: transmits suspensions but not strata.
- **D — figurae + strata**: `materials/prompt-f-D.txt` (107 KB): the same
  assembly from the current files — figurae SKILL with rule 3b
  (stratification), the reference with section 11 (Contrapunctus IX rule,
  harmonized/stratified worked pair), and the pack now including the
  recorded figurae-strata-004 lesson.

Delivery protocol from 005 (halves with <CONTINUES>) retained.

## Scoring

Strict + default eval (now including `rhythmic_homorhythm`), ambition
metrics, motif battery (echoes, economy, melodic fusion, homorhythm
fractions), and the targeted measurement: co-attack fraction in the
answer+countersubject bars (8-16) plus piece-level homorhythm mean.

## Registered prediction

D runs drop piece-level homorhythm mean below 0.8 (C's 005 values: 0.84,
0.62, 0.58 — wait, C already moved; the sharper target is the CS bars)
and, specifically, the answer+CS co-attack fraction falls below 0.6 in at
least two D runs (all six 004/005 B/C runs sit at ~1.0), via a
countersubject at double speed or in syncopation — while keeping 0 strict
errors and 0 melodic-fusion regions. Density should finally move too:
a double-speed CS forces eighth fraction above 0.30 in D. If D instead
reproduces the pack's homorhythmic exposition, the exemplar's gravity
beats the named rule, and the next iteration must re-record the worked
exposition itself with a stratified CS.

## Run log

Launched 2026-07-06, six fresh general-purpose agents:
f-C-1..3 (prompt-f-C), f-D-1..3 (prompt-f-D). Submissions land verbatim
in `submissions/`; evals in `evals/`.
