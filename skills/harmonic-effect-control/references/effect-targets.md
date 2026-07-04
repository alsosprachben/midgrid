# Harmonic Effect Targets

Use these mappings when reading `.report.txt` or `.report.json` output from `midgrid_parser.py`. Prefer JSON for automated loops because it exposes `summary`, `beats`, and `pairs` without text parsing.

## Targets

Repose:

- Prefer unisons, octaves, fifths at structural cadences, and consonant thirds/sixths inside phrases.
- Prefer lower perceptual complexity at cadence beats than at preparation beats.
- Use oblique or contrary motion into stable arrivals.

Pressure:

- Increase perceptual complexity over two or more beats.
- Use controlled dissonance or high-register spacing.
- Avoid accidental unresolved harshness unless the target is disruption.

Release:

- Move from higher complexity to lower complexity.
- Resolve stepwise when possible.
- Let the report show a clearer consonance after the tense beat.

Brightness:

- Use upper-register consonant thirds/sixths.
- Keep voices close enough to read as connected, not cluttered.

Density:

- Increase active voice count and moderate interval variety.
- Watch for report clutter: many high-complexity pairings on the same beat.

Austerity:

- Use open perfect intervals sparingly.
- Avoid consecutive perfect parallels.

## Example Diagnosis

Input report excerpt:

```text
Beat 2.00:
  V0-V1: interval=Tritone, motion=similar, perceptual_complexity=77.0
Beat 3.00:
  V0-V1: interval=Major 6th, motion=contrary, perceptual_complexity=8.0
```

Likely effect:

- Beat 2 produces strong pressure.
- Beat 3 releases because complexity drops sharply and motion becomes contrary.

## Example Repair

Before:

```text
0 | F4:1@80 | B3:1@70
1 | G4:1@80 | C4:1@70
```

After:

```text
0 | E4:1@80 | B3:1@70
1 | G4:1@80 | C4:1@70
```

Repair intent:

- Reduce the opening tritone-like roughness.
- Preserve the second beat.
