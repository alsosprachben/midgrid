# Worked example — Bach, Prelude & Fugue in A minor, BWV 543

The first piece shaped with this skill, and a good demonstration because the two
movements need *different* treatment in every parameter.

## The problem

Rendered straight from the notation (LilyPond → MIDI), it was **fast and
dead-legato**: every note its full written value, every beat exactly equal, no
punctuation. On a fixed-volume organ that is maximally expressionless — none of
the three expressive channels was being used. It sounded mechanical *because*
nothing had room to speak, not because anything was wrong with the notes.

## The plan

```text
Piece: Bach, Prelude & Fugue in A minor, BWV 543
Affekt: Prelude — brilliant, improvisatory toccata; Fugue — a driving 6/8 gigue.

Movement       Meter  Tempo  Touch (gap-frac)  Agogic  Cadence
-------------  -----  -----  ----------------  ------  ------------------
Prelude        4/4    q=62   ordinary 0.22     0.09    rit 6 beats x1.7
Fugue          6/8    q=69   ordinary 0.22     0.09    rit 8 beats x1.9
```

    perform_baroque.py bwv543_prelude_organ.mid prel_perf.mid \
        --bpm 62 --rit-beats 6 --rit-amount 1.7 --agogic 0.09
    perform_baroque.py bwv543_fugue_organ.mid  fug_perf.mid \
        --bpm 69 --rit-beats 8 --rit-amount 1.9 --agogic 0.09

Then render each movement, concatenate with ~2 s between (the cathedral tail of
the prelude rings into the fugue), and reverb the whole.

## Why these values

- **Tempo down from ♩80 to 62/69.** The LilyPond default was brisk; the toccata's
  32nd-note figuration and the fugue's ornaments had no room. Quantz's test — the
  shortest values must still speak — chooses the tempo, not the "usual" speed.
- **Touch 0.22 with a 0.13 s cap.** In a wet cathedral the room supplies much of
  the connection, so a modest gap suffices; the *cap* is what matters, keeping the
  running passagework nearly connected while quarters and pedal notes get real
  air. (A dry room would want more separation.)
- **Agogic 0.09 in both, but very different results.** The prelude leans on the
  4/4 hierarchy (1 ≫ 3 > 2, 4). The fugue is **6/8** — a compound gigue — so it
  lilts on its two dotted-quarter beats. Same number, different *feel*, entirely
  from the meter profile.
- **Bigger rit for the fugue** (1.9× over 8 beats vs 1.7× over 6): a full-plenum
  fugal close carries more energy to dissipate than the prelude's cadence.

## The bug worth remembering

The fugue first came out breathing in **4/4** — because the registration
generator hadn't carried the source's `time_signature` into its output MIDI, so
the transform defaulted to 4/4 and put the agogic stress on the wrong beats. The
result wasn't obviously "wrong", just subtly unsettled everywhere. **Always
verify the meter the transform reports** (it prints e.g. `6/8 agogic 0.09`), and
make registration generators preserve `time_signature`.

## Interaction with the other skills

- **Registration** (`organ-registration`) is applied *first*; the transform warps
  its CC events along with the notes, so terraced changes and the pedal-solo
  brightening stay exactly where they belong.
- **Ornaments** are realized *before* the transform, so their figures stretch
  with the tempo and broaden with the cadential rit — as a player's would.
- **Rendering** is `render_organ.sh` afterwards.

Order: **notation → ornaments → registration → agogics → render.**
