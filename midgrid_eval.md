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

`voice_fusion` (default mode): parallel motion across simple-ratio interval classes (unison/octave, fifth, and fourth) reported as a run with start and end beats. This is meta-analysis of the harmonic layer, not a rule: common-fate motion across simple ratios fuses two voices into one perceived stream. That is a defect when it silently costs a voice, and a device when it is a deliberate handoff, doubling, or registration effect. Static doubling (pedal points) is not motion and is never reported. Counterpoint's goal is voice independence; read fusion findings as "here the texture locally has fewer voices than the page says."

`parallel_perfect` (only with `--strict-parallels`): consecutive parallel perfect fifth/octave class in a voice pair, as a categorical error. Classical pedagogy mode, used by the species exercises via `evaluation_defaults.strict_parallels`; deliberately over-constrained for drilling.

`direct_perfect` (only with `--strict-parallels`): similar motion into a perfect fifth/octave class, as a warning.

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
