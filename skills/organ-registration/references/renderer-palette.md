# Renderer palette — the executable bridge

How a drawn stop becomes sound in `../tuning`. The engine is a monotimbral
physical-model additive synth: one note-on → one voice. So a **stop = a voice
class (chosen by GM program) + a pitch transposition**, and a **chorus = the
same note emitted several times, transposed, one rank per channel**. The
renderer resolves the voice class from the channel's *live* program at
note-attack (`midilib.py`), so program changes mid-piece re-register on the fly.

## Family → voice class → GM program

Voice classes are defined in `../tuning/tonelib.py`; the GM→class routing is
`../tuning/patch_map.py`. Pick the program to select the class:

| Stop family (Geer) | Voice class | Program(s) | Character in the model |
|--------------------|-------------|-----------:|------------------------|
| **Principal / Diapason** (chorus, mixtures) | `FlueOrganProperties` | 16–19 | full spectrum, octave-emphasis, **dynamic inharmonicity → locks to `hybrid`** |
| **Flute** (Gedackt, Rohrflöte) | `BlownPipeProperties` | 72–79 | odd-only, near-sine, soft & round |
| **String** (Gamba, Salicional) | `BowedStringProperties` | 40–44 | 1/n saw-ish, keen, subtle shimmer |
| **Solo / colour reed** (Dulzian, Krummhorn, Vox Humana) | `ReedOrganProperties` | 20–23, 64–71 | odd-only, hollow, phase-locked, no chiff |
| **Chorus reed** (Trumpet / Trompette 8′) | `BrightBrassProperties` | 56 (57,59) | bright, edgy, tongued "rip" — cuts through a pleno |
| **Pedal reed** (Posaune / Bombarde 16′) | `DarkBrassProperties` | 58 (60) | round, dark, slower speech — gravity without edge |

Notes:
- Use **FlueOrgan (19)** for *all* principal/mixture ranks — it is the only
  organ voice with dynamic inharmonicity, so under `hybrid` tuning its octave
  partials lock to the tuner's stretched octaves instead of beating. The other
  organ voices are phase-locked (harmonic), which is fine for reeds/flutes.
- **Brass = reeds** here: the tongued attack and full/ bright spectrum read as
  organ chorus reeds. Bright = manual Trompette; Dark = pedal Posaune.

## Footage → transposition (semitones)

A rank sounds at a fixed interval from the key; emit the note transposed:

| Stop | Semitones | | Stop | Semitones |
|------|----------:|-|------|----------:|
| 16′  | **−12** | | 2⅔′ (Quint) | **+19** |
| 8′   | **0**   | | 2′ (Super)  | **+24** |
| 4′   | **+12** | | 1⅗′ (Tierce)| **+28** |
|      |         | | 1⅓′ (mixture)| **+31** |

A **Mixture** = a stack of the upper octave/fifth ranks (e.g. +19, +24, +31)
at low velocity. Clamp transposed notes to MIDI 0–127.

## Realization recipe

1. **One rank per channel**, program set once at tick 0 (a rank keeps one voice
   for the whole piece). Only 0–7 are used by a typical SATB source, but you
   own all 16 — spend them on ranks.
2. **Divisions:** route the bass/pedal line's ranks to their own channels
   (Pedal), the upper voices' ranks to others (Great/Positiv). Independence =
   separate channels/programs, exactly like separate divisions.
3. **Pyramid via velocity:** 8′ at (near) source velocity; 4′ ~0.85; 2′/2⅔′
   ~0.6; mixtures lower; a solo reed *above* its accompaniment. This both
   models the pyramid and controls level.
4. **Terrace by section:** to change registration at a section tick, either
   change the channel's `program` there, or simply **start/stop emitting a
   rank's notes** at that tick (a stop drawn/retired). Gate low pedal ranks
   (16′/Posaune) to real pedal notes (e.g. source note ≤ G3) so high bass
   flourishes don't get a subsonic doubling.

## Worked stop recipes

- **Organo Pleno (Great):** FLUE 19 @ 0, +12, +19, +24 (vel 1.0/0.85/0.62/0.62).
- **Positiv 8′+4′ (lighter chorus / fugue):** FLUE 19 @ 0, +12.
- **Flute solo + accompaniment:** BlownPipe 74 @ 0 (solo, louder) over FLUE 19
  @ 0 quiet on another division.
- **Pedal foundation:** FLUE 19 @ −12 (16′) + @ 0 (8′), + DARK 58 @ −12
  (Posaune 16′) at pillars.
- **Grand close:** Great pleno + BRIGHT 56 @ 0 (Trompette 8′); Pedal 16′+8′+
  Posaune.

## Tuning, reverb, and the clipping ceiling

- **Tuning:** `hybrid` for Baroque (meantone-quality thirds; principals lock).
  See `$tuning-render` and the [[hybrid-tuner-for-baroque]] memory.
- **Reverb:** organs get the **hall**, not the piano chamber —
  `sox DRY OUT vol <V> pad 0 5 reverb 100 20 100 100 0 -9` (see
  [[reverb-by-voice]]).
- **Density is the ceiling.** A full pleno on several voices is many
  simultaneous ranks — it *will* clip if `vol` is too hot. After reverb,
  **always** run `sox FILE -n stats` and require **Flat factor 0.00**; if not,
  lower `vol` (dense pleno often needs ~0.5), thin the upperwork, or append
  `gain -n -1`. Loud is built from the *pyramid and the reed*, not from `vol`.
