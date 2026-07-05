---
name: tuning-render
description: Render MIDI files to audio with the adaptive-tuning physical-modeling synthesizer in ../tuning. Use when the user wants MIDI rendered with their own software, with historical temperaments (just, Pythagorean, well-tempered, stretch, Bechstein), adaptive per-chord retuning, or synthesis without soundfonts. Complements the MidGrid pipeline: .midgrid to .mid to .wav.
---

# Tuning Render

Render MIDI to audio with the standalone synthesizer in `../tuning` (sibling of this repo). It parses MIDI itself, synthesizes tones by physical-model families, and retunes all sounding notes whenever the chord changes, using a selectable temperament.

## Quick Start

```bash
# From anywhere; writes output-base.raw and output-base.wav
/home/ben/repos/tuning/render.sh input.mid output-base [tuner]

# Under the hood (raw only; convert with sox):
python3 /home/ben/repos/tuning/midi.py input.mid output-base [tuner]
sox -t raw -r 44100 -b 32 -c 2 -e signed-integer output-base.raw output-base.wav
```

Run `midi.py` with no arguments for usage. Errors abort the run with a message (workers no longer hang the parent).

## Tuners

Pass one of these names as the third argument (default `stretch`):

| Name | Temperament | Reference pitch |
|---|---|---|
| `stretch` | Pythagorean-comma-aligned stretch octaves | A=415 (baroque) |
| `even` | Equal temperament | A=415 |
| `just` | Just intonation (asymmetric scale) | A=440 |
| `pyth` | Pythagorean | A=415 |
| `well` | Well-tempered, deduced from the WTC title-page spiral | A=415 |
| `linearwell` | Well-tempered with linear comma spreads | A=415 |
| `linear` | Linear semitone interval | A=440 |
| `linear5` | Fifths kept in octave, linear offset | A=415 |
| `bechstein` | 1898 Bechstein of Savona Cathedral | A=440 |

All tuners are 12-tone, C-based. Retuning happens adaptively: every time the set of sounding notes changes, the whole sounding set is retuned together.

## What the Renderer Honors

- Note on/off, velocity, tempo changes.
- Program changes select a physical model family, not a soundfont patch:
  programs 1-6 hammered string (Steinway), 7-8 and 25-32 plucked string,
  17-20 flue organ (incl. Church Organ, with pipe inharmonicity tuned to
  the stretched octave), 21-24 and 65-72 reed organ (harmonic partials,
  no chiff), 57-64 brass, 74-80 blown pipe, all else plucked string.
  (Numbers here are 1-based GM programs; MidGrid patch numbers are 0-based,
  so `// Patch V0: 19` = Church Organ = flue model.)
- CC10 pan, applied per note at attack (0 left, 64 center, 127 right),
  on top of a pitch-based soundboard position.
- Spatialization defaults to the Brown-Duda spherical-head model:
  Woodworth interaural delays plus per-partial head-shadow gains (far ear
  loses treble, keeps bass) computed from the source positions at a 2 m
  listener distance. Natural, keeps both channels fed, best on
  headphones; RMS channel balance stays near 0.5 by design, so do not
  judge the image by level meters. `TUNING_HRTF=0` restores the legacy
  amplitude pan law, whose steep curve projects a wider image on
  speakers (+-20 from center is already wide; +-64 nearly one-eared).
- MidGrid `// Pan` and `// Patch` directives therefore carry through.

## Performance and Output

- `render.sh` prefers pypy3 (about 5x faster than CPython; override with
  `TUNING_PYTHON=python3`). Under pypy3 a three-voice 63s fugue renders in
  roughly a minute; under CPython the same took 6m17s. Tell the user the
  expected wait before long renders, and run them in the background.
- Output: `output-base.raw` is headerless stereo, 32-bit signed integer,
  44.1 kHz; `render.sh` also writes `output-base.wav` via sox.
- Progress lines print to stderr every 0.1s of rendered audio. Set
  `TUNING_VERBOSE=1` for the synthesizer's internal debug logging.
- Reverb: pipe through sox with the repo's preset, e.g.
  `sox output-base.wav wet.wav $(/home/ben/repos/tuning/reverb.sh)`.

## MidGrid Pipeline

```bash
python3 midgrid_parser.py piece.midgrid piece.mid   # midgrid -> MIDI + reports
/home/ben/repos/tuning/render.sh piece.mid piece well   # MIDI -> piece.wav, well-tempered
```

Because tuning is adaptive and temperaments are C-based at A=415 for most
tuners, absolute pitch will differ from equal-tempered A=440 renders
(timidity); intervals within chords will sound purer. When comparing
temperaments, render the same .mid with different tuner names into
differently named outputs.
