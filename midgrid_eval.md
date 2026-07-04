# MidGrid Evaluation Diagnostics

`midgrid_eval.py` is the deterministic critic for composition loops. It runs strict syntax linting, invokes `midgrid_parser.py`, reads `.report.json`, and emits repair-oriented diagnostics.

## Usage

```bash
python3 midgrid_eval.py piece.midgrid --fail-on none
python3 midgrid_eval.py piece.midgrid --json --write-json piece.eval.json
```

By default, generated MIDI and reports are written under `/tmp` using the input stem, for example:

```text
/tmp/piece.mid
/tmp/piece.report.txt
/tmp/piece.report.json
```

Use `--midi-out path/to/piece.mid` to choose another output location.

## JSON Schema

The evaluator writes schema `midgrid.eval.v1`:

```json
{
  "schema": "midgrid.eval.v1",
  "input": "piece.midgrid",
  "lint": {
    "ok": true,
    "errors": [],
    "warnings": []
  },
  "parser": {
    "ok": true,
    "returncode": 0,
    "stdout": "...",
    "stderr": "",
    "midi_out": "/tmp/piece.mid",
    "report_text": "/tmp/piece.report.txt",
    "report_json": "/tmp/piece.report.json"
  },
  "report_summary": {
    "beat_count": 8,
    "active_pair_count": 8,
    "rest_pair_count": 0,
    "motion_counts": {"parallel": 1},
    "mean_perceptual_complexity": 7.0,
    "max_perceptual_complexity": 77.0,
    "max_perceptual_complexity_pair": {
      "beat": 4.0,
      "voice_pair": "V0-V1",
      "perceptual_complexity": 77.0,
      "interval": "Tritone"
    }
  },
  "issues": [
    {
      "severity": "error",
      "code": "parallel_perfect",
      "message": "Parallel perfect interval in V0-V1 from beat 0 to 1.",
      "beat": 1.0,
      "previous_beat": 0.0,
      "voice_pair": "V0-V1"
    }
  ],
  "issue_counts": {
    "error": 1,
    "warning": 0,
    "info": 0
  }
}
```

## Issue Codes

`parse_failed`: parser failed or did not produce a JSON report.

`parallel_perfect`: consecutive parallel perfect fifth/octave class in a voice pair. Treat as a hard counterpoint error unless the style explicitly allows it.

`direct_perfect`: similar motion into a perfect fifth/octave class. Treat as a warning; inspect melodic context before repair.

`voice_crossing`: an earlier voice column sounds below a later voice column, assuming top-to-bottom voice ordering.

`high_complexity`: a voice pair reaches or exceeds `--high-complexity-threshold`.

`wide_adjacent_spacing`: adjacent voice columns exceed `--wide-spacing-threshold` semitones.

## Repair Loop Use

1. Run `midgrid_eval.py draft.midgrid --json --fail-on none`.
2. Fix `lint.errors` first.
3. Fix `parse_failed` before musical issues.
4. Group `issues` by `beat` and `voice_pair`.
5. Patch the smallest MidGrid region that resolves the issue.
6. Re-run the evaluator and preserve improvements.
