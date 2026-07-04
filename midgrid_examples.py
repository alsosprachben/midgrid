#!/usr/bin/env python3
"""Export recorded MidGrid training examples as prompt-ready packs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_RECORDS_DIR = Path("training_examples")
DEFAULT_EXERCISES_DIR = Path("exercises")


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def maybe_read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


def read_text_excerpt(path: Path, max_lines: int) -> str:
    text = path.read_text(encoding="utf-8").rstrip()
    if max_lines <= 0:
        return text
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    omitted = len(lines) - max_lines
    clipped = lines[:max_lines]
    clipped.append(f"... ({omitted} more lines omitted)")
    return "\n".join(clipped)


def load_exercises(exercises_dir: Path) -> dict[str, dict[str, Any]]:
    base = repo_root() / exercises_dir
    exercises: dict[str, dict[str, Any]] = {}
    if not base.exists():
        return exercises
    for path in sorted(base.glob("*.json")):
        data = read_json(path)
        data["_path"] = str(path.relative_to(repo_root()))
        exercises[data["id"]] = data
    return exercises


def get_target_exercise(exercises: dict[str, dict[str, Any]], exercise_id: str | None) -> dict[str, Any] | None:
    if not exercise_id:
        return None
    try:
        return exercises[exercise_id]
    except KeyError:
        known = ", ".join(sorted(exercises))
        raise SystemExit(f"unknown target exercise id '{exercise_id}'. Known ids: {known}")


def issue_counts_by_code(eval_data: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in eval_data.get("issues", []):
        code = issue.get("code", "unknown")
        counts[code] = counts.get(code, 0) + 1
    return counts


def compact_issues(eval_data: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    compact = []
    for issue in eval_data.get("issues", [])[:limit]:
        item = {
            "severity": issue.get("severity"),
            "code": issue.get("code"),
            "message": issue.get("message"),
        }
        for key in ["beat", "voice", "voice_pair", "voices", "interval", "interval_class"]:
            if key in issue:
                item[key] = issue[key]
        compact.append(item)
    return compact


def build_example(record_path: Path, exercises: dict[str, dict[str, Any]], max_lines: int) -> dict[str, Any]:
    record_dir = record_path.parent
    record = read_json(record_path)
    exercise_id = record["exercise_id"]
    exercise = exercises.get(exercise_id, {})
    attempt_eval = maybe_read_json(record_dir / record.get("attempt_eval", "attempt.eval.json"))
    corrected_eval = maybe_read_json(record_dir / record.get("corrected_eval", "corrected.eval.json"))

    attempt_path = record_dir / record.get("attempt", "attempt.midgrid")
    corrected_path = record_dir / record.get("corrected", "corrected.midgrid")

    return {
        "exercise_id": exercise_id,
        "exercise_title": record.get("exercise_title") or exercise.get("title"),
        "skill": exercise.get("skill"),
        "species": exercise.get("species"),
        "created_utc": record.get("created_utc"),
        "record_path": str(record_path.relative_to(repo_root())),
        "objective": exercise.get("objective"),
        "prompt": exercise.get("prompt"),
        "lesson": record.get("lesson", ""),
        "attempt_issue_counts": issue_counts_by_code(attempt_eval),
        "attempt_issues": compact_issues(attempt_eval),
        "corrected_issue_counts": corrected_eval.get("issue_counts", {}),
        "corrected_report_summary": corrected_eval.get("report_summary"),
        "attempt_midgrid": read_text_excerpt(attempt_path, max_lines),
        "corrected_midgrid": read_text_excerpt(corrected_path, max_lines),
    }


def target_for_output(target: dict[str, Any] | None) -> dict[str, Any] | None:
    if target is None:
        return None
    return {
        "exercise_id": target["id"],
        "exercise_title": target["title"],
        "skill": target.get("skill"),
        "species": target.get("species"),
        "objective": target.get("objective"),
        "prompt": target.get("prompt"),
        "seed_midgrid": target.get("seed_midgrid"),
        "success_criteria": target.get("success_criteria", []),
        "evaluation_defaults": target.get("evaluation_defaults", {}),
        "exercise_checks": target.get("exercise_checks", {}),
    }


def collect_examples(args: argparse.Namespace, exercises: dict[str, dict[str, Any]], target: dict[str, Any] | None) -> list[dict[str, Any]]:
    base = repo_root() / args.records_dir
    examples = []
    filter_skill = args.skill
    if filter_skill is None and target is not None:
        filter_skill = target.get("skill")

    excluded = set(args.exclude_exercise_id or [])
    if target is not None and not args.include_target_example:
        excluded.add(target["id"])

    for record_path in sorted(base.glob("*/*/record.json")):
        example = build_example(record_path, exercises, args.max_lines)
        if example.get("exercise_id") in excluded:
            continue
        if filter_skill and example.get("skill") != filter_skill:
            continue
        if args.species and example.get("species") != args.species:
            continue
        if args.exercise_id and example.get("exercise_id") != args.exercise_id:
            continue
        examples.append(example)
    if args.limit is not None:
        examples = examples[:args.limit]
    return examples


def render_code_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{code}={count}" for code, count in sorted(counts.items()))


def render_result_summary(example: dict[str, Any]) -> str:
    counts = example.get("corrected_issue_counts") or {}
    summary = example.get("corrected_report_summary") or {}
    pieces = [
        f"errors={counts.get('error', 0)}",
        f"warnings={counts.get('warning', 0)}",
    ]
    if summary:
        pieces.append(f"beats={summary.get('beat_count', 'n/a')}")
        pieces.append(f"mean_complexity={summary.get('mean_perceptual_complexity', 'n/a')}")
    return ", ".join(pieces)


def render_example_markdown(example: dict[str, Any], index: int) -> list[str]:
    title = example.get("exercise_title") or example["exercise_id"]
    lines = [
        f"## Example {index}: {title}",
        "",
        f"Exercise: `{example['exercise_id']}`",
        f"Skill: `{example.get('skill') or 'n/a'}`",
        f"Species: `{example.get('species') or 'n/a'}`",
        f"Record: `{example['record_path']}`",
        "",
    ]
    if example.get("objective"):
        lines.extend(["Objective:", example["objective"], ""])
    if example.get("prompt"):
        lines.extend(["Prompt:", example["prompt"], ""])
    lines.extend([
        "Attempt issue codes:",
        render_code_counts(example.get("attempt_issue_counts") or {}),
        "",
    ])
    issues = example.get("attempt_issues") or []
    if issues:
        lines.append("Diagnosis excerpt:")
        for issue in issues:
            location = []
            if "beat" in issue:
                location.append(f"beat {issue['beat']:g}")
            if "voice_pair" in issue:
                location.append(issue["voice_pair"])
            elif "voice" in issue:
                location.append(f"V{issue['voice']}")
            where = f" ({', '.join(location)})" if location else ""
            lines.append(f"- {issue.get('severity')} {issue.get('code')}{where}: {issue.get('message')}")
        lines.append("")
    lines.extend([
        "Attempt:",
        "```text",
        example["attempt_midgrid"],
        "```",
        "",
        "Correction:",
        "```text",
        example["corrected_midgrid"],
        "```",
        "",
        "Result:",
        render_result_summary(example),
        "",
        "Lesson:",
        example.get("lesson") or "Correction passed evaluator requirements.",
        "",
    ])
    return lines


def render_target_markdown(target: dict[str, Any]) -> list[str]:
    checks = target.get("exercise_checks") or {}
    lines = [
        "# Target Exercise",
        "",
        f"Exercise: `{target['id']}`",
        f"Title: {target['title']}",
        f"Skill: `{target.get('skill') or 'n/a'}`",
        f"Species: `{target.get('species') or 'n/a'}`",
        "",
        "Objective:",
        target.get("objective", ""),
        "",
        "Prompt:",
        target.get("prompt", ""),
        "",
        "Seed MidGrid:",
        "```text",
        target.get("seed_midgrid", "").rstrip(),
        "```",
        "",
    ]
    criteria = target.get("success_criteria") or []
    if criteria:
        lines.append("Success Criteria:")
        for item in criteria:
            lines.append(f"- {item}")
        lines.append("")
    if checks:
        lines.extend([
            "Exercise Checks:",
            "```json",
            json.dumps(checks, indent=2),
            "```",
            "",
        ])
    lines.extend([
        "Task:",
        "Study the examples above, then complete the target exercise. Output strict parser-valid MidGrid only unless a diagnosis is explicitly requested.",
        "",
        "After drafting, evaluate with:",
        "```bash",
        f"python3 midgrid_exercise.py evaluate {target['id']} attempt.midgrid --fail-on none",
        "```",
    ])
    return lines


def render_markdown(examples: list[dict[str, Any]], target: dict[str, Any] | None = None) -> str:
    lines = [
        "# MidGrid Example Pack",
        "",
        "Use these as few-shot learning material: imitate the attempt, diagnosis, correction, and lesson pattern. Rules are included only as diagnostic labels and validation checks.",
        "",
    ]
    if not examples:
        lines.append("No examples matched the filters.")
        lines.append("")

    for index, example in enumerate(examples, start=1):
        lines.extend(render_example_markdown(example, index))

    if target is not None:
        lines.extend(render_target_markdown(target))

    return "\n".join(lines).rstrip() + "\n"


def render_json(examples: list[dict[str, Any]], target: dict[str, Any] | None = None) -> str:
    return json.dumps({
        "schema": "midgrid.example_pack.v1",
        "examples": examples,
        "target_exercise": target_for_output(target),
    }, indent=2) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export recorded MidGrid examples for in-context composition learning.")
    parser.add_argument("--records-dir", type=Path, default=DEFAULT_RECORDS_DIR)
    parser.add_argument("--exercises-dir", type=Path, default=DEFAULT_EXERCISES_DIR)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--skill", help="filter examples by exercise skill")
    parser.add_argument("--species", help="filter examples by species")
    parser.add_argument("--exercise-id", help="filter examples by exercise id")
    parser.add_argument("--exclude-exercise-id", action="append", default=[], help="exclude a recorded exercise id; may be repeated")
    parser.add_argument("--target-exercise-id", help="append a target exercise prompt after examples; excludes its recorded solution by default")
    parser.add_argument("--include-target-example", action="store_true", help="allow examples from --target-exercise-id to appear in the pack")
    parser.add_argument("--limit", type=int, help="maximum examples to emit")
    parser.add_argument("--max-lines", type=int, default=80, help="maximum MidGrid lines per attempt/correction; <=0 keeps full text")
    parser.add_argument("--output", type=Path, help="write the rendered pack to a file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    exercises = load_exercises(args.exercises_dir)
    target = get_target_exercise(exercises, args.target_exercise_id)
    examples = collect_examples(args, exercises, target)
    if args.format == "json":
        rendered = render_json(examples, target)
    else:
        rendered = render_markdown(examples, target)

    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
