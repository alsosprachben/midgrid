# The plucked side — harpsichord agogics

On a harpsichord the plectrum plucks with a **fixed force**: touch cannot make a
note louder. So the expressive levers are different from the organ's, though the
principle (`time-as-dynamics.md`) is identical.

| Lever | Organ | Harpsichord |
|---|---|---|
| primary | **release** (sounding fraction) | **space between attacks** |
| accent | agogic length | **spread (arpégement)** + agogic length |
| color/weight | drawn stops | **engaged registers** (see below) |
| shaping | articulation, agogic, rubato | the same, plus **notes inégales** |

## Arpégement — spread as the accent

`--spread MS [--spread-dir up|down] [--spread-accent]`

Couperin's *arpégement*: the notes of a chord are **rolled**, not struck together.
Because the pluck itself is fixed, **how widely a chord is spread is how strongly
it is accented** — and a spread chord also sustains better, since the notes decay
from staggered starts. This is the harpsichord's forte.

- **`--spread`** — milliseconds between successive notes of a chord. 15–30 ms is a
  normal expressive roll; 40+ is a big rhetorical gesture (a *grand* arpeggio at
  a final cadence); under 10 ms is barely more than a "together" chord.
- **`--spread-accent`** — scale the roll by the **metric weight**, so downbeats
  roll wider than weak beats. This is what makes spread function as accent rather
  than as a mannerism.
- **`--spread-dir`** — up (default) or down. Upward is the norm; downward is a
  special colour (and, historically, sometimes notated).

Implementation notes: rolls are collected **globally across tracks**, so a chord
divided between the hands/staves rolls as *one* gesture. Only the onsets move —
the note-offs stay put, since the hand lifts together.

## Notes inégales — the French inequality

`--inegales R [--inegales-div N]`

In French practice, stepwise subdivisions are played **long-short** rather than
evenly. `R` is the first note's share of the pair: `0.5` = equal (off), `0.60` =
*lourer* (a gentle lilt), `0.667` = a sharp 2:1 *pointer*. `--inegales-div` sets
how many subdivisions per beat are made unequal (2 = eighths against a quarter
beat).

Implemented as part of the **time-map** rather than per-note surgery: the beat
boundaries are fixed points of the warp, so longer values are untouched and every
voice stays automatically consistent (a quarter against inégal eighths still lands
where it should).

**Apply it idiomatically**: inégales is a French convention for specific
repertoire and specific note-values — *not* a global groove. It is wrong in most
German and Italian music. When in doubt, leave it at 0.5.

## Overholding — *style brisé*

`--overhold BEATS`

*Style brisé* / *style luthé*: the fingers **hold keys past the written value** so
a broken chord accumulates into a sounding harmony — the lute-derived texture at
the heart of the French unmeasured prelude. Each note is held up to `BEATS`
longer, but never past the next strike of **its own pitch** (a string can only
sound once), so the texture clears itself as the harmony moves.

**This is not a sustain pedal.** A harpsichord has none: its dampers ride on the
jacks, one per key, and no mechanism lifts them all. (The renderer implements no
CC64 either.) Overholding is therefore purely a matter of note *duration* — which
is exactly what the fingers do — and needs no MIDI feature beyond longer notes.
The one genuine MIDI constraint is overlapping the *same* pitch; the engine
ref-counts re-attacks, and the transform stops a held note short of its own next
onset regardless.

Use 2–4 beats for a rich brisé texture; smaller values just thicken the legato.
It overrides the articulation gap where they conflict (a held note is not also a
separated one).

## Registers, and coupling

The harpsichord is a **registered** instrument, exactly like the organ: no
dynamics, so you change the sound by engaging whole **choirs** of strings. It
therefore reuses the same registerable/CC11 machinery — see
`organ-registration/references/renderer-palette.md`:

- bit 0 = **8′ lower manual** (plucked further from the nut: round)
- bit 1 = **8′ upper manual** (plucked near the nut: nasal, bright)
- bit 2 = **4′ choir**
- bit 3 = **lute/buff stop** (pads damp the strings: dry, dull, short)

**Coupling is simply drawing both 8′ choirs** (`0b0011`) — which is mechanically
what a coupler does. `0b0111` (both 8′s + 4′) is the full *grand jeu*. Register
changes are terraced by section, exactly like organ registration, and they are the
harpsichord's only "dynamics" — which is why the agogic levers above carry the
rest of the expression.

GM programs **6 and 7** route to the harpsichord voice.
