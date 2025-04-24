# MidGrid Format Specification

The MidGrid format is a compact, human-readable grid-based notation for specifying MIDI events across multiple voices in a polyphonic composition. It is designed to be easily parsed by programs and editable by musicians or developers.

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

### Symbols

- A pitch is written as a note name followed by an optional octave shift:
  - Examples: `C4`, `D#3`, `G5`, `Bb`
- A held note is represented by `-` (continuation of the previous pitch).
- A rest or silence is represented by `.` or space.
- Optional **velocity** (volume) is encoded with `@` suffix:
  - Example: `C4@90`
- Optional **duration** (in beats) is encoded with `:` suffix:
  - Example: `E4:1.5` (plays for 1.5 beats)
- Velocity and duration can be specified independently or together using either `@`, `:`, or both suffixes:
  - Examples: `D#4@80:1.0`, `G3:0.5@100`
- Optional **instrument patch** (MIDI program number) is encoded with `~` suffix:
  - Example: `G3~41`
- Multiple properties may be chained in any order:
  - Examples: `C4@100:1.5~23`, `C4~23:1.5@100`

### Example

```
# Title: Fugue Example
# Tempo: 90

V0: C4   -    -    D4   -    -    E4   -    -    F4   -    -    
V1: G3   -    -    A3   -    -    B3   -    -    C4   -    -    
V2: .    .    C3   -    -    .    D3   -    -    .    E3   -    
```

## Notes

- All voices must contain the same number of columns (use `.` or `-` to pad).
- Columns may be subdivided by measure with visual guides (`|`) for readability.
- Grid spacing may be adjusted for visual alignment but must maintain consistency within a line.
- The parser accepts chained note modifiers in any order and parses them according to suffix symbols.

## Applications

The MidGrid format is designed for use in:
- Compositional sketches
- Algorithmic generation of MIDI data
- Educational tools for voice leading and counterpoint
- MIDI playback engines that interpret grid timing

## Future Extensions

- Channel/Instrument mapping per voice
- Microtonal pitch notation
- Multiple per-note properties: velocity, duration, patch
- Tied notes and slurs
