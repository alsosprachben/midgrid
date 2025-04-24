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
- Optional velocity can be encoded as a suffix: `C4:100`
- Optional duration can be inferred by contiguous `-` following a pitch event.

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

## Applications

The MidGrid format is designed for use in:
- Compositional sketches
- Algorithmic generation of MIDI data
- Educational tools for voice leading and counterpoint
- MIDI playback engines that interpret grid timing

## Future Extensions

- Channel/Instrument mapping per voice
- Microtonal pitch notation
- Explicit duration encoding
- Tied notes and slurs

