---
name: baroque-agogics
description: Shape Baroque performance in TIME rather than volume — articulation (separation), agogic accent, tempo and cadential rubato — for fixed-dynamic instruments (organ, harpsichord) rendered in the ../tuning physical-model synth. Use when a render sounds mechanical, too fast, or dead-legato; when asked for expression/dynamics on an organ or harpsichord; when phrasing a fugue or toccata; or when realizing "notes inégales", agogic stress, or a ritardando into a cadence.
---

# Baroque Agogics — expression as time

On the organ and harpsichord you **cannot shade a note's volume**. Every pipe
speaks at the pressure the wind gives it; every pluck is the same pluck. So the
expression that other instruments make with dynamics is made here almost entirely
in **time** — what Harnoncourt called *Klangrede*, "sounding speech."

This is the **time** counterpart to `organ-registration`'s **color**. Registration
chooses *what* sounds; agogics chooses *when*, and that is where the music
breathes.

## The core equivalence

**Separation ≈ softening. Connection ≈ weight.**

More air between events reads as lighter and quieter; fuller note-values and
forward motion read as heavier and louder. The ear trades density for loudness,
so the performer's dynamic shape becomes an articulation-and-timing shape:

| Musical intention | On a fixed-volume instrument |
|---|---|
| *diminuendo* | more separation; broadening (cadential relaxation) |
| *crescendo* | more connection; forward motion, fuller values |
| *sforzando* / accent | **agogic**: lengthen the note (and steal from its neighbour) |
| *piano* passage | shorter sounding-fraction, lighter touch |
| *tenuto* / weight | hold the full value, minimal gap |

Two levers, by instrument type:
- **Sustained (organ)** — the lever is the **release**: a note's *sounding
  fraction* of its written value. Shorten it to add air; hold it full for weight.
- **Plucked (harpsichord)** — the lever is the **space between attacks** and
  **chord spread** (arpégement = emphasis), since the pluck itself is fixed.
  See `references/plucked-instruments.md`; the harpsichord's *registers* (and
  coupling) are drawn stops, handled by `organ-registration`.

## First: does the source already carry a performance?

**Apply this skill to NOTATION. If a source already carries someone's
interpretation, register and render it but leave its timing alone.**

A MIDI transcribed by a performer/arranger often has a real tempo map — rubato,
sectional tempi, a written-out closing ritardando — which *is* an interpretation.
Running the transform over it replaces that phrasing with generated shaping:
silently destroying someone's work and gaining nothing, since the expression is
already there.

Check before shaping:

    tempo events: 1 (or none)   -> notation. Shape it; that is what this skill is for.
    tempo events: many, varying -> a performance. Register and render; do NOT shape.

Worked contrast in this repo: **BWV 543** was compiled from an engraving (no
interpretation at all — so it needs tempo, touch, agogics, phrase shaping, even
editorial ornaments), while **BWV 542** came from Martin Robinson's MIDI with 32
tempo events of his own phrasing — so it gets our registration and physics, and
his rubato is left untouched. Same repertoire, opposite treatment, because the
sources are different kinds of object.

If you want *some* of the layer on a performance source, the articulation
(`--gap-*`) is the safe part — touch is not usually encoded in a tempo map — but
tempo, agogic and rit all belong to the interpreter who is already there.

## Workflow

1. **Read the affect and the rhetoric.** What is the piece's *Affekt*? Where are
   the phrases, the sentences, the punctuation? Baroque music is speech
   (`references/time-as-dynamics.md`).
2. **Choose the tempo.** Unhurried. A fast tempo is the commonest way to destroy
   Baroque expression: it leaves no room for the articulation and agogics that
   carry it. Prefer too slow to too fast; let the piece's shortest note values
   still speak.
3. **Choose the touch** — the *ordinary* (non-legato) articulation, and where it
   varies: heavier/more connected in weighty passages, lighter/more separated in
   soft ones. This is your dynamic plan.
4. **Set the metric hierarchy.** Which beats are "good" (strong) and which "bad"?
   The agogic breath lengthens the good ones so the meter is *felt*, not counted.
5. **Plan the punctuation** — broadening into cadences (sectional as well as
   final); forward motion out of them.
6. **Realize as timing** (`references/performance-bridge.md`): apply
   `examples/perform_baroque.py`; leave velocity flat. Two of its knobs are easy
   to read backwards, and both mistakes sound like heavy rubato:
   - `--rit-amount` is a **multiplier on beat length**, not an amount to slow by.
     `1.6`–`2.0` is a cadential broadening; anything **below 1.0 accelerates**
     into the close.
   - `--tension` lengthens **every beat carrying a sounding dissonance**. In
     chromatic writing that is most beats, so it belongs at `0.02`–`0.03`. At
     `0.4` the music lurches continuously.
   The script now warns on both, but the warning is a backstop, not a licence to
   guess.
7. **Record the settings that were approved by ear, and re-use them.** A tempo
   and shaping plan that has passed a listening test is a result; re-deriving it
   from scratch discards that result and usually lands somewhere worse. For the
   organ corpus they live in the `WORKS` table of
   `organ-registration/examples/render_work.py`, one entry per work.
8. **Judge by ear.** Does it speak? Does the meter breathe without seasickness?
   Do the cadences land? Never let the shaping be *noticeable as an effect*.

## Rule Priority

1. **Legibility of the line** — articulation must clarify the counterpoint, never
   chop it up.
2. **The meter must be felt** — a listener should sense the downbeat without
   being told; that is the agogic's job.
3. **Tempo that allows speech** — if the ornaments, the articulation, or the
   cadential broadening have no room, the tempo is wrong.
4. **Punctuation** — phrase- and section-ends are *heard* as ends.
5. **Proportion** — the shaping is felt, not noticed. Over-agogics sounds drunk;
   over-separation sounds staccato and prissy.
6. **No volume dynamics** — on a fixed-dynamic instrument, velocity stays flat.
   If you reach for velocity, you have given up on the idiom.

## Output Pattern

State the performance plan before realizing it:

```text
Piece: <name / meter / form>
Affekt: <one line>

Movement     Tempo   Touch (gap)      Agogic   Cadences
-----------  ------  ---------------  -------  ---------------------------
Prelude      q=62    ordinary .22     0.09     rit last 6 beats x1.7
Fugue (6/8)  q.=69   ordinary .22     0.09     rit last 8 beats x1.9
```

Then apply the transform. If the user wants only the plan, output only the table.

## References

- `references/time-as-dynamics.md` — the model: why time *is* dynamics here,
  the metric hierarchy (good/bad notes), agogic accent, cadential rubato.
- `references/treatise-sources.md` — the grounding: C.P.E. Bach, Quantz, Türk,
  Couperin, Frescobaldi, and Harnoncourt's modern synthesis.
- `references/performance-bridge.md` — the executable bridge: intention →
  concrete timing transform, every parameter and what it does to the sound.
- `examples/perform_baroque.py` — the transform (tempo, articulation, agogic
  breath, cadential rit), warping all events through one monotonic time-map.
- `references/plucked-instruments.md` — the harpsichord side: arpégement
  (spread as accent), notes inégales, and registers/coupling as drawn stops.
- `references/performance-bwv543.md` — worked example: Bach's A minor P&F.
