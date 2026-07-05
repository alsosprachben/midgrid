# Cold-Model Experiment 004 — Results

Run 2026-07-04/05. Six fresh agents, one-sentence task ("compose a complete
fugue in G minor for three voices... make it as good a fugue as you can"),
no contrapuntal constraints in the prompt. A = format contract only (2.3 KB);
B = contract + all skills (84 KB). Full protocol in `design.md`.

## Primary result — the first non-null of the series

| run | strict errors | where | default-mode fusion warnings |
|---|---|---|---|
| f-A-1 | **1** | parallel_perfect V0-V2 @ 51.5 | 0 (1 displaced_root_motion) |
| f-A-2 | **3** | parallel_perfect V0-V2 @ 40.0, 52.5, 53.0 | 2 |
| f-A-3 | **3** | parallel_perfect V0-V1 @ 20.0; voice_crossing @ 20.0, 23.0 | 1 |
| f-B-1 | **0** | — | 0 |
| f-B-2 | **0** | — | 0 |
| f-B-3 | **0** | — | 0 |

Controls: 7 errors across 3 runs, every run errs. Skills: 0 across 3 runs.
**The registered prediction finally held**: five of six control parallels
land in V0-V2, the least-watched outer pair — the exact warm-session failure
mode (the sixth is a V0-V1 parallel plus two crossings). The fusion
meta-analysis confirms independently: control parallels register as
voice_fusion warnings in default mode; no B run triggers fusion at all.

## Why 004 discriminated where 001-003 could not

001-003 put the constraints in the task spec, and the spec was a complete
transmitter. 004's task is one sentence; the only place contrapuntal
knowledge could come from was the base model's disposition (A) or the skills
(B). With no spec to lean on, the controls composed ambitious textures and
slipped in exactly the regime the warm data predicted (long pieces, all-pairs
vigilance, outer pair least watched); every skills run stayed clean.

## Ambition control — clean is not empty, but style transferred

| run | length | attacks/beat | eighth frac | syncopes | ndur |
|---|---|---|---|---|---|
| f-A-1 | 70 | 4.10 | 0.71 | 0 | 3 |
| f-A-2 | 71 | 3.23 | 0.51 | 0 | 5 |
| f-A-3 | 73 | 3.14 | 0.29 | 0 | 4 |
| f-B-1 | 61 | 2.52 | 0.22 | 0 | 5 |
| f-B-2 | 67 | 2.58 | 0.22 | 0 | 4 |
| f-B-3 | 58 | 2.69 | 0.22 | 0 | 5 |

Two honest observations cut both ways:

1. **B runs are less florid** (apb ~2.6 vs 3.1-4.1; eighth fraction 0.22 vs
   0.29-0.71). The skills condition wrote in the quarter-note-leaning style
   of the pack examples. Part of the B error advantage is disposition — the
   curriculum transmitted a more conservative, survivable texture, not just
   vigilance. That is itself a transmission (002 showed cold agents default
   to safety only when the task is a drill; here the task said "as good a
   fugue as you can" and B still chose the pack's texture).
2. **Zero syncopes in all six.** Consistent with 002: no cold agent spends
   suspensions unprompted, skills or not. The dissonance-first disposition
   still does not transmit by example; it lives in the spec (003) or in the
   warm collaboration.

## Curriculum fingerprint

All three B runs open with the pack's worked D-minor exposition subject
transposed to G minor (G D B-flat-A G F-sharp G-A B-flat A) — direct
evidence the skills material was read and used, not merely carried. B runs
also reproduce pack structure: tonal answers, countersubject reuse, episodes
by sequence, middle entries in relative/subdominant regions, dominant pedal
(f-B-1: G2:8), Picardy closes. Controls invented their own subjects and
still built real fugues (expositions, episodes, middle entries in B-flat
and C minor, stretto gestures, Picardy) — structure was never the missing
piece; pair-discipline under ambition was.

## Conclusion across 001-004

- 001-003: when the task spec carries the constraints, the spec is a
  complete transmitter and the curriculum shows no delta.
- 004: when the spec carries nothing, the curriculum is worth roughly
  2.3 strict errors per fugue at this length — all of them the
  least-watched-pair parallels the warm sessions kept finding — plus a
  transmitted compositional style.

So the two artifacts of this project divide the labor: the **evaluator and
constraint vocabulary** transmit correctness when you can afford to spell
the task out; the **skills** transmit it when you cannot. The remaining gap
(no cold agent, either condition, ever spends a suspension unforced) is the
dissonance-disposition problem — per the session thesis, that is the actual
content of counterpoint, and it still only appears on demand.

## Artifacts

- Submissions: `submissions/f-{A,B}-{1,2,3}.midgrid` (A-1 and B-2 recovered
  from truncated deliveries by resend; spliced verbatim).
- Evals: `evals/*.json` (strict) and `evals/*.default.json` (fusion mode).
- Ambition: `score_ambition.py`.
- Renders for judgment by ear: best of each condition (f-A-1, f-B-1) via
  the tuning renderer, stretch tuner, HRTF on.
