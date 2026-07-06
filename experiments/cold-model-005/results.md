# Cold-Model Experiment 005 — Results

Run 2026-07-05/06. Nine fresh agents, one-sentence G-minor fugue task
(004-identical), three conditions x 3 replicates. A = contract only;
B = all skills (004's bundle, frozen); C = B + the figurae layer.

## Primary result

| run | strict errors | melodic_fusion regions | attacks/beat | eighth frac | syncopes | economy |
|---|---|---|---|---|---|---|
| f-A-1 | 0 | **3** | 3.32 | 0.51 | 0 | 31% |
| f-A-2 | **4** | 2 | 3.30 | 0.48 | 0 | 36% |
| f-A-3 | 0 | **3** | 3.61 | 0.49 | 0 | 23% |
| f-B-1 | 0 | 0 | 2.60 | 0.24 | 0 | 41% |
| f-B-2 | 0 | 0 | 2.85 | 0.20 | 0 | 26% |
| f-B-3 | 0 | 0 | 2.78 | 0.22 | 0 | 34% |
| f-C-1 | 0 | 0 | 2.71 | 0.24 | **6** | 42% |
| f-C-2 | 0 | 0 | 2.73 | 0.33 | 0 | 41% |
| f-C-3 | 0 | 0 | 2.54 | 0.25 | **2** | 34% |

## The registered prediction, clause by clause

1. **Density (C eighth fraction > 0.30): FAILED.** C sits at B's density
   (0.24/0.33/0.25). The figurae layer did not make cold agents more
   florid; the conservative pack style dominates the surface.
2. **Correctness (0 errors, 0 fusion in C): HELD**, all three runs.
3. **Disposition (>= 1 C run spends an unforced suspension): CONFIRMED,
   2 of 3.** The first unforced dissonance expenditure in the series,
   after zero in fifteen prior cold runs across 001-005 A/B:
   - f-C-1, beats 36.5-39.5: a textbook **7-6 suspension chain** — V0
     attacks off the beat, sustains across each bar into sevenths against
     the descending bass D3-C3-B-2-A2, resolving down by step each time
     (three chained suspensions), exactly the figurae-suspension-weave
     grammar, plus further syncopes at 50-52 and 58.
   - f-C-3, beats 40.5-42.5: chained 4-3 suspensions over the falling
     bass (D4 held into a fourth against A2 resolving to C4, itself held
     into a fourth against G2 resolving to B-3).
   Zero syncopes in every A and B run of both 004 and 005 (12 runs).

So the figurae layer transmitted **the disposition but not the density**:
cold agents given the cell/suspension vocabulary spend real dissonance in
free composition, while keeping the pack's conservative rhythm. The
"warm Bach" combination (A's density at C's discipline) still does not
appear cold.

## Secondary finding: melodic_fusion separates when error counts don't

This round's controls mostly dodged categorical parallels (0, 4, 0 errors
vs 004's 1, 3, 3) — but all three carry sustained melodic-fusion regions
(3, 2, 3), while every B and C run has zero. The directional diagnostic
discriminates the conditions perfectly at N=9 even where the strict rule
has gone quiet: what the controls reliably lack is not parallel-avoidance
but directional independence.

## Structural transfer

All six B/C runs open with the pack subject transposed to G minor (the
004 fingerprint again). f-C-2's first episode (beats 24-29.5) is the
figurae reference's Episode-1 pattern verbatim in structure: the
falling-third cell alternating between V0 and V1, each resting while the
other speaks, over the moving bass. C runs also lead motivic economy
(42/41/34% vs B's 41/26/34% and A's 31/36/23%), weakly suggesting the
cell discipline tightens motivic reuse, though N is far too small.

## Caveats

- f-C-2's delivery was corrupted: the agent recomposed rows 22-31 when
  asked to re-send (its first and second versions of the episode swap the
  voices' roles). The assembled file uses first delivery 0-21.5, re-sent
  22-31, remainder 32-62; the seams parse and evaluate cleanly, but the
  run's scores carry that asterisk. It is also the C run with zero
  syncopes, so the disposition finding does not rest on it.
- N=3 per condition; the density clause failed cleanly, but the
  suspension delta (2/3 vs 0/12) is the kind of small-N qualitative
  signature that wants a replication before strong claims.
- All A runs used empty cells or sharps-spelling variants the lint layer
  tolerates; no parse failures anywhere.

## Conclusion across 004-005

004: skills buy pair-discipline when the spec is silent. 005: the figurae
layer additionally buys dissonance disposition — suspensions finally
appear cold, in the exact grammar the weave lesson recorded — while
density remains the untransmitted residue. Across both experiments the
composite picture of what the curriculum transmits, in order of
robustness: notation (001), form schema (004), pair vigilance /
directional independence (004-005), dissonance disposition (005, partial),
florid density (never). The remaining gap is now precisely characterized:
cold agents will spend dissonance they have a named pattern for, but will
not write more notes than the examples they imitate.

## Artifacts

Submissions (delivery-recovered where noted), evals (strict + default
with melodic_fusion + motif JSONs), renders of the best run per condition
(f-A-3, f-B-2, f-C-1) via the tuning renderer, stretch tuner, HRTF.
