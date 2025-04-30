# MidGrid Format Specification

The MidGrid format is a compact, human-readable grid-based notation for specifying MIDI events across multiple voices in a polyphonic composition. It is designed to be easily parsed by programs and editable by musicians or developers. This specification includes some features discovered in the reference parser but not previously documented.

## Overview

A MidGrid file represents musical notes and timing in a text grid where each column represents a beat subdivision and each row represents a voice or instrument. Each voice line specifies events using shorthand symbols, and all voices are aligned horizontally by beat position.

## Format

- The file is structured as:
  - An optional metadata block (comment lines starting with `#` or `;`)
  - A sequence of time-aligned lines for each voice
- Voice lines follow the format:
  ```
  V[n]: [note grid...]
  ```
  where `V[n]` is the voice number, and the note grid consists of space- or tab-separated symbols denoting pitch events.
- Voice aliases such as `S`, `A`, `T`, and `B` (for Soprano, Alto, Tenor, Bass) may be used in place of `V0`, `V1`, etc., in `// Patch` directives or voice assignments.
- Tempo changes can be specified using `# tempo <BPM> [at_beat]`, where BPM is a number and `at_beat` is optional (defaults to 0.0). Example: `# tempo 72.0 8.0`

### Symbols

- A pitch is written as a note name followed by an optional octave shift:
  - Examples: `C4`, `D#3`, `G5`, `Bb`
- A held note is represented by `-` (continuation of the previous pitch). Held notes must still appear as entries in each beat row, even if the note is continuing. Its duration is also implicitly extended until the next beat row unless a duration is explicitly provided earlier.
- A rest or silence is represented by `.` or space. Rests must be explicitly present in each beat row.
- Optional **velocity** (volume) is encoded with `@` suffix:
  - Example: `C4@90`
  - If not specified, the default velocity is `70`.
- Optional **duration** (in beats) is encoded with `:` suffix:
  - Example: `E4:1.5` (plays for 1.5 beats)
  - Beat numbers and durations can be fractional (e.g., `:0.5`, `:1.25`).
  - If duration is omitted, it is implicitly calculated to extend to the next explicitly declared beat row.
- Velocity and duration can be specified independently or together using either `@`, `:`, or both suffixes:
  - Examples: `D#4@80:1.0`, `G3:0.5@100`
- Optional **instrument patch** (MIDI program number) is encoded with `~` suffix:
  - Example: `G3~41`
  - Inline patch changes can also be specified per note using `~` within the cell (e.g., `C4~41`). This allows mid-sequence patch changes for a voice.
- Multiple properties may be chained in any order:
  - Examples: `C4@100:1.5~23`, `C4~23:1.5@100`
- You may use `//` within a note cell for inline comments; text after `//` in a cell is ignored after splitting.

### Example

```
# Title: Fugue Example
# Tempo: 90
# tempo 90.0

V0: C4   -    -    D4   -    -    E4   -    -    F4   -    -    
V1: G3   -    -    A3   -    -    B3   -    -    C4   -    -    
V2: .    .    C3   -    -    .    D3   -    -    .    E3   -    
```

## Notes

- All voices must contain the same number of columns (use `.` or `-` to pad).
- Columns may be subdivided by measure with visual guides (`|`) for readability.
- Grid spacing may be adjusted for visual alignment but must maintain consistency within a line.
- The parser accepts chained note modifiers in any order and parses them according to suffix symbols.
- Inline `// Patch` changes mid-sequence can alter the patch for a voice on that row.
- If you run the parser script directly, a contrapuntal analysis report may be generated alongside the MIDI output.
- Tempo changes affect playback timing and are inserted as MIDI tempo events at the given beat locations.
- If no tempo is specified, a default of 96 BPM is used.

## Applications

The MidGrid format is designed for use in:
- Compositional sketches
- Algorithmic generation of MIDI data
- Educational tools for voice leading and counterpoint
- MIDI playback engines that interpret grid timing


## Extended Event Section

In addition to the primary grid of notes, a MidGrid file may include a supplemental section that encodes general MIDI events not represented in the note grid. This section begins with a comment line:

```
# events
```

Each subsequent line represents a MIDI event in beat-time format:

```
[beat] <event_type> <key=value> <key=value> ...
```

### Supported Event Types

- `program_change`: e.g. `[12.0] program_change channel=2 program=42`
- `control_change`: e.g. `[2.0] control_change channel=0 control=64 value=127`
- `pitchwheel`: e.g. `[8.0] pitchwheel channel=1 pitch=8192`
- `aftertouch`: e.g. `[5.5] aftertouch channel=3 pressure=90`
- `text`: e.g. `[10.0] text "G major"`
- `sysex`: (optional) e.g. `[15.0] sysex data=F0434C...` (hex or base64)

### Notes

- Beat values may be fractional and align with the main grid.
- These events are emitted by the MidGrid-to-MIDI converter when present in the source file.
- Events in this section are ignored by parsers that focus only on musical notes but may be processed by extended tools.
- `text` meta events may be used to preserve beat-level comments or labels such as key changes, dynamics, or rehearsal marks.

---

This establishes a clear format for storing non-grid events while preserving forward compatibility.
