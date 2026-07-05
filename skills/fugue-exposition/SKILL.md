---
name: fugue-exposition
description: Compose, inspect, or repair strict MidGrid fugue expositions with subject, answer, countersubject, entry order, tonal answer choices, invertible counterpoint checks, and report-driven revision. Use when building the opening exposition of a fugue or training LLM composition through fugal examples.
---

# Fugue Exposition

## Workflow

Build the exposition as a sequence of visible entries, then test whether the countersubject survives above and below the subject.

1. Read `references/exposition-patterns.md`; for post-exposition work (episodes, stretto), read `references/stretto-and-episodes.md`; for canon, `references/canon-patterns.md`.
2. State the subject in one voice using strict MidGrid.
3. Decide real or tonal answer. Prefer tonal answer when scale-degree 5 to 1 motion would destabilize the key.
4. Add countersubject against the answer.
5. Reuse the countersubject in a different vertical position before trusting it.
6. Fill non-entry voices with rests or simple consonant support until the exposition passes.
7. Check with parser/report and repair beat-local failures.

## Hard Checks

- Every row must remain parser-valid MidGrid.
- Subject entries must be recognizable in the grid.
- Countersubject must be viable above and below the subject or answer.
- Avoid forbidden perfect parallels during entries.
- Keep entries clear enough that the model can see them spatially.
- Delay episode writing until the exposition is stable.

## Output Pattern

For design or diagnosis:

```text
Subject:
Answer:
Entry order:
Countersubject:
MidGrid:
Report concerns:
Repair plan:
```

For notation-only requests, output only the MidGrid.
