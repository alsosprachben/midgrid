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

# Voice fusion is graded from the same ratio table as perceptual complexity:
# the simpler the interval's ratio, the more the voices' partials align, and
# the more strongly common-fate motion fuses them into one perceived stream.
# Each parallel transition contributes FUSION_SCALE / perceptual_complexity;
# runs accumulate. Below FUSION_INFO nothing is reported; at or above
# FUSION_WARN the run is a warning, in between it is informational.
FUSION_SCALE = 10.0
FUSION_INFO = 1.4
FUSION_WARN = 5.0

# Fundamental orientation (per the fundamental-oriented definition of
# contrapuntal intervals): for a just ratio n/d the implied fundamental
# lies at lower/d, so when d is a power of 2 the lower note is
# octave-equivalent to the fundamental and the interval is ROOTED
# (2/1, 3/2, 5/4, 9/8, 5/2, ...). When d has an odd factor (4/3, 6/5,
# 5/3, 8/5) the root is displaced away from the lower note. The odd part
# of d is invariant under octave compounding, so rootedness is a pure
# interval-class property: the eleventh is displaced like the fourth,
# while the twelfth (3/1) is rooted. Parallel motion on a displaced
# interval makes the unvoiced implied fundamental travel in parallel:
# covert parallels with a phantom root, reported as its own diagnostic.
# Ratio denominators by interval class (ratio = higher/lower):
#   0:1  1:15  2:8  3:5  4:4  5:3  6:32  7:2  8:5  9:3  10:9  11:8
ROOTED_CLASSES = {0, 2, 4, 6, 7, 11}

# Salience of a displaced root scales inversely with the odd factor of the
# denominator: 4/3 and 5/3 displace the root only a twelfth below the lower
# note (loud phantom), 6/5 and 8/5 push it two octaves and a third down
# (faint). Displaced runs are weighted by 3/odd_factor and warn earlier
# than fusion runs, because a traveling fourth-class root is audible fast.
DISPLACED_ODD_FACTOR = {1: 15, 3: 5, 5: 3, 8: 5, 9: 3, 10: 9}
DISPLACED_WARN = 2.8

# Melodic fusion is the directional-domain twin of voice_fusion: two voices
# sustaining same-direction co-movement share one directional predictor and
# collapse toward a single perceived stream even when no instantaneous
# interval is perfect (auditory common fate acting on contour rather than
# on ratio alignment). Regions come from midgrid_motif.melodic_fusion
# (4-beat sliding window). Calibration on the repo corpus: the warm
# capstones produce at most bare-minimum 4.0-beat regions (paired cadence
# descents), while every fused cold control runs 4.5-7.5 beats, so regions
# at the 4.0 floor are informational and anything longer warns.
MELODIC_FUSION_WARN_LEN = 4.5


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
    """Meta-analysis of the harmonic report: common-fate motion fuses two
    voices toward one perceived stream, in proportion to how simple the
    interval's ratio is. Strength is graded straight from the report's
    perceptual_complexity (FUSION_SCALE / complexity per transition), so
    parallel octaves grade far above parallel fourths, and imperfect
    parallels only surface as sustained chains. Static doubling (pedal
    points, drones) is not motion and is never reported."""
    issues = []
    beats = report.get("beats", [])
    previous_by_pair: dict[str, dict[str, Any]] = {}
    previous_beat_by_pair: dict[str, float] = {}
    runs: dict[str, dict[str, Any]] = {}

    def flush(label: str) -> None:
        run = runs.pop(label, None)
        if run is None:
            return
        strength = run["strength"]
        if strength < FUSION_INFO:
            return
        warn_at = FUSION_WARN if run["rooted"] else DISPLACED_WARN
        severity = "warning" if strength >= warn_at else "info"
        counts = f"({run['transitions']} transition{'s' if run['transitions'] > 1 else ''}, strength {strength:.1f} from the ratio table)"
        span = f"from beat {run['start']:g} to {run['end']:g}"
        if run["rooted"]:
            issues.append(issue(
                severity,
                "voice_fusion",
                f"{label} move in parallel {run['interval']} {span} {counts}: "
                f"a rooted interval, so common-fate motion merges the voices into one "
                f"bass-rooted stream. Legitimate as a deliberate handoff or doubling; "
                f"otherwise restore independence with contrary or oblique motion.",
                beat=run["end"], start_beat=run["start"], voice_pair=label,
                transitions=run["transitions"], strength=round(strength, 2),
            ))
        else:
            issues.append(issue(
                severity,
                "displaced_root_motion",
                f"{label} travel in parallel {run['interval']} {span} {counts}: "
                f"the interval's implied fundamental is displaced from the lower note "
                f"(ratio denominator has an odd factor), so the unvoiced root travels "
                f"in parallel with the pair. Break the traveling fourth-class motion, "
                f"or voice the root so the displacement is intentional.",
                beat=run["end"], start_beat=run["start"], voice_pair=label,
                transitions=run["transitions"], strength=round(strength, 2),
            ))

    for beat in beats:
        current_beat = beat["beat"]
        for pair in beat.get("pairs", []):
            label = pair["voice_pair"]
            prev = previous_by_pair.get(label)
            if prev is not None:
                moving = False
                try:
                    moving = pair["midis"][0] != prev["midis"][0]
                except (KeyError, IndexError, TypeError):
                    moving = pair.get("motion") == "parallel"
                complexity = pair.get("perceptual_complexity")
                if pair.get("motion") == "parallel" and moving and complexity:
                    step = FUSION_SCALE / max(float(complexity), 1.0)
                    cls = interval_class(pair)
                    if cls not in ROOTED_CLASSES:
                        step *= 3.0 / DISPLACED_ODD_FACTOR.get(cls, 3)
                    run = runs.get(label)
                    if run is None:
                        runs[label] = {
                            "start": previous_beat_by_pair[label],
                            "end": current_beat,
                            "transitions": 1,
                            "strength": step,
                            "interval": pair.get("interval", "intervals"),
                            "rooted": interval_class(pair) in ROOTED_CLASSES,
                        }
                    else:
                        run["end"] = current_beat
                        run["transitions"] += 1
                        run["strength"] += step
                else:
                    flush(label)
            previous_by_pair[label] = pair
            previous_beat_by_pair[label] = current_beat

    for label in list(runs):
        flush(label)
    return issues


def detect_melodic_fusion(input_path: Path) -> list[dict[str, Any]]:
    """Directional meta-analysis of the grid itself: sustained regions where
    a voice pair co-moves in the same direction. Severity is graded by how
    far the region outlasts the detection window; `locked` counts steps
    where the chromatic motion is identical (the strongest common-fate
    cue)."""
    from midgrid_motif import melodic_fusion, parse_midgrid

    issues_list = []
    for region in melodic_fusion(parse_midgrid(input_path)):
        length = region["beat_end"] - region["beat_start"]
        severity = "warning" if length >= MELODIC_FUSION_WARN_LEN else "info"
        issues_list.append(issue(
            severity,
            "melodic_fusion",
            f"{region['pair']} co-move in the same direction from beat "
            f"{region['beat_start']:g} to {region['beat_end']:g} "
            f"({region['comoves']} co-movements, {region['locked']} locked steps): "
            f"the voices share one directional predictor and collapse toward a "
            f"single stream even without parallel perfects. Give one voice "
            f"contrary or oblique cells, or make the doubling deliberate.",
            beat=region["beat_end"],
            start_beat=region["beat_start"],
            voice_pair=region["pair"],
            comoves=region["comoves"],
            locked=region["locked"],
            length_beats=round(length, 2),
        ))
    return issues_list


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
    if not args.strict_parallels and not args.no_melodic_fusion:
        result["issues"].extend(detect_melodic_fusion(input_path))
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
    parser.add_argument("--no-melodic-fusion", action="store_true",
                        help="disable the melodic_fusion directional meta-analysis")
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
