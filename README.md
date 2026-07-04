# MidGrid

**MidGrid** is a lightweight textual representation of MIDI sequences designed for human readability and compactness. This project includes tools to convert `.midgrid` files into standard `.mid` files and generate playback outputs.

## Features

- Text-based MIDI composition format
- Human-editable and version-control-friendly
- Includes a parser that converts `.midgrid` to `.mid` and writes text/JSON harmonic reports
- Plays output MIDI and audio with optional tools

## Requirements

To use the MidGrid tools, ensure you have the following dependencies installed:

- Python 3.7+
- `timidity` (for MIDI playback)
- `sox` (for `.ogg` playback via `play`)
- Python packages: `mido`, `python-rtmidi` (if using live playback or I/O extensions)

To install the Python dependencies:

```bash
pip install mido python-rtmidi
```

To install required command-line tools on macOS using Homebrew:

```bash
brew install timidity sox
```

## Usage

To convert and play a MidGrid file using the shell script (Unix/macOS):

```bash
./midgrid_parser.sh filename
```

This script:
1. Converts `filename.midgrid` to `filename.mid`
2. Generates `filename.report.txt` and `filename.report.json` with harmonic analysis
3. Plays `filename.mid` using `timidity`
4. Optionally plays `filename.ogg` if present using `sox`

If you're not using a Unix-style shell, you can invoke the parser directly via Python:

```bash
python midgrid_parser.py filename.midgrid filename.mid
```

To lint MidGrid syntax without MIDI dependencies:

```bash
python3 midgrid_lint.py filename.midgrid
```

To run the full repair-loop evaluator, including lint, parser, JSON report, and counterpoint diagnostics:

```bash
python3 midgrid_eval.py filename.midgrid --fail-on none
```

To run example-oriented composition exercises:

```bash
python3 midgrid_exercise.py list
python3 midgrid_exercise.py show first-species-above-001
python3 midgrid_exercise.py show second-species-above-001
python3 midgrid_exercise.py evaluate first-species-above-001 attempt.midgrid
```

To export recorded attempts and corrections as few-shot learning material:

```bash
python3 midgrid_examples.py --skill species-counterpoint --format markdown
```

## File Structure

- `midgrid_parser.py`: Main parser converting `.midgrid` to `.mid` and writing `.report.txt`/`.report.json`
- `midgrid_parser.sh`: Shell wrapper for parsing and playback
- `midgrid_lint.py`: Dependency-free strict syntax linter for generated MidGrid
- `midgrid_eval.py`: Repair-loop evaluator for lint, parser, report, and counterpoint diagnostics
- `midgrid_exercise.py`: Exercise runner for Fux-style examples, evaluation, and training records
- `midgrid_examples.py`: Example-pack exporter for in-context learning from recorded attempts and corrections

## Specifications

The following documents describe the core formats used in this project:

- [MidGrid Format Specification](midgrid.md): Defines the `.midgrid` textual format for representing MIDI sequences.
- [Harmonic Analysis Report Format](midgrid_report.md): Describes the structure of analysis reports generated from `.midgrid` input.
- [MidGrid Evaluation Diagnostics](midgrid_eval.md): Defines repair-loop diagnostics emitted by `midgrid_eval.py`.
- [MidGrid Exercise Runner](midgrid_exercise.md): Defines exercise files, commands, and training example records.
- [MidGrid Example Pack Exporter](midgrid_examples.md): Defines prompt-ready example packs generated from recorded training examples.

## Composition Skills

The [composition skills map](composition_skills.md) outlines repo-local skill packets for example-driven counterpoint and fugue training with MidGrid, including strict output, Fux species exercises, harmonic effect control, fugue exposition, and report-driven repair loops.

## License

MIT License
