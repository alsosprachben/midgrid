#!/usr/bin/env python3
"""Run and record example-oriented MidGrid counterpoint exercises."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

DEFAULT_EXERCISES_DIR = Path("exercises")
DEFAULT_RECORDS_DIR = Path("training_examples")

REQUIRED_EXERCISE_FIELDS = {
    "id",
    "title",
    "skill",
    "objective",
    "prompt",
    "seed_midgrid",
    "success_criteria",
    "evaluation_defaults",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def load_exercises(exercises_dir: Path) -> dict[str, dict[str, Any]]:
    base = repo_root() / exercises_dir
    exercises = {}
    if not base.exists():
        raise SystemExit(f"exercise directory not found: {base}")
    for path in sorted(base.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = sorted(REQUIRED_EXERCISE_FIELDS - set(data))
        if missing:
            raise SystemExit(f"{path}: missing required fields: {', '.join(missing)}")
        exercise_id = data["id"]
        if exercise_id in exercises:
            raise SystemExit(f"duplicate exercise id: {exercise_id}")
        data["_path"] = str(path)
        exercises[exercise_id] = data
    return exercises


def get_exercise(exercises: dict[str, dict[str, Any]], exercise_id: str) -> dict[str, Any]:
    try:
        return exercises[exercise_id]
    except KeyError:
        known = ", ".join(sorted(exercises))
        raise SystemExit(f"unknown exercise id '{exercise_id}'. Known ids: {known}")


def evaluation_args(exercise: dict[str, Any], fail_on: str | None = None) -> list[str]:
    defaults = exercise.get("evaluation_defaults", {})
    args = []
    args.extend(["--high-complexity-threshold", str(defaults.get("high_complexity_threshold", 30.0))])
    args.extend(["--wide-spacing-threshold", str(defaults.get("wide_spacing_threshold", 19))])
    args.extend(["--fail-on", fail_on or defaults.get("fail_on", "error")])
    return args


def run_command(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=repo_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_eval(exercise: dict[str, Any], midgrid_path: Path, fail_on: str | None = None) -> tuple[dict[str, Any], subprocess.CompletedProcess[str]]:
    argv = [
        sys.executable,
        "midgrid_eval.py",
        str(midgrid_path),
        "--json",
    ]
    argv.extend(evaluation_args(exercise, fail_on=fail_on))
    proc = run_command(argv)
    if not proc.stdout.strip():
        raise SystemExit(f"midgrid_eval.py produced no JSON for {midgrid_path}\n{proc.stderr}")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"could not parse evaluator JSON for {midgrid_path}: {exc}\n{proc.stdout}\n{proc.stderr}")
    return data, proc


REST_OR_HOLD_CELLS = {"", ".", "-", "_"}


def parse_grid_rows(text: str) -> list[dict[str, Any]]:
    rows = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("# events"):
            break
        if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith(";"):
            continue
        core = raw_line.split("//", 1)[0].strip()
        if not core:
            continue
        parts = [part.strip() for part in core.split("|")]
        if len(parts) < 2:
            continue
        try:
            beat = float(parts[0])
        except ValueError:
            continue
        rows.append({"line": line_number, "beat": beat, "cells": parts[1:]})
    return rows


def read_grid_rows(path: Path) -> list[dict[str, Any]]:
    return parse_grid_rows(path.read_text(encoding="utf-8"))


def cell_is_note(cell: str) -> bool:
    return cell.strip() not in REST_OR_HOLD_CELLS


def cell_is_sounding(cell: str) -> bool:
    # A hold continues a sounding note, so it fills its row; syncopated
    # species sustain across downbeats with '-' cells.
    return cell.strip() in {"-", "_"} or cell_is_note(cell)


def exercise_issue(severity: str, code: str, message: str, **fields: Any) -> dict[str, Any]:
    data = {"severity": severity, "code": code, "message": message}
    data.update(fields)
    return data


def issue_counts(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"error": 0, "warning": 0, "info": 0}
    for item in issues:
        severity = item.get("severity", "info")
        counts[severity] = counts.get(severity, 0) + 1
    return counts


def load_report(eval_data: dict[str, Any]) -> dict[str, Any] | None:
    parser = eval_data.get("parser") or {}
    report_json = parser.get("report_json")
    if not report_json:
        return None
    report_path = Path(report_json)
    if not report_path.exists():
        return None
    try:
        return json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def beat_matches_interval_rule(beat: float, rule: dict[str, Any]) -> bool:
    epsilon = 1e-6
    if any(abs(beat - float(excluded)) < epsilon for excluded in rule.get("exclude_beats", [])):
        return False
    if "beats" in rule:
        return any(abs(beat - float(candidate)) < epsilon for candidate in rule["beats"])

    beat_filter = rule.get("beat_filter", "all")
    if beat_filter == "all":
        return True
    if beat_filter == "integer":
        return abs(beat - round(beat)) < epsilon
    if beat_filter == "non_integer":
        return abs(beat - round(beat)) >= epsilon
    return True


def append_interval_rule_checks(checks: dict[str, Any], eval_data: dict[str, Any], exercise_issues: list[dict[str, Any]]) -> None:
    rules = checks.get("interval_rules") or []
    if not rules:
        return
    report = load_report(eval_data)
    if report is None:
        return

    for rule in rules:
        voice_pair = rule.get("voice_pair", "V0-V1")
        allowed_classes = {int(value) % 12 for value in rule.get("allowed_interval_classes", [])}
        if not allowed_classes:
            continue
        severity = rule.get("severity", "error")
        code = rule.get("code", "exercise_interval_class")
        label = rule.get("label", "interval rule")
        allow_rests = bool(rule.get("allow_rests", False))

        for beat_report in report.get("beats", []):
            beat = float(beat_report["beat"])
            if not beat_matches_interval_rule(beat, rule):
                continue
            pair = next((item for item in beat_report.get("pairs", []) if item.get("voice_pair") == voice_pair), None)
            if pair is None or pair.get("interval_semitones") is None:
                if allow_rests:
                    continue
                exercise_issues.append(exercise_issue(
                    severity,
                    "exercise_interval_rest",
                    f"{label}: {voice_pair} has no sounding interval at beat {beat:g}.",
                    beat=beat,
                    voice_pair=voice_pair,
                ))
                continue

            interval = int(pair["interval_semitones"])
            interval_class = interval % 12
            if interval_class not in allowed_classes:
                exercise_issues.append(exercise_issue(
                    severity,
                    code,
                    f"{label}: {voice_pair} interval class {interval_class} is not allowed at beat {beat:g}.",
                    beat=beat,
                    voice_pair=voice_pair,
                    interval=pair.get("interval"),
                    interval_semitones=interval,
                    interval_class=interval_class,
                    allowed_interval_classes=sorted(allowed_classes),
                ))


def append_exercise_checks(exercise: dict[str, Any], eval_data: dict[str, Any], midgrid_path: Path) -> None:
    checks = exercise.get("exercise_checks") or {}
    if not checks:
        eval_data["exercise_issues"] = []
        return

    exercise_issues: list[dict[str, Any]] = []
    attempt_rows = read_grid_rows(midgrid_path)
    seed_rows = parse_grid_rows(exercise["seed_midgrid"])

    expected_rows = len(seed_rows)
    if expected_rows and len(attempt_rows) != expected_rows:
        exercise_issues.append(exercise_issue(
            "error",
            "exercise_row_count",
            f"Exercise expects {expected_rows} grid rows, found {len(attempt_rows)}.",
            expected_rows=expected_rows,
            actual_rows=len(attempt_rows),
        ))

    voices_sounded: set[int] = set()
    for row_index, (seed_row, attempt_row) in enumerate(zip(seed_rows, attempt_rows)):
        if seed_row["beat"] != attempt_row["beat"]:
            exercise_issues.append(exercise_issue(
                "error",
                "exercise_beat_changed",
                f"Beat at row {row_index + 1} changed from {seed_row['beat']:g} to {attempt_row['beat']:g}.",
                row=row_index + 1,
                expected_beat=seed_row["beat"],
                actual_beat=attempt_row["beat"],
            ))

        for voice in checks.get("locked_voices", []):
            seed_cell = seed_row["cells"][voice].strip() if voice < len(seed_row["cells"]) else None
            attempt_cell = attempt_row["cells"][voice].strip() if voice < len(attempt_row["cells"]) else None
            if seed_cell != attempt_cell:
                exercise_issues.append(exercise_issue(
                    "error",
                    "exercise_locked_voice_changed",
                    f"Locked V{voice} changed at beat {attempt_row['beat']:g}.",
                    beat=attempt_row["beat"],
                    voice=voice,
                    expected=seed_cell,
                    actual=attempt_cell,
                ))

        for voice in checks.get("filled_voices", []):
            attempt_cell = attempt_row["cells"][voice].strip() if voice < len(attempt_row["cells"]) else ""
            if cell_is_note(attempt_cell):
                voices_sounded.add(voice)
            # Leading rests are legal (syncopated species enter after a rest);
            # a voice must be continuously filled only once it has sounded.
            if voice not in voices_sounded:
                continue
            if not cell_is_sounding(attempt_cell):
                exercise_issues.append(exercise_issue(
                    "error",
                    "exercise_unfilled_voice",
                    f"Required V{voice} is not filled at beat {attempt_row['beat']:g}.",
                    beat=attempt_row["beat"],
                    voice=voice,
                    actual=attempt_cell,
                ))

    append_interval_rule_checks(checks, eval_data, exercise_issues)

    eval_data["exercise_issues"] = exercise_issues
    if exercise_issues:
        eval_data.setdefault("issues", []).extend(exercise_issues)
    eval_data["issue_counts"] = issue_counts(eval_data.get("issues", []))


def lint_ok(eval_data: dict[str, Any]) -> bool:
    return not eval_data.get("lint", {}).get("errors")


def eval_failed(eval_data: dict[str, Any], fail_on: str) -> bool:
    if not lint_ok(eval_data):
        return True
    parser = eval_data.get("parser")
    if parser and not parser.get("ok"):
        return True
    counts = eval_data.get("issue_counts", {})
    if fail_on == "none":
        return False
    if fail_on == "warning":
        return counts.get("error", 0) > 0 or counts.get("warning", 0) > 0
    return counts.get("error", 0) > 0


def print_issue_summary(eval_data: dict[str, Any]) -> None:
    counts = eval_data.get("issue_counts", {})
    summary = eval_data.get("report_summary") or {}
    print(
        "summary: "
        f"errors={counts.get('error', 0)} "
        f"warnings={counts.get('warning', 0)} "
        f"beats={summary.get('beat_count', 'n/a')} "
        f"mean_complexity={summary.get('mean_perceptual_complexity', 'n/a')}"
    )
    issues = eval_data.get("issues", [])
    for item in issues:
        location = []
        if "beat" in item:
            location.append(f"beat {item['beat']:g}")
        if "voice_pair" in item:
            location.append(item["voice_pair"])
        elif "voices" in item:
            location.append("V" + "-V".join(str(v) for v in item["voices"]))
        loc = f" ({', '.join(location)})" if location else ""
        print(f"- {item['severity']} {item['code']}{loc}: {item['message']}")


def command_list(args: argparse.Namespace) -> int:
    exercises = load_exercises(args.exercises_dir)
    for exercise in exercises.values():
        species = exercise.get("species", "")
        species_suffix = f" [{species}]" if species else ""
        print(f"{exercise['id']} - {exercise['title']}{species_suffix}")
    return 0


def command_show(args: argparse.Namespace) -> int:
    exercises = load_exercises(args.exercises_dir)
    exercise = get_exercise(exercises, args.exercise_id)
    if args.json:
        data = {k: v for k, v in exercise.items() if not k.startswith("_")}
        print(json.dumps(data, indent=2))
        return 0

    print(f"# {exercise['title']}")
    print(f"id: {exercise['id']}")
    print(f"skill: {exercise['skill']}")
    if exercise.get("species"):
        print(f"species: {exercise['species']}")
    print()
    print("Objective:")
    print(exercise["objective"])
    print()
    print("Prompt:")
    print(exercise["prompt"])
    print()
    print("Seed MidGrid:")
    print(exercise["seed_midgrid"].rstrip())
    print()
    print("Success Criteria:")
    for criterion in exercise["success_criteria"]:
        print(f"- {criterion}")
    return 0


def command_evaluate(args: argparse.Namespace) -> int:
    exercises = load_exercises(args.exercises_dir)
    exercise = get_exercise(exercises, args.exercise_id)
    attempt_path = Path(args.attempt_midgrid)
    eval_data, proc = run_eval(exercise, attempt_path, fail_on=args.fail_on)
    append_exercise_checks(exercise, eval_data, attempt_path)

    if args.write_json:
        Path(args.write_json).write_text(json.dumps(eval_data, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(eval_data, indent=2))
    else:
        print(f"Exercise: {exercise['id']} - {exercise['title']}")
        print(f"Attempt: {attempt_path}")
        print_issue_summary(eval_data)

    fail_on = args.fail_on or exercise.get("evaluation_defaults", {}).get("fail_on", "error")
    return 1 if eval_failed(eval_data, fail_on) else 0


def record_dir(base_dir: Path, exercise_id: str) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return repo_root() / base_dir / exercise_id / stamp


def copy_optional_report(eval_data: dict[str, Any], destination: Path, prefix: str) -> dict[str, str | None]:
    parser = eval_data.get("parser") or {}
    copied = {"report_json": None, "report_text": None}
    for key, suffix in [("report_json", ".report.json"), ("report_text", ".report.txt")]:
        src = parser.get(key)
        if not src:
            continue
        src_path = Path(src)
        if src_path.exists():
            dst = destination / f"{prefix}{suffix}"
            shutil.copy2(src_path, dst)
            copied[key] = dst.name
    return copied


def command_record(args: argparse.Namespace) -> int:
    exercises = load_exercises(args.exercises_dir)
    exercise = get_exercise(exercises, args.exercise_id)
    attempt_path = Path(args.attempt_midgrid)
    corrected_path = Path(args.corrected_midgrid)

    attempt_eval, _ = run_eval(exercise, attempt_path, fail_on="none")
    append_exercise_checks(exercise, attempt_eval, attempt_path)
    corrected_fail_on = args.corrected_fail_on or exercise.get("recording", {}).get("corrected_fail_on", "error")
    corrected_eval, _ = run_eval(exercise, corrected_path, fail_on=corrected_fail_on)
    append_exercise_checks(exercise, corrected_eval, corrected_path)

    failures = []
    if not lint_ok(attempt_eval):
        failures.append("attempt has lint errors")
    if not lint_ok(corrected_eval):
        failures.append("corrected file has lint errors")
    if eval_failed(corrected_eval, corrected_fail_on):
        failures.append(f"corrected file fails evaluator with --fail-on {corrected_fail_on}")
    if failures:
        for failure in failures:
            print(f"record rejected: {failure}", file=sys.stderr)
        print("Attempt diagnostics:", file=sys.stderr)
        print(json.dumps(attempt_eval.get("lint", {}), indent=2), file=sys.stderr)
        print("Corrected issue counts:", file=sys.stderr)
        print(json.dumps(corrected_eval.get("issue_counts", {}), indent=2), file=sys.stderr)
        return 1

    destination = record_dir(args.records_dir, exercise["id"])
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copy2(attempt_path, destination / "attempt.midgrid")
    shutil.copy2(corrected_path, destination / "corrected.midgrid")
    (destination / "attempt.eval.json").write_text(json.dumps(attempt_eval, indent=2) + "\n", encoding="utf-8")
    (destination / "corrected.eval.json").write_text(json.dumps(corrected_eval, indent=2) + "\n", encoding="utf-8")
    attempt_reports = copy_optional_report(attempt_eval, destination, "attempt")
    corrected_reports = copy_optional_report(corrected_eval, destination, "corrected")

    lesson = args.lesson.strip() if args.lesson else ""
    if not lesson:
        lesson = "Correction passed lint and evaluator requirements."
    record = {
        "schema": "midgrid.training_example.v1",
        "exercise_id": exercise["id"],
        "exercise_title": exercise["title"],
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "attempt": "attempt.midgrid",
        "corrected": "corrected.midgrid",
        "attempt_eval": "attempt.eval.json",
        "corrected_eval": "corrected.eval.json",
        "attempt_reports": attempt_reports,
        "corrected_reports": corrected_reports,
        "lesson": lesson,
    }
    (destination / "record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(f"recorded: {destination}")
    print(f"lesson: {lesson}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run and record MidGrid composition exercises.")
    parser.add_argument("--exercises-dir", type=Path, default=DEFAULT_EXERCISES_DIR)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list available exercises")
    list_parser.set_defaults(func=command_list)

    show_parser = subparsers.add_parser("show", help="show an exercise prompt and seed MidGrid")
    show_parser.add_argument("exercise_id")
    show_parser.add_argument("--json", action="store_true")
    show_parser.set_defaults(func=command_show)

    eval_parser = subparsers.add_parser("evaluate", help="evaluate an attempt against an exercise")
    eval_parser.add_argument("exercise_id")
    eval_parser.add_argument("attempt_midgrid")
    eval_parser.add_argument("--json", action="store_true")
    eval_parser.add_argument("--write-json")
    eval_parser.add_argument("--fail-on", choices=["error", "warning", "none"])
    eval_parser.set_defaults(func=command_evaluate)

    record_parser = subparsers.add_parser("record", help="record an attempt/correction pair as a training example")
    record_parser.add_argument("exercise_id")
    record_parser.add_argument("attempt_midgrid")
    record_parser.add_argument("corrected_midgrid")
    record_parser.add_argument("--records-dir", type=Path, default=DEFAULT_RECORDS_DIR)
    record_parser.add_argument("--corrected-fail-on", choices=["error", "warning", "none"])
    record_parser.add_argument("--lesson", help="short lesson distilled from the correction")
    record_parser.set_defaults(func=command_record)

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
