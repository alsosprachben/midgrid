# Cold-Model Experiment 005 — The Figurae Transmission Test

004 left both conditions short of the target: controls florid but fused,
all-skills clean but rhythmically conservative (2.5 attacks/beat, eighth
fraction 0.22), zero unforced suspensions anywhere in the series. The
figurae layer (skills/figurae/) teaches directional cells with metric
placement — the claimed mechanism for florid-AND-independent writing and
for spending dissonance on purpose. 005 measures whether that layer
transmits, holding everything else identical to 004.

## Conditions

Same one-sentence task as 004, verbatim; three replicates each:

- **A — contract only**: `materials/prompt-f-A.txt`, byte-identical to 004
  (2.3 KB). Fresh baseline.
- **B — all skills (004)**: `materials/prompt-f-B.txt`, byte-identical to
  004 (84 KB).
- **C — all skills + figurae**: `materials/prompt-f-C.txt` (102 KB): B's
  content with the figurae SKILL.md, figurae-patterns.md reference, and
  the figurae example pack (three recorded attempt/correction lessons)
  inserted before the task line.

Delivery change from 004 (mechanics only, not materials): the agent
wrapper prompt now instructs long pieces to arrive in halves with a
`<CONTINUES>` marker, to avoid the truncated-message recoveries 004
needed.

## Scoring

1. `midgrid_eval.py --strict-parallels` and default mode (now including
   the `melodic_fusion` directional diagnostic).
2. Ambition metrics: attacks/beat, eighth-note fraction, syncopated
   attacks, distinct durations, length.
3. `midgrid_motif.py`: echo table, motivic economy, fusion regions.
4. Structural checklist and, at the end, renders of the best run per
   condition.

## Registered prediction

C runs exceed B's density (eighth-note fraction > 0.30, approaching
control levels) while keeping 0 strict errors and 0 melodic-fusion
regions, and at least one C run spends an unforced suspension
(syncopes > 0) — the first cold appearance of the dissonance disposition
in the series. If C stays as conservative as B, the figurae layer
transmits vocabulary but not disposition, and the write-up will say so.

## Run log

Launched 2026-07-05, nine fresh general-purpose agents in one batch:
f-A-1..3 (prompt-f-A), f-B-1..3 (prompt-f-B), f-C-1..3 (prompt-f-C).
Submissions land in `submissions/<run>.midgrid` exactly as returned;
evaluator JSON in `evals/`.
