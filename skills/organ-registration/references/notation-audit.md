# What the engravings mark, and what reaches the audio

An audit of all 111 Mutopia Bach organ engravings, run because the same failure
kept surfacing one item at a time: notation that MIDI cannot carry was reaching
the render only when Ben noticed its absence by ear. Ornaments, then fermatas,
then arpeggios — each found the same way. This is the systematic version of that
search, so the remaining gaps are known rather than discovered.

Method: every work's event-listener log was regenerated with the current
listener (111/111, no empty logs), and the converted sources were surveyed for
constructs the log does not report. Counts below are corpus totals.

## Carried by LilyPond's MIDI — nothing to do

| element | instances | works |
|---|---|---|
| ties | 6598 | 110 |
| tuplets | 293 | 18 |
| grace / appoggiatura / acciaccatura | 117 | 22 |
| metronome tempo marks | 172 | 44 |
| dynamics | 5 | 1 |

## Recovered from the listener log — handled

| element | instances | works | how |
|---|---|---|---|
| stems | 135283 | 111 | `read_stems` — identifies the sustained voice |
| fermatas | 473 | 88 | markers → held at the note's tail |
| ornament signs | 718 | 58 | C.P.E. Bach engine; prall and mordent kept distinct |
| arpeggio | 3 | 2 | markers → rolled across manuals |

Ornament signs seen: prall 382, prallprall 119, mordent 104, trill 46,
prallmordent 18, downprall 15, turn 11, upprall 9, downmordent 8, upmordent 3,
prallup 2, lineprall 1. `prallup` was missing from the sign table and is now
mapped; it was the only unhandled sign in the corpus.

## Found broken by the audit — fixed

**`\repeat volta` is not played in MIDI.** Verified directly: `\repeat volta 2
{ c d e f } g1` yields 5 note-ons, `\repeat unfold` yields 9. The converter now
rewrites volta as unfold, which is what `\unfoldRepeats` does and which survives
`\alternative` correctly.

The first count here was wrong and worth recording as a caution: 29 works contain
`\repeat volta`, but **27 of them already wrap it in `\unfoldRepeats`** — the
typesetters had handled it. Only **2 works, 7 repeats**, were genuinely affected
(BWV 625 and BWV 645 *Wachet auf*). Counting the construct rather than the
condition overstated the problem twentyfold.

**The agogic bar grid ignored the anacrusis.** `perform_baroque` assumed tick 0
was a downbeat — a comment in it even said so, scoped to the one piece it was
written for. **42 of the 111 works open with a `\partial`** (22 with a quarter,
10 with a half, 8 with an eighth, 2 others). For all of them the metric breath
was lengthening the wrong beats: the music still breathed, but against the meter
rather than with it. `--anacrusis` now shifts the grid, and the converter records
each work's pickup in quarter notes.

## Found by the audit — NOT yet handled

**Slurs: 2341 across 36 works.** A slur is a legato instruction, and the touch is
applied uniformly: every note gets the same `--gap-frac` separation whether or
not the score groups it. On a fixed-volume instrument, where separation *is*
dynamics, ignoring slurs flattens exactly the shaping this skill exists to
produce. The log gives start/stop flags on the preceding note, so the data is
there. This is the largest remaining gap.

**Articulation marks: 550 staccato across 6 works**, plus 10 breath marks in one.
Same mechanism, smaller reach.

**Polyphony sharing a MIDI channel: 66 `<< \\ >>` splits across 18 works.**
`midi-voice-channels.ly` puts each voice on its own channel and `read_notes`
pairs by channel, but the corpus was not converted with it. Where two voices in
one staff briefly share a pitch, their durations swap.

## Things that turned out not to matter

- **`text` events (297 across 48 works)** are fingerings and analysis marks —
  "q", "//", "4-5", "Choral". Nothing sounding.
- **`rtoe` / `lheel` (260 across 5 works)** are organ pedalling marks: right toe,
  left heel. They describe technique, not sound.
- **No hairpins, no `\ottava`, no glissandi, no textual tempo marks** anywhere in
  the corpus except BWV 565's `Adagio`/`Prestissimo`, which are already handled
  (they are what broke the stock listener).
