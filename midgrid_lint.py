#!/usr/bin/env python3
"""Dependency-free syntax linter for strict MidGrid files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ALLOWED_NOTE_NAMES = {
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
    "B-", "A-", "E-",
}

NOTE_RE = re.compile(
    r"^(?P<name>[A-G](?:#|-)?)"
    r"(?P<octave>[0-9])"
    r"(?::(?P<duration>[0-9]+(?:\.[0-9]+)?))?"
    r"(?:@(?P<velocity>[0-9]+))?"
    r"(?:~(?P<patch>[0-9]+))?$"
)
PATCH_RE = re.compile(r"^//\s*Patch\s+(?:(V\d+)|([SATB])):\s*(\d+)\s*(?://.*)?$")
TEMPO_RE = re.compile(r"^#\s*tempo\s+([0-9]+(?:\.[0-9]+)?)(?:\s+([0-9]+(?:\.[0-9]+)?))?\s*$")


@dataclass
class Finding:
    path: str
    line: int
    column: int | None
    message: str

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "message": self.message,
        }

    def __str__(self) -> str:
        where = f"{self.path}:{self.line}"
        if self.column is not None:
            where += f":V{self.column}"
        return f"{where}: {self.message}"


def lint_cell(cell: str, path: str, line_no: int, column: int, errors: list[Finding], warnings: list[Finding]) -> None:
    if cell == "":
        warnings.append(Finding(path, line_no, column, "empty cell; prefer explicit rest '.'"))
        return
    if cell in {".", "-", "_"}:
        return
    if any(ch.isspace() for ch in cell):
        errors.append(Finding(path, line_no, column, "cell contains whitespace; move comments after the row"))
        return
    match = NOTE_RE.match(cell)
    if not match:
        errors.append(Finding(path, line_no, column, "invalid note cell or modifier order"))
        return

    name = match.group("name")
    if name not in ALLOWED_NOTE_NAMES:
        errors.append(Finding(path, line_no, column, f"unsupported note name '{name}'; prefer sharps or B-/A-/E-"))

    duration = match.group("duration")
    if duration is not None and float(duration) <= 0:
        errors.append(Finding(path, line_no, column, "duration must be greater than zero"))

    velocity = match.group("velocity")
    if velocity is not None and not (0 <= int(velocity) <= 127):
        errors.append(Finding(path, line_no, column, "velocity must be between 0 and 127"))

    patch = match.group("patch")
    if patch is not None and not (0 <= int(patch) <= 127):
        errors.append(Finding(path, line_no, column, "patch must be between 0 and 127"))


def lint_text(text: str, path: str) -> tuple[list[Finding], list[Finding]]:
    errors: list[Finding] = []
    warnings: list[Finding] = []
    voice_count: int | None = None
    previous_beat: float | None = None
    in_events = False

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue

        if in_events:
            continue

        if stripped.startswith("# events"):
            in_events = True
            continue

        if stripped.startswith("#"):
            if stripped.startswith("# tempo") and not TEMPO_RE.match(stripped):
                errors.append(Finding(path, line_no, None, "invalid # tempo directive; use '# tempo BPM [beat]'"))
            continue

        if stripped.startswith("//"):
            if stripped.startswith("// Patch"):
                match = PATCH_RE.match(stripped)
                if not match:
                    errors.append(Finding(path, line_no, None, "invalid patch directive; use '// Patch V0: 73' or '// Patch S: 73'"))
                else:
                    patch = int(match.group(3))
                    if not (0 <= patch <= 127):
                        errors.append(Finding(path, line_no, None, "patch directive must be between 0 and 127"))
            continue

        if stripped.startswith(";"):
            errors.append(Finding(path, line_no, None, "semicolon comments are not skipped by the current parser; use '#'"))
            continue

        core = raw_line.split("//", 1)[0].strip()
        if not core:
            continue

        parts = [part.strip() for part in core.split("|")]
        if len(parts) < 2:
            errors.append(Finding(path, line_no, None, "grid row must contain a beat and at least one voice column separated by '|'"))
            continue

        try:
            beat = float(parts[0])
        except ValueError:
            errors.append(Finding(path, line_no, None, "grid row must start with a numeric beat"))
            continue

        if previous_beat is not None and beat < previous_beat:
            errors.append(Finding(path, line_no, None, "beat values must not decrease"))
        previous_beat = beat

        cells = parts[1:]
        if voice_count is None:
            voice_count = len(cells)
        elif len(cells) != voice_count:
            errors.append(Finding(path, line_no, None, f"expected {voice_count} voice columns, found {len(cells)}"))

        for column, cell in enumerate(cells):
            lint_cell(cell, path, line_no, column, errors, warnings)

    if voice_count is None:
        errors.append(Finding(path, 1, None, "no MidGrid rows found"))

    return errors, warnings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Lint strict MidGrid syntax without MIDI dependencies.")
    parser.add_argument("paths", nargs="+", help=".midgrid files to lint")
    parser.add_argument("--json", action="store_true", help="write findings as JSON")
    args = parser.parse_args(argv)

    all_errors: list[Finding] = []
    all_warnings: list[Finding] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            all_errors.append(Finding(raw_path, 1, None, f"cannot read file: {exc}"))
            continue
        errors, warnings = lint_text(text, str(path))
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    if args.json:
        print(json.dumps({
            "ok": not all_errors,
            "errors": [finding.as_dict() for finding in all_errors],
            "warnings": [finding.as_dict() for finding in all_warnings],
        }, indent=2))
    else:
        for finding in all_errors:
            print(f"error: {finding}", file=sys.stderr)
        for finding in all_warnings:
            print(f"warning: {finding}", file=sys.stderr)
        if not all_errors:
            count = len(args.paths)
            suffix = "file" if count == 1 else "files"
            print(f"OK: {count} {suffix} linted")

    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
