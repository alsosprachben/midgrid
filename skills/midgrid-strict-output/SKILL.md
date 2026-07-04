---
name: midgrid-strict-output
description: Produce, clean, or constrain parser-valid MidGrid notation for LLM composition workflows. Use when Codex must emit strict .midgrid content, repair invalid note cells, prevent prose or analytical labels inside grid cells, prepare MidGrid for parser/report execution, or enforce spatial voice/time notation before composition analysis.
---

# MidGrid Strict Output

## Workflow

Use MidGrid as a spatial score, not as prose. Keep musical intent in comments or surrounding analysis, and keep grid cells parser-valid.

1. Read `references/midgrid-contract.md` before generating or repairing substantial MidGrid.
2. Choose a fixed voice order and keep the same number of voice columns on every beat row.
3. Use parser-safe metadata only: `#` comments, `# tempo BPM [beat]`, and `// Patch Voice: program`.
4. Emit note cells using only pitches, rests, holds, and canonical suffixes.
5. Put commentary after `//` at the row level, never inside a cell.
6. If the user requests "no commentary", return only the MidGrid block.
7. Validate locally with `python3 midgrid_lint.py input.midgrid`; run `python3 midgrid_parser.py input.midgrid output.mid` when MIDI dependencies are installed.

## Cell Contract

Use these forms:

```text
.
-
C4
C#4
B-3
C4:1
C4@80
C4:1@80
C4:1@80~40
```

Avoid these forms:

```text
(free canon)C4
C4 (suspension)
Bb4
C4@80:1
; section comments inside the grid
```

## Composition Use

When another composition skill asks for MidGrid output, apply this skill first or last:

- First: establish the legal notation surface before composing.
- Last: clean generated music into parseable MidGrid without changing musical intent.
