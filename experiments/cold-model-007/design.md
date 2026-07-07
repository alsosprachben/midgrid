# Cold-Model Experiment 007 — Novel Subject, Stratified Exemplar

Two changes over 006, both aimed at the same law (agents compose what
examples show, where they show it):

1. **The exemplar now shows the right thing.** The fugue pack's worked
   countersubject is no longer a 1:1 harmonization: exposition-patterns.md
   and the newly recorded invertible-counterpoint-001 pair teach a
   syncopated-second-species CS in its own rhythmic stratum (co-attack
   0.4), with the OLD harmonized CS preserved as the recorded attempt.
2. **The subject is prescribed and novel** (Ben: "force creativity").
   Every prior B/C/D run transposed the pack's D-minor subject; 007's task
   fixes an 11-note G-minor subject absent from the corpus — rising minor
   sixth head (G4-E-5), stepwise descent, chromatic F#4 mid-subject,
   ending on the third. Agents cannot copy the worked exposition; they
   must apply its pattern to unseen material.

## Conditions

Same scaffold as 004-006; task now includes the subject grid verbatim.
Three replicates each:

- **A — contract only**: `materials/prompt-f-A.txt` (2.6 KB).
- **E — full current bundle**: `materials/prompt-f-E.txt` (114 KB): all
  skills rebuilt from current files (species, fugue-exposition with the
  stratified worked example, harmonic effect, repair loop, figurae with
  strata) plus all three example packs including the
  invertible-counterpoint-001 recording.

## Scoring

Strict + default eval (melodic_fusion + rhythmic_homorhythm), ambition
metrics, motif battery, and the targeted measurements: CS co-attack in
the answer bars (8-16 relative to the first entry), piece homorhythm
mean, syncope count, and subject fidelity (motif echo of the prescribed
subject: the opening entry must score REAL/t=0 against the task grid).

## Registered prediction

E runs state the subject faithfully, derive a legal answer, and write a
countersubject in a different rhythmic stratum (CS co-attack < 0.6 in at
least two of three E runs) with 0 strict errors — the position-matched
exemplar finally transmitting stratification. A controls harmonize
(co-attack ~1.0) and/or fuse directionally, as in every prior control.
Secondary: E keeps unforced suspensions (>= 1 run with syncopes > 0) and
homorhythm mean < 0.8. If E still harmonizes bars 8-15 with the corrected
exemplar in context, position matching is not sufficient either, and the
next probe is a spec-level instruction ("write the CS in second species"),
which 003 showed always works — locating stratification's transmitter
precisely between exemplar and spec.

## Run log

Launched 2026-07-06, six fresh general-purpose agents: f-A-1..3
(prompt-f-A), f-E-1..3 (prompt-f-E). Halves-with-<CONTINUES> delivery
protocol. Submissions land verbatim in `submissions/`; evals in `evals/`.
