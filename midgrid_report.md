

# MidGrid Harmonic Analysis Report Specification

This document specifies the format and conventions used in the output of harmonic analysis performed on MidGrid-structured music data. The report enables structured tracking of harmonic intervals, motion types, and perceptual complexity between polyphonic voice pairs across time.

## Overview

The MidGrid Harmonic Analysis Report consists of beat-aligned sections, each describing the intervallic relationships between voices (typically SATB or other polyphonic configurations) at a given moment in time.

## Format

The report is structured in a human-readable plain text format, with sections beginning with a beat label:

```
Beat 0.00:
  V0–V1: interval=Perfect 4th [phase-aligned], motion=unknown, perceptual_complexity=7.0
  V0–V2: interval=Minor 6th [phase-aligned], motion=unknown, perceptual_complexity=13.0
  ...
```

### Section Header

- `Beat N.NN:`  
  Indicates the exact beat time of the analysis frame.

### Voice Pair Lines

Each line describes the harmonic relationship between a pair of voices (e.g., V0 and V1). The fields are:

- `interval`: The musical interval between the two voices (e.g., "Perfect 4th", "Major 6th", "Tritone"). When the interval spans octaves, this is annotated (e.g., `(+2 oct)`).
- `phase-aligned` (optional): Indicates that the interval harmonics align in phase.
- `motion`: Describes the relative motion of the two voices since the last beat (`parallel`, `contrary`, `similar`, `oblique`, `unknown`).
- `perceptual_complexity`: A floating-point value representing the computed perceptual complexity of the interval, based on harmonic overlap, octave span, and inharmonic decay assumptions.

### Missing Beats

If a beat is listed (e.g., `Beat 6.00:`) with no following lines, it indicates a silent frame or unprocessed analysis window.

## Notes

- Voice indices (V0, V1, V2, etc.) refer to the order of voices as determined by the MidGrid track assignment.
- Interval names follow standard Western tonal terminology.
- The `perceptual_complexity` model is logarithmic and incorporates frequency-domain interference and psychoacoustic decay factors.
- `motion` analysis is best-effort and requires previous beat context. If unavailable, it defaults to `unknown`.

## Example

```
Beat 2.00:
  V0–V1: interval=Perfect 4th [phase-aligned], motion=parallel, perceptual_complexity=7.0
  V0–V2: interval=Major 6th, motion=similar, perceptual_complexity=8.0
  V1–V2: interval=Major 3rd, motion=similar, perceptual_complexity=9.0
```

## Intended Use

This report is intended to support analysis of counterpoint, consonance, and perceptual density in generative or composed MidGrid music. It may serve as input for visualizations, pattern recognition, or further symbolic transformations.