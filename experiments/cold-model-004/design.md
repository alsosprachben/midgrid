# Cold-Model Experiment 004 — The Full-Fugue Null Test

Ben's proposal, verbatim intent: "Ask for a full fugue with only the midgrid
skill. Then ask for a full fugue with all of the skills."

001-003 converged on: specification language is the complete transmitter at
this model tier; when the task prompt spells out the constraints, controls
match curriculum. 004 removes the spec crutch. The task is one sentence with
no contrapuntal constraints at all — so anything condition B does better is
purely what the skills add when nobody tells the model what counterpoint is.

## Conditions

Identical scaffold (work only from this message; return only MidGrid text
starting `# Title:`; no code fences) and identical task line:

> Compose a complete fugue in G minor for three voices, roughly 60 to 90
> beats, tempo 80, three columns (V0 high, V1 middle, V2 low). Make it as
> good a fugue as you can.

- **A — contract only** (`materials/prompt-f-A.txt`, 2.3 KB): the MidGrid
  format contract, nothing about counterpoint.
- **B — all skills** (`materials/prompt-f-B.txt`, 84 KB): contract + every
  skill in the repo: species SKILL + curriculum + first/second/third/fourth/
  fifth/three-voice references, fugue-exposition SKILL + exposition-patterns
  + stretto-and-episodes + canon-patterns, harmonic-effect-control +
  effect-targets, repair-loop + repair-patterns, and both example packs.

Three replicates per condition, six fresh general-purpose agents.

## Scoring

Error count alone saturated in 001-003, so scoring is multi-dimensional:

1. `midgrid_eval.py --strict-parallels` (comparable to the warm 2,2,2,0,0
   baseline) and default voice-fusion mode.
2. Ambition metrics (`score_ambition.py`): attacks/beat, eighth-note attack
   fraction, syncopated attacks, distinct durations, length. Guards against
   "clean because empty" — a condition that wins on errors by writing the
   null hypothesis doesn't win.
3. Structural checklist: exposition order, tonal answer, countersubject
   reuse, episodes, middle entries, stretto/pedal, final cadence.
4. Renders of the best run per condition for judgment by ear.

## Registered prediction

Controls will err in the least-watched pair (V0-V2) once length and texture
force the all-pairs regime — the warm-session failure mode — while
condition-B runs stay clean at comparable ambition, because the skills
install pair vigilance and repair habits that one-sentence tasks don't.

## Run log

Launched 2026-07-04/05, six agents in parallel:

| run | agent | prompt | delivery |
|---|---|---|---|
| f-A-1 | ae3806eb9d90458e5 | prompt-f-A.txt | truncated twice; recovered in two halves via resend protocol |
| f-A-2 | ae16e3a9a89a65bae | prompt-f-A.txt | clean |
| f-A-3 | a84272b5ce8edf96e | prompt-f-A.txt | (pending at time of writing) |
| f-B-1 | ad0a4844522c20d56 | prompt-f-B.txt | clean |
| f-B-2 | a48e4f3def2f35187 | prompt-f-B.txt | truncated (head missing); recovered via resend |
| f-B-3 | acd65346d1dc649e0 | prompt-f-B.txt | clean |

Truncation is a delivery-channel artifact (long single messages), not a
composition failure; recovered text is spliced verbatim, no notes altered.
