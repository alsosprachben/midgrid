# Cold-Model Experiment 007 — Results

Run 2026-07-06. Novel prescribed subject (absent from corpus), 3 controls
(A, contract only) vs 3 with the full current bundle (E), including the
corrected stratified-countersubject exemplar.

## MODEL CONFOUND (read first)

The session's Fable quota was exhausted midway; the model was switched to
Opus 4.8 to continue. Reconstructed from delivery order:

- **All three A runs completed (both halves) before the switch — fully
  Fable.**
- **Each E run delivered its FIRST HALF on Fable, its remainder on Opus
  4.8.**

Therefore the exposition (bars 0-~37, containing the answer and
countersubject) is **Fable for every run**, and the primary measurement —
countersubject co-attack in bars 8-16 — is a clean Fable-vs-Fable
comparison. Whole-piece metrics for E (total errors, syncopes, homorhythm
mean) mix Fable exposition with Opus development and must not be compared
head-to-head with the all-Fable controls. They are reported below but
flagged.

## Primary result — countersubject stratification in the exposition (all Fable)

| run | CS co-attack (8-16) | subject stated verbatim |
|---|---|---|
| f-A-1 | 1.00 | yes |
| f-A-2 | 0.91 | yes |
| f-A-3 | 0.91 | yes |
| f-E-1 | **0.50** | yes |
| f-E-2 | **0.70** | yes |
| f-E-3 | **0.78** | yes |

**Every E countersubject is more rhythmically independent than every A
countersubject; the two conditions do not overlap.** All six runs state
the novel subject exactly (subject fidelity is the controlled variable,
not the discriminator). The controls harmonize the answer note-for-note
(co-attack ~0.9-1.0) exactly as in 004-006; the bundle runs put the
countersubject on the off-beats, holding across the answer's attacks —
the syncopated-second-species pattern from the corrected
invertible-counterpoint-001 exemplar, applied to a subject none of them
had seen.

This is the 006 law confirmed by construction: 006 showed cold agents copy
the worked exposition's countersubject verbatim at bars 8-15 regardless of
adjacent rules; 007 changed only that one exemplar, and the behavior at
exactly that position flipped. **The transmitter of stratification is the
position-matched exemplar.** The registered strict threshold ("co-attack
< 0.6 in >= 2 of 3") was optimistic — only f-E-1 cleared 0.6 — but the
directional prediction (every E below every A) held completely.

## Whole-piece metrics (E development is Opus — flagged, not comparable)

| run | strict errors | melodic_fusion | homorhythm mean | syncopes | model (dev) |
|---|---|---|---|---|---|
| f-A-1 | 4 | 2 | 1.00 | 0 | Fable |
| f-A-2 | 4 | 1 | 1.00 | 0 | Fable |
| f-A-3 | 2 | 2 | 0.78 | 0 | Fable |
| f-E-1 | 0 | 0 | 0.19 | 40 | Opus |
| f-E-2 | 1 | 2 | 0.53 | 10 | Opus |
| f-E-3 | 10 | 1 | 0.62 | 4 | Opus |

Observations, all caveated by the confound:

- f-E-1 is the strongest stratified fugue in the whole series (homorhythm
  0.19, the corpus minimum; zero errors; zero fusion) — but its
  development is Opus, so this cannot be read as a pure Fable capability.
- f-E-3 stratified the exposition (Fable, co-attack 0.78) yet carries 10
  strict parallels — the competence x ambition tax of 002 resurfacing:
  rhythmically independent writing opens far more parallel-perfect
  opportunities than lockstep harmonization does. Whether the errors are
  Fable's or Opus's is confounded (most fall in the development).
- Controls remain the clean anchor: 4/4/2 errors, fusion everywhere, zero
  syncopes, homorhythm ~1.0 — the harmonizing default, fully Fable, on the
  novel subject. The novel subject did not by itself induce stratification.

## Conclusion

The one clean, uncontaminated finding is decisive: **the exposition
countersubject stratified in all three bundle runs and none of the three
controls, on unseen material, with the only relevant change being the
corrected worked exemplar.** This closes the arc 004-007: the curriculum
transmits behavior through position-matched examples, and the country-song
countersubject — traced back to a flaw in one hand-written exemplar — is
fixed at the source. The development-phase quality question (does the
stratified texture survive a full fugue without the error inflation of
f-E-3) needs a clean rerun on a single model tier.

## Next

Rerun 007 with model pinned (no mid-run switch) to de-confound the
whole-piece metrics, and add a strict-parallel repair pass to test whether
the competence x ambition errors of f-E-3 are one-repair-round fixable
(the 001-003 repair-loop claim, never yet exercised on a stratified
texture).

## Artifacts

Submissions in `submissions/` (E remainders Opus-generated, noted),
strict + default evals in `evals/`, prompts frozen in `materials/`.
