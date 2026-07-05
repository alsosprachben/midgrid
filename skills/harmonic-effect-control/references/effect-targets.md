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

## Recorded Training Example: fugue-cadential-tension-release

From a completed three-voice fugue in D minor. Every section cadence deliberately spikes perceptual complexity on the dominant sonority and releases it at the resolution. The evaluator emits `high_complexity` warnings at these beats; they are correct by design because each spike resolves within one to two beats.

Final cadence (V0 soprano, V1 alto, V2 bass):

```text
81 | A4:1@84  | D4:1@80   | D3:1@86
82 | G4:2@84  | C#4:2@82  | A2:2@84
84 | F#4:4@88 | D4:4@84   | D2:4@90
```

Report trace (V0-V1 pair):

- beat 81: consonant support, complexity under 10
- beat 82: G4 against C#4 is the dominant-seventh tritone, complexity 77 (warning)
- beat 84: resolution by contrary motion (G4 down to F#4, C#4 up to D4), complexity 9

Lesson:

- Place maximum roughness on the pre-cadential dominant and resolve both tritone members by step in contrary motion.
- A `high_complexity` warning is acceptable only when the report shows the complexity collapsing at the next structural beat; an unresolved spike is a defect.
- Read the beat-pair complexity trace after composing a cadence; the spike-then-release shape should be visible in numbers, not just intended.

## Recorded Training Example: complexity-release-repair-001

Attempt (smoothed the second beat, left the pressure source):

```text
0 | F4:1@80 | B3:1@70
1 | A4:1@80 | C4:1@70
2 | E4:1@80 | C4:1@70
```

Evaluator diagnosis:

- `high_complexity` at beat 0: F4 over B3 is a tritone, complexity 77. Editing beat 1 changed nothing about the warning.

Correction (single-cell edit at the source):

```text
0 | F4:1@80 | A3:1@70
1 | G4:1@80 | C4:1@70
2 | E4:1@80 | C4:1@70
```

Complexity trace: 13 (sixth) -> 12 (fifth) -> 9 (third), a monotonic release with no warnings.

Lesson:

- Repair the source of a pressure spike, not its aftermath; prefer the smallest edit that converts the offending interval class.
- Verify release as a declining complexity trace across the phrase, not by ear alone.

## Voice Independence and Fusion

Counterpoint is noise shaping: the vertical dimension distributes roughness over time (the pressure and release targets above), and the horizontal dimension keeps concurrent streams perceptually separate. Parallel motion makes two voices share common fate, and the ear merges them into one stream in proportion to how simple the interval's ratio is. The evaluator's `voice_fusion` diagnostic grades that strength straight from the ratio table: parallel octaves warn from a single transition, fifths from a sustained chain, fourths and tenths surface as information, and imperfect parallels only register as exact chromatic chains. Strength accumulates over the run, so brief blends read differently from a texture that has genuinely lost a voice.

Parallel motion splits by fundamental orientation. Intervals whose just-ratio denominator is a power of 2 (octave 2/1, fifth 3/2, major third 5/4, tenth 5/2) are rooted: the lower note is octave-equivalent to the implied fundamental, so parallel motion merges into one bass-rooted stream (`voice_fusion`) and tenths plane safely. Intervals with an odd factor in the denominator (fourth 4/3, sixths 5/3 and 8/5, minor third 6/5) carry a displaced root, and traveling them drags the unvoiced fundamental along in parallel (`displaced_root_motion`): the reason traveling fourths are avoided while tenths are not, even though 4/3 looks simpler than 5/4. Voicing the displaced root (as the bass under upper-voice fourths, or by the spectral re-basing that distortion performs on power chords) converts the displacement into intent.

Fusion is a knob, not a sin:

- Unintended fusion is the real content of the classical parallel-fifths rule: the texture silently loses a voice. Repair with contrary or oblique motion, exactly as the strict drills teach.
- Intentional fusion is an effect target. Fuse two voices briefly to hand the listener's attention from one line to another; fuse at the octave to thicken a line (registration doubling); sustain a pedal under moving voices (static doubling is never flagged).
- The strict species exercises (`evaluation_defaults.strict_parallels`) keep the categorical rules because over-constraint is good pedagogy; finished pieces are evaluated by the perceptual meta-analysis instead.

When shaping a passage, decide the intended stream count per beat and check the fusion findings against it: independence where you promised independent voices, fusion only where you spend it deliberately.
