#!/usr/bin/env python3
"""Evaluate MidGrid files for syntax, parser success, and repair-loop diagnostics."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from midgrid_lint import lint_text

PERFECT_CLASSES = {0, 7}

# Simple-ratio interval classes (unison/octave 1:1/1:2, fifth 2:3, fourth 3:4).
# Parallel motion across these fuses two voices into one perceived stream:
# the meta-analysis reports that fusion instead of enforcing a rule, since
# fusion is sometimes the intent (voice handoffs, registration doubling).
FUSABLE_CLASSES = {0, 5, 7}


def report_path_with_suffix(mid_path: Path, suffix: str) -> Path:
    if mid_path.name.endswith(".mid"):
        return mid_path.with_name(mid_path.name[:-4] + suffix)
    return mid_path.with_name(mid_path.name + suffix)


def finding_dict(finding: Any) -> dict[str, Any]:
    return finding.as_dict() if hasattr(finding, "as_dict") else dict(finding)


def run_lint(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    errors, warnings = lint_text(text, str(path))
    return {
        "ok": not errors,
        "errors": [finding_dict(finding) for finding in errors],
        "warnings": [finding_dict(finding) for finding in warnings],
    }


def run_parser(input_path: Path, midi_out: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "midgrid_parser.py", str(input_path), str(midi_out)],
        cwd=Path(__file__).resolve().parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    report_json = report_path_with_suffix(midi_out, ".report.json")
    report_text = report_path_with_suffix(midi_out, ".report.txt")
    return {
        "ok": proc.returncode == 0 and report_json.exists(),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "midi_out": str(midi_out),
        "report_text": str(report_text) if report_text.exists() else None,
        "report_json": str(report_json) if report_json.exists() else None,
    }


def issue(severity: str, code: str, message: str, **fields: Any) -> dict[str, Any]:
    data = {"severity": severity, "code": code, "message": message}
    data.update(fields)
    return data


def pair_map(beat: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {pair["voice_pair"]: pair for pair in beat.get("pairs", [])}


def interval_class(pair: dict[str, Any]) -> int | None:
    interval = pair.get("interval_semitones")
    if interval is None:
        return None
    return interval % 12


def detect_parallel_and_direct_perfects(report: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    beats = report.get("beats", [])
    previous_by_pair: dict[str, dict[str, Any]] = {}
    previous_beat_by_pair: dict[str, float] = {}

    for beat in beats:
        current_beat = beat["beat"]
        for pair in beat.get("pairs", []):
            label = pair["voice_pair"]
            prev = previous_by_pair.get(label)
            if prev is None:
                previous_by_pair[label] = pair
                previous_beat_by_pair[label] = current_beat
                continue

            prev_class = interval_class(prev)
            cur_class = interval_class(pair)
            if prev_class in PERFECT_CLASSES and cur_class in PERFECT_CLASSES:
                if pair.get("motion") == "parallel" and prev_class == cur_class:
                    issues.append(issue(
                        "error",
                        "parallel_perfect",
                        f"Parallel perfect interval in {label} from beat {previous_beat_by_pair[label]:g} to {current_beat:g}.",
                        beat=current_beat,
                        previous_beat=previous_beat_by_pair[label],
                        voice_pair=label,
                        previous_interval=prev.get("interval"),
                        interval=pair.get("interval"),
                    ))
                elif pair.get("motion") == "similar":
                    issues.append(issue(
                        "warning",
                        "direct_perfect",
                        f"Similar motion into a perfect interval in {label} at beat {current_beat:g}.",
                        beat=current_beat,
                        previous_beat=previous_beat_by_pair[label],
                        voice_pair=label,
                        previous_interval=prev.get("interval"),
                        interval=pair.get("interval"),
                    ))

            previous_by_pair[label] = pair
            previous_beat_by_pair[label] = current_beat
    return issues


def detect_voice_fusion(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Meta-analysis of the harmonic report: common-fate motion across
    simple-ratio intervals collapses two voices into one perceived stream.

    A fusion transition is parallel motion (equal, nonzero pitch deltas)
    where both sonorities sit in FUSABLE_CLASSES. Consecutive transitions
    merge into one reported run. Static doubling (pedal points, drones) is
    not motion and is not reported."""
    issues = []
    beats = report.get("beats", [])
    previous_by_pair: dict[str, dict[str, Any]] = {}
    previous_beat_by_pair: dict[str, float] = {}
    previous_midis: list[Any] = []
    runs: dict[str, dict[str, Any]] = {}

    def flush(label: str) -> None:
        run = runs.pop(label, None)
        if run is None:
            return
        beats_span = f"beat {run['start']:g} to {run['end']:g}"
        issues.append(issue(
            "warning",
            "voice_fusion",
            f"{label} move in parallel {run['intervals']} from {beats_span}: "
            f"common-fate motion across simple ratios fuses the voices into one stream "
            f"({run['transitions']} transition{'s' if run['transitions'] > 1 else ''}). "
            f"Legitimate as a deliberate handoff or doubling; otherwise restore "
            f"independence with contrary or oblique motion.",
            beat=run["end"],
            start_beat=run["start"],
            voice_pair=label,
            transitions=run["transitions"],
        ))

    for beat in beats:
        current_beat = beat["beat"]
        midis = beat.get("sounding_midis", [])
        for pair in beat.get("pairs", []):
            label = pair["voice_pair"]
            prev = previous_by_pair.get(label)
            if prev is not None:
                prev_class = interval_class(prev)
                cur_class = interval_class(pair)
                moving = False
                try:
                    hi, lo = (int(label[1]), int(label[4]))
                    d_hi = midis[hi] - previous_midis[hi]
                    moving = d_hi != 0
                except (TypeError, ValueError, IndexError):
                    moving = pair.get("motion") == "parallel"
                fused = (
                    pair.get("motion") == "parallel"
                    and moving
                    and prev_class in FUSABLE_CLASSES
                    and cur_class in FUSABLE_CLASSES
                )
                if fused:
                    run = runs.get(label)
                    if run is None:
                        runs[label] = {
                            "start": previous_beat_by_pair[label],
                            "end": current_beat,
                            "transitions": 1,
                            "intervals": pair.get("interval", "perfect intervals"),
                        }
                    else:
                        run["end"] = current_beat
                        run["transitions"] += 1
                else:
                    flush(label)
            previous_by_pair[label] = pair
            previous_beat_by_pair[label] = current_beat
        previous_midis = midis

    for label in list(runs):
        flush(label)
    return issues


def detect_voice_crossing(report: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    for beat in report.get("beats", []):
        sounding = beat.get("sounding_midis", [])
        for upper_idx in range(len(sounding)):
            upper = sounding[upper_idx]
            if upper is None:
                continue
            for lower_idx in range(upper_idx + 1, len(sounding)):
                lower = sounding[lower_idx]
                if lower is None:
                    continue
                if upper < lower:
                    issues.append(issue(
                        "error",
                        "voice_crossing",
                        f"V{upper_idx} sounds below V{lower_idx} at beat {beat['beat']:g}.",
                        beat=beat["beat"],
                        voices=[upper_idx, lower_idx],
                        midis=[upper, lower],
                    ))
    return issues


def detect_high_complexity(report: dict[str, Any], threshold: float) -> list[dict[str, Any]]:
    issues = []
    for beat in report.get("beats", []):
        for pair in beat.get("pairs", []):
            pscore = pair.get("perceptual_complexity")
            if pscore is not None and pscore >= threshold:
                issues.append(issue(
                    "warning",
                    "high_complexity",
                    f"{pair['voice_pair']} reaches perceptual complexity {pscore:g} at beat {beat['beat']:g}.",
                    beat=beat["beat"],
                    voice_pair=pair["voice_pair"],
                    interval=pair.get("interval"),
                    perceptual_complexity=pscore,
                    threshold=threshold,
                ))
    return issues


def detect_wide_adjacent_spacing(report: dict[str, Any], threshold: int) -> list[dict[str, Any]]:
    issues = []
    for beat in report.get("beats", []):
        for pair in beat.get("pairs", []):
            voices = pair.get("voices", [])
            interval = pair.get("interval_semitones")
            if len(voices) == 2 and voices[1] == voices[0] + 1 and interval is not None and interval > threshold:
                issues.append(issue(
                    "warning",
                    "wide_adjacent_spacing",
                    f"Adjacent voices {pair['voice_pair']} are {interval} semitones apart at beat {beat['beat']:g}.",
                    beat=beat["beat"],
                    voice_pair=pair["voice_pair"],
                    interval_semitones=interval,
                    threshold=threshold,
                ))
    return issues


def evaluate_report(report: dict[str, Any], high_complexity_threshold: float, wide_spacing_threshold: int,
                    strict_parallels: bool = False) -> list[dict[str, Any]]:
    issues = []
    if strict_parallels:
        # Classical pedagogy mode (species drills): categorical prohibitions.
        issues.extend(detect_parallel_and_direct_perfects(report))
    else:
        # Default: intervallic findings are meta-analysis of the harmonic
        # layer. Parallel perfects are reported as stream fusion, which may
        # be intentional; nothing intervallic is an error by category.
        issues.extend(detect_voice_fusion(report))
    issues.extend(detect_voice_crossing(report))
    issues.extend(detect_high_complexity(report, high_complexity_threshold))
    issues.extend(detect_wide_adjacent_spacing(report, wide_spacing_threshold))
    return issues


def count_by_severity(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"error": 0, "warning": 0, "info": 0}
    for item in issues:
        severity = item.get("severity", "info")
        counts[severity] = counts.get(severity, 0) + 1
    return counts


def render_text(result: dict[str, Any]) -> str:
    lines = []
    lines.append(f"Input: {result['input']}")
    lint = result["lint"]
    lines.append(f"Lint: {len(lint['errors'])} errors, {len(lint['warnings'])} warnings")

    parser = result.get("parser")
    if parser:
        lines.append(f"Parser: {'ok' if parser['ok'] else 'failed'}")
        if parser.get("report_json"):
            lines.append(f"Report JSON: {parser['report_json']}")

    summary = result.get("report_summary")
    if summary:
        lines.append(
            "Summary: "
            f"beats={summary['beat_count']}, "
            f"mean_complexity={summary['mean_perceptual_complexity']}, "
            f"max_complexity={summary['max_perceptual_complexity']}"
        )

    issues = result.get("issues", [])
    lines.append(f"Issues: {len(issues)}")
    for item in issues:
        location = []
        if "beat" in item:
            location.append(f"beat {item['beat']:g}")
        if "voice_pair" in item:
            location.append(item["voice_pair"])
        elif "voices" in item:
            location.append("V" + "-V".join(str(v) for v in item["voices"]))
        loc = f" ({', '.join(location)})" if location else ""
        lines.append(f"- {item['severity']} {item['code']}{loc}: {item['message']}")
    return "\n".join(lines)


def should_fail(result: dict[str, Any], fail_on: str) -> bool:
    if fail_on == "none":
        return False
    if result["lint"]["errors"]:
        return True
    parser = result.get("parser")
    if parser and not parser["ok"]:
        return True
    counts = result.get("issue_counts", {})
    if fail_on == "warning":
        return counts.get("error", 0) > 0 or counts.get("warning", 0) > 0
    return counts.get("error", 0) > 0


def evaluate(input_path: Path, args: argparse.Namespace, midi_out: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": "midgrid.eval.v1",
        "input": str(input_path),
        "lint": run_lint(input_path),
        "parser": None,
        "report_summary": None,
        "issues": [],
    }

    if result["lint"]["errors"] and not args.parse_with_lint_errors:
        result["issue_counts"] = count_by_severity(result["issues"])
        return result

    parser_result = run_parser(input_path, midi_out)
    result["parser"] = parser_result
    if not parser_result["ok"]:
        result["issues"].append(issue(
            "error",
            "parse_failed",
            "midgrid_parser.py failed or did not produce a JSON report.",
            returncode=parser_result["returncode"],
            stderr=parser_result["stderr"],
        ))
        result["issue_counts"] = count_by_severity(result["issues"])
        return result

    report_path = Path(parser_result["report_json"])
    report = json.loads(report_path.read_text(encoding="utf-8"))
    result["report_summary"] = report.get("summary")
    result["issues"].extend(evaluate_report(
        report,
        high_complexity_threshold=args.high_complexity_threshold,
        wide_spacing_threshold=args.wide_spacing_threshold,
        strict_parallels=args.strict_parallels,
    ))
    result["issue_counts"] = count_by_severity(result["issues"])
    return result


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Evaluate a MidGrid file for repair-loop diagnostics.")
    parser.add_argument("input", help=".midgrid file to evaluate")
    parser.add_argument("--midi-out", help="optional output .mid path; defaults to a temporary file")
    parser.add_argument("--json", action="store_true", help="write diagnostics as JSON")
    parser.add_argument("--write-json", help="write diagnostics JSON to this path")
    parser.add_argument("--parse-with-lint-errors", action="store_true", help="try parser even if lint errors are present")
    parser.add_argument("--strict-parallels", action="store_true",
                        help="classical pedagogy mode: parallel/direct perfects are categorical "
                             "errors instead of voice_fusion meta-analysis warnings")
    parser.add_argument("--high-complexity-threshold", type=float, default=30.0)
    parser.add_argument("--wide-spacing-threshold", type=int, default=19)
    parser.add_argument("--fail-on", choices=["error", "warning", "none"], default="error")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if args.midi_out:
        midi_out = Path(args.midi_out)
        result = evaluate(input_path, args, midi_out)
    else:
        midi_out = Path(tempfile.gettempdir()) / (input_path.stem + ".mid")
        result = evaluate(input_path, args, midi_out)

    if args.write_json:
        Path(args.write_json).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_text(result))

    return 1 if should_fail(result, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
