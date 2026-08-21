# The executable bridge — intention → timing

How an expressive intention becomes a concrete transform on the MIDI, for the
`../tuning` fixed-volume renderer. The tool is `examples/perform_baroque.py`.

    perform_baroque.py IN.mid OUT.mid [--bpm 63] [--gap-frac 0.22] [--gap-cap 0.13]
        [--gap-min 0.03] [--agogic 0.09] [--rit-beats 8] [--rit-amount 1.8]

**Velocity is never touched.** On a fixed-dynamic instrument, expression that
shows up in velocity is a bug.

## How it works

Everything is one **monotonic time-map** (beat → performed seconds), and *every*
event is warped through it — notes, registration CCs, ornament figures. So a
tempo/agogic change can never desync the registration switches or the trills.
Note-offs are then pulled in from the warped value to make the articulation gap.
Output carries a fixed tempo; the warped tick positions are the performance.

## The parameters

### Tempo — `--bpm`
The base tempo in written beats. **Choose it first and choose it slow** (Quantz:
the shortest note-values must still speak). Toccata/prelude figuration and fugue
subjects need room for their articulation; if a run sounds like a smear, the
tempo is wrong before anything else is.

### Touch — `--gap-frac`, `--gap-cap`, `--gap-min`
The *ordinary* (non-legato) articulation. Each note releases early, leaving
silence:

    gap = clamp(gap_frac * performed_duration, gap_min, gap_cap)

- **`gap-frac`** (default 0.22) — the fraction of a note's own value given to
  silence. This is the **dynamic lever**: raise it for a lighter/softer passage,
  lower it for weight. (C.P.E. Bach's "about half value" would be ~0.5, which is
  a very detached, small-room touch; 0.15–0.30 suits an organ in a resonant
  space, where the room supplies connection.)
- **`gap-cap`** (default 0.13 s) — the maximum silence. Without it, long notes
  would leave gaping holes; with it, whole notes keep nearly their full value
  while short notes still separate. **This is what keeps runs connected and gives
  weighty notes air** — the value-scaled touch.
- **`gap-min`** (default 0.03 s) — always some air, so nothing is truly legato.

### Agogic breath — `--agogic`
Depth of the metric lengthening (0 = off, 0.09 typical, >0.15 gets seasick). The
meter's strong beats are given proportionally more time, **mean-preserving** over
the bar so the tempo does not drift. Profiles are derived from the MIDI's time
signature:

- **Simple meters** — 4/4 is weighted 1.0 / 0.3 / 0.6 / 0.3 (beat 1 ≫ 3 > 2, 4);
  3/4 is 1.0 / 0.3 / 0.5; 2/2 is 1.0 / 0.5.
- **Compound meters** — 6/8, 9/8, 12/8 use dotted-quarter beats, with the bar's
  first beat strongest, a lift on the third eighth (the lead-in to the next beat),
  and the mid-bar beat secondary. This produces the compound *lilt* — a gigue
  fugue in 6/8 must swing on its two beats, not on four quarters.

**The MIDI must carry its `time_signature`**, or the transform assumes 4/4 and
the breath lands on the wrong beats (a real bug we hit: a 6/8 fugue breathing in
4/4 sounds subtly wrong everywhere). Anacrusis is assumed absent — tick 0 is a
downbeat; shift the source if not.

### Cadential broadening — `--rit-beats`, `--rit-amount`
A smoothstep ritardando over the last `rit-beats` beats reaching `rit-amount`×
slower. Rubato *as* the diminuendo. 1.7–1.9× over 6–8 beats reads as a real close
without sounding like a tape slowing down. Apply per movement (run the tool on
each movement separately, then concatenate) so internal movement-ends broaden too.

### Phrase-aware shaping — `--phrase`, `--density-damp`, `--tension`

A player does not breathe identically in every bar. Three signals read from the
score (`analyze_score`) make the base agogic respond to the music:

- **`--phrase`** (0.09–0.16) — broaden approaching a phrase end, re-gather after.
  Boundaries are found **per voice** (a rest, or a note long for that voice) and
  then pooled, because in real counterpoint the *aggregate* onset stream never
  stops — when one voice rests the others cover it, which is what fugal writing is
  FOR. Looking for gaps in the whole texture finds nothing. **Voices phrase;
  textures rarely do.** Candidates are scored continuously and the strongest are
  kept at a musical *rate* (~1 per 4 bars) rather than by a threshold, which makes
  the detector behave consistently across a resting fugue and a seamless
  4-part texture alike. Use MORE in improvisatory music (a toccata, prelude,
  fantasia — Frescobaldi's flexible time) and LESS in a driving fugue.
- **`--density-damp`** (0.7–0.85) — damp the metric breath where the texture runs
  fast. Passagework should flow, not be stressed beat by beat.
- **`--tension`** (0.02–0.03) — lean on a sounding dissonance (m2/M2/tritone/7th).
  A dissonance is a "good note" wherever it falls. (Vertical dissonance only; true
  suspension detection, with resolution tracking, is not implemented.)

These are heuristics, not analysis: they find *plausible* boundaries, not
analytically correct ones. All default to 0, i.e. the uniform behaviour.

### Editorial performance — `--cadential-trills`, `--figuration-hold`

A Baroque player did more than the page shows. Both of these are **opt-in** and
report what they did, because they change the notes.

- **`--cadential-trills`** — a trill on the penultimate note at detected cadences,
  realized by midgrid's C.P.E. Bach engine (trill from above, appui on long notes,
  on the beat). Conservative: top voice only, only a note long enough to hold a
  trill, only a stepwise close (the 4-3 / 2-1 formula). Note that in a merged
  registration MIDI "the previous note in the track" is *not* "the previous note in
  the voice" — the penultimate is found by melodic proximity instead.
- **`--figuration-hold BEATS`** — broken-chord figuration carries an implied inner
  voice (the lowest note of each beat-group) that the ear hears as held. Sources
  often write it out in some bars and abbreviate it in others; E. Power Biggs
  famously continued BWV 543's every-other-bar alternation through its triplet runs.

  **The rule: continue a pattern only where the source establishes one, and only
  as long as the texture that carries it lasts.** Concretely it requires an
  alternation of >= 3 held bars of one parity, every other bar, and it extends only
  within that section (the piece is segmented into contiguous runs of one
  subdivision — a triplet run and a 16th run are different music). Irregular held
  inner voices elsewhere are left alone: inventing more of a pattern than the
  composer established is composing, not performing.

## Recipe

1. Register the piece first (see `organ-registration`), keeping the
   `time_signature` in the output.
2. Run `perform_baroque.py` per movement with the chosen tempo/touch/agogic/rit.
3. Render with `organ-registration/examples/render_organ.sh` (which adds the
   cathedral reverb and headroom).
4. Judge by ear: does it speak; does the meter breathe; do the cadences land;
   is the shaping *unnoticeable as an effect*?

## Known limits (worth extending)

- **Phrase detection is a heuristic**, not analysis. It ranks note-ends by how much
  a voice breathes and keeps the best at an imposed rate (~1 per 4 bars); the rate
  is assumed rather than discovered, and a piece that phrases irregularly will be
  shaped evenly regardless. Inspect what it found (the tool prints the count).
- **Tension is vertical dissonance only** — no resolution tracking, so a true
  suspension is not distinguished from any passing dissonance, and a phrase PEAK
  (the melodic high point) is not stressed at all.
- Only **sectional/final** rit is available (per movement); internal cadences
  broaden only through the phrase bumps, not a real rit.
- **Editorial features assume a well-formed source**: `--figuration-hold` needs the
  pattern established early and regularly, and `--cadential-trills` needs the
  cadence to offer a trillable stepwise penultimate. Both no-op quietly otherwise.
- **Anacrusis is assumed absent** (tick 0 = downbeat) throughout.
