# Cold-Model Experiment 001

## Question

Do the curriculum artifacts (example packs from `midgrid_examples.py` plus skill
references) transmit counterpoint competence to a model with no session context?
All prior measurements (first-draft errors 2, 2, 2, 0, 0 across five capstones)
measured the warm collaborator. This measures the curriculum.

## Conditions

Identical scaffold; only materials differ. Prompts frozen verbatim in `materials/`.

- **A (control)**: MidGrid format contract only (`materials/contract.md`).
- **B (curriculum)**: contract + example pack (attempt/diagnosis/correction/lesson)
  + matching reference doc: species pack + first-species ref (t1), species pack +
  fourth-species ref (t2), fugue pack + exposition-patterns ref (t3).

## Tasks (novel material, absent from the repo)

Cantus firmus, A minor, composed for this experiment only:
`A3 C4 B3 D4 C4 E4 D4 B3 C4 B3 A3`

1. **t1**: first species above the cantus (`tasks/cold1-first-species-above.json`).
2. **t2**: fourth species above the cantus (`tasks/cold1-fourth-species-above.json`).
3. **t3**: free two-voice fugue exposition in D minor, 16 beats: subject alone
   (0-7), answer at the fifth + countersubject (8-15).

Reference solutions for t1/t2 verify with zero errors and seeded negatives fail
(harness validity confirmed before launch).

## Protocol

- Cold agents: fresh general-purpose subagents; each may read only its own
  sealed prompt file; novel tasks make repo-peeking moot.
- Phase 1 (primary): one-shot first draft.
- Phase 2 (secondary): each errored run receives its evaluator output verbatim
  and one repair round.
- Scoring: t1/t2 via `midgrid_exercise.py --exercises-dir tasks/ evaluate`
  (strict parallels); t3 via `midgrid_eval.py --strict-parallels` plus a
  structural checklist (subject alone; answer at the fifth, tonal head if
  needed; countersubject present; no crossing).
- Primary metric: mean first-draft error count per cell. Secondary: parse
  failures, repair delta. N=2 per cell; no conclusions where cells overlap
  within one error.

## Run log

Launched 2026-07-05, twelve agents in one parallel batch:

| run | condition file |
|---|---|
| t1-A-1, t1-A-2 | prompt-t1-A.txt |
| t1-B-1, t1-B-2 | prompt-t1-B.txt |
| t2-A-1, t2-A-2 | prompt-t2-A.txt |
| t2-B-1, t2-B-2 | prompt-t2-B.txt |
| t3-A-1, t3-A-2 | prompt-t3-A.txt |
| t3-B-1, t3-B-2 | prompt-t3-B.txt |

Submissions land in `submissions/<run>.midgrid` exactly as returned (code
fences stripped if present); evaluator JSON in `evals/<run>.json`.
