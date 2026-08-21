# Worked example — Bach, Prelude & Fugue in A minor, BWV 543

Three things this example exists to show: how to get a **notated** source (not a
performance MIDI), how to realize its **ornaments**, and the **pedal-solo
registration** — E. Power Biggs's device of brightening the pedal while it is
exposed, then pushing the stops back before the manuals return.

Generator: `examples/register_bwv543.py`.

## 1. Get a notated source

A performance MIDI is the wrong input for registration: BWV 542's file had the
maker's octave doublings baked in and a channel soup that made the real texture
unreadable. A **score** format gives clean voice/staff separation.

For 543 there is no kern; IMSLP's only MusicXML is a 4-recorder arrangement
(transposed, no pedal staff). The right source is the **LilyPond engraving of the
original organ version** (lekro, after Rust's BGA edition):

    IMSLP Special:ImagefromIndex/376414  ->  PMLP111731-bach_bwv543.zip

(IMSLP is captcha-gated — download it in a browser.) Then:

    convert-ly -e bach_bwv543.ly            # 2015 syntax -> current
    lilypond -dbackend=null bach_bwv543.ly  # -> bach_bwv543.midi (Prelude)
                                            #    bach_bwv543-1.midi (Fugue)

This yields exactly what registration needs: `right:` / `left:` manual staves and
a separate `pedal:` staff, correct notes, **no doublings**. Check that
`time_signature` survives (the Prelude is 4/4, the Fugue **6/8**) — `baroque-agogics`
needs it, and a missing meter silently breaks the agogic breath.

## 2. Realize the ornaments

LilyPond's MIDI does **not** expand ornaments — `\mordent`/`\prall` render as the
plain principal note. The 543 Fugue has 9 (6 mordents, 2 pralls, 1 up-prall; the
Prelude has none), at bars 33/46/60–61/70 and a rising chain at 94–95.

Recompile with `\include "event-listener.ly"` to get a log of every note *and*
articulation with exact times, pair each `script` line with the `note` line
before it, and realize with **midgrid's own C.P.E. Bach engine**
(`kern2midi_ornaments.realize`) — every wavy sign becomes a trill from above,
appui on long notes, on the beat. Splice the figures into the manual note list.

(Why not the MusicXML front-end? It emits a merged *piano* MIDI, which would
destroy the manual/pedal separation. Reusing `realize()` directly keeps both.)

## 3. The registration

```text
Piece: Bach, Prelude & Fugue in A minor, BWV 543
Design: brilliant plenum (NOT the austere Contrapunctus 1 treatment); parsimony
        build in the fugue; pedal solos brightened Biggs-style.

Division    Channel   Prelude                  Fugue
----------  --------  -----------------------  ---------------------------------
Great       ch0 p19   8+4 -> 8+4+2             8' -> 8+4 -> 8+4+2 -> full+16+Mixtur
Pedal flue  ch1 p19   16+8, +4'+2' in solos    16+8 -> +4'+2' (ending solo)
Posaune     ch2 p20   in the pedal solos only  from the final section
Trompette   ch3 p20   --                       final cadence only
```

## 4. The pedal-solo registration (the point)

Find the windows where the **manuals are silent** (test *onsets*, not sustain — a
held manual chord still masks a pedal line):

- **Prelude** — beats 99–111 and 181–187.
- **Fugue** — beats 421–433, the big ending solo.

In the prelude, draw **4′+2′+Posaune** onto the pedal at the solo's start so the
line blazes, then **retract** before the manuals re-enter (at 110/186 — in the
gap, never on a note's attack; same discipline as the 542 chorale switches).

In the fugue the ending solo is different: the manuals return *fortissimo* at 434,
so the brightening **flows into** the final plenum rather than retracting — the
solo becomes the tutti.

## 5. Perform and render

543 is also the worked example for `baroque-agogics` — straight from notation it
is fast and dead-legato. Apply `perform_baroque.py` per movement (Prelude ♩62,
Fugue ♩69, agogic 0.09, cadential rit), then `render_organ.sh`.

**Order: notation → ornaments → registration → agogics → render.**

## Lesson

Where 542 taught *re-registering someone's registration*, 543 teaches *starting
from the score*: a notated source, its ornaments realized by our own period
engine, and a registration device (the pedal solo) that only becomes possible
once the pedal is cleanly separated from the manuals.
