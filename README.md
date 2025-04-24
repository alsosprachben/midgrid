# MidGrid

**MidGrid** is a lightweight textual representation of MIDI sequences designed for human readability and compactness. This project includes tools to convert `.midgrid` files into standard `.mid` files and generate playback outputs.

## Features

- Text-based MIDI composition format
- Human-editable and version-control-friendly
- Includes a parser that converts `.midgrid` to `.mid`
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
2. Generates `filename.midgrid_report.txt` with harmonic analysis
3. Plays `filename.mid` using `timidity`
4. Optionally plays `filename.ogg` if present using `sox`

If you're not using a Unix-style shell, you can invoke the parser directly via Python:

```bash
python midgrid_parser.py filename.midgrid
```

## File Structure

- `midgrid_parser.py`: Main parser converting `.midgrid` to `.mid`
- `midgrid_parser.sh`: Shell wrapper for parsing and playback

## Specifications

The following documents describe the core formats used in this project:

- [MidGrid Format Specification](midgrid.md): Defines the `.midgrid` textual format for representing MIDI sequences.
- [Harmonic Analysis Report Format](midgrid_report.md): Describes the structure of analysis reports generated from `.midgrid` input.

## License

MIT License
