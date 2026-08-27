#!/usr/bin/env python3
"""Registration of Bach, Toccata and Fugue in D minor, BWV 565 -- TWO MANUALS.

Source: the Mutopia LilyPond engraving, compiled by mutopia_to_midi.py. Being
notation it takes the FULL treatment: ornaments and fermatas recovered from the
event-listener log, registration here, then baroque-agogics.

WHY TWO MANUALS, AND HOW THE DIVISION WAS DECIDED. The engraving separates the
hands properly -- `\\context Staff = "RH"` and `= "LH"` -- and the earlier version
of this file merged both onto one Great channel, discarding that. What it does
NOT contain is any manual indication: no Oberwerk, no Rueckpositiv, no
registration marks of any kind, and its own header names its source as the
Bach-Gesellschaft Ausgabe of 1867. BWV 565 has no autograph at all (the earliest
source is Ringk's copy), so manual changes in it are editorial by nature.

Stem direction does not supply them either, though it was worth checking: all
3433 manual stems in this engraving are explicit, and in the RH staff the
stem-DOWN notes have a HIGHER median pitch than the stem-up ones (73 vs 69),
which is the ordinary rule of pointing stems away from the middle staff line --
layout, not voicing.

So the two-manual plan is derived from the notes themselves, and only where they
actually ask for it:

  * The ECHO at bars 14-15. The RH figure of bar 14 returns in bar 15 transposed
    exactly -12 semitones, over an LH figure that repeats note for note. That is
    a written echo, and the one place in the piece where the notation itself asks
    for a manual change. Both hands drop to a bare 8' for bar 15 and return.
  * The FUGUE'S ECHOES, found the same way and not by stems, which mark vertical
    position rather than manual. Inside the 28-bar manualiter span (bars 58-85,
    pedal silent) the music restates itself literally every HALF BAR: the right
    hand from bar 62 to 70, then the left from 73.5 to 81. Sixteen such pairs, all
    exact repeats of rhythm and pitch. That is an echo passage, and an organist
    plays the statement on the main manual and the answer on the softer one --
    which is a change of MANUAL, not of stops, so we route the answer half-bars
    to the Rueckpositiv rather than re-registering mid-phrase. The routing is by
    role, not by hand: during the left hand's echoes its statements take the
    Oberwerk too, because the statement always belongs on the main manual.
  * Everywhere else the manuals carry the SAME registration, which is what
    coupling is. Two manuals is not the same as two colours all evening; the
    toccata's chords and the peroration want one weight, not a dialogue.

  Oberwerk    ch0 p19 flue  <- RH     8+4+2 -> chords -> lean (fugue) -> plenum
  Rueckpositiv ch1 p19 flue <- LH     coupled, except the echo and the manualiter
  Pedal       ch2 p19 flue  <- pedal  16+8; brightened for the pedal solo
  Posaune     ch3 p20 reed  <- pedal  toccata chords, pedal solo, coda
  Trompette   ch4 p20 reed  <- RH+LH  Great Trompette, peroration only
"""
import mido, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reglib import (read_notes, make_channel_track, conductor,
                    read_ornament_log, realize_ornaments, apply_ornaments,
                    read_fermatas, find_echoes, split_echoes,
                    read_arpeggios, big_chords, read_stems, hold_stem_voice,
                    F8, F4, F2, F223, F16, F513, FLUTE, MIXTUR, R8, R16, TRUMPET,
                    PLENUM, PEDAL_FOUND)

SRC = os.environ.get("BWV565_SRC",
                     os.path.expanduser("~/Downloads/mutopia-bach-midi/ToccataFugue.mid"))
DST = os.path.expanduser("~/Downloads/bwv565_organ.mid")
# Ornaments AND fermatas live only here -- MIDI carries neither.
ORN_LOG = os.environ.get("BWV565_NOTES", os.path.expanduser(
    "~/Downloads/mutopia-bach-midi/ToccataFugue.work"))

RH_TRACK, LH_TRACK, PEDAL_TRACK = 1, 2, 3

# D minor, HARMONIC -- the leading tone is C#, which the opening flourish spells
# out itself (a g f e d cis d).
D_MINOR = {2, 4, 5, 7, 9, 10, 1}

# --- section beats (4/4, so bar = beat/4 + 1) --------------------------------
DECLAIM   = 12     # bars 1-3: the opening declamation is ONE gesture on ONE
                   # manual. It is an unharmonised flourish doubled at the octave
                   # and answered twice a register lower; routing it by hand put
                   # the lowest answer on the other division, so the three
                   # statements no longer matched each other.
ARP_IN    = 52     # bar 14: the broken-chord figure with its repeated inner note
ARP_OUT   = 80     # bar 21: ...ends
T_CHORDS  = 104    # bar 27: the toccata's weighty chords ACTUALLY begin here --
                   # measured, not assumed. The old value (bar 17) sat in the
                   # middle of the running figure: bars 14-26 carry no sustained
                   # chord at all, and the first two land in bars 27-28.
FUGUE     = 118    # the seam, found from where the SUBJECT enters rather than
                   # from a bar number. It enters at 118.25 -- `a g a f a e a d`,
                   # the alternation against the repeated A -- after a 16th rest.
                   # The old value of 116 cut the toccata's own final cadence in
                   # half: the resolving D minor chord begins exactly at 116 and
                   # runs to 118, so it was thrown onto the fugue's side and the
                   # toccata simply stopped, unresolved, followed by the silence
                   # of the movement gap. Nothing at all crosses beat 118.
ECHO2_IN  = 244    # bar 62: the fugue's echo passage begins (half-bar repeats)
ECHO2_OUT = 324    # bar 82: it ends; the manuals couple again
F_BUILD   = 352    # bar 89: density rises toward the close of the fugue
PSOLO_IN  = 435    # bars 109-111, manuals silent: brighten the pedal (Biggs)
PSOLO_OUT = 441    # ...and retract BEFORE the manuals return at 442
CODA      = 508    # bar 128: recitative into the peroration

LEAN = F8 | F4                                  # the fugue subject must read
OBERWERK = [(0,         F8|F4|F2),              # bold declamation, not yet complete
            (T_CHORDS,  F8|F4|F2|F223|F16),     # the chords: add gravity
            (FUGUE,     LEAN),
            (F_BUILD,   PLENUM),
            (CODA,      PLENUM|F16|MIXTUR)]     # the crown

RUCKPOSITIV = [(0,         F8|F4|F2),           # coupled with the Oberwerk
               (ARP_IN,    F8),                 # the ECHO manual through the figure
               (ARP_OUT,   F8|F4|F2),           # coupled again
               (T_CHORDS,  F8|F4|F2|F223|F16),
               (FUGUE,     LEAN),
               (ECHO2_IN,  F8),                 # the ECHO manual: one rank, clearly softer
               (ECHO2_OUT, LEAN),               # coupled again after the echoes
               (F_BUILD,   PLENUM),
               (CODA,      PLENUM|F16|MIXTUR)]

PEDAL = [(0,         PEDAL_FOUND),
         (PSOLO_IN,  PEDAL_FOUND|F4|F2),        # the solo line must sing out
         (PSOLO_OUT, PEDAL_FOUND),              # retract in the gap, before the manuals
         (CODA,      PEDAL_FOUND|F513)]

POSAUNE = [(0,         0),
           (T_CHORDS,  R8|R16),                 # weight under the toccata's chords
           (FUGUE,     0),                      # out of the fugue: keep it transparent
           (PSOLO_IN,  R8|R16),                 # the pedal solo blazes
           (PSOLO_OUT, 0),
           (CODA,      R8|R16)]

TROMPETTE = [(0, 0), (CODA, TRUMPET)]           # Great Trompette, peroration only


def unify_octave_doublings(rh, lh):
    """Move LH notes that merely DOUBLE an RH note at the octave into the RH set.

    An octave doubling is one gesture, not two voices -- and BWV 565 opens with
    exactly that: three declamatory A's, each doubled an octave below. The hands
    happen to straddle the staff boundary, so routing by hand put the second
    gesture's A4 on the Oberwerk and its own octave A3 on the Rueckpositiv. The
    two manuals stand in different places, so the gesture arrived split and
    smeared while its neighbours were whole. Same onset, same duration, an exact
    octave apart: that is a doubling, and it belongs on one manual.
    """
    idx = {}
    for s, e, p, v in rh: idx.setdefault((s, e), set()).add(p)
    moved, rest = [], []
    for n in lh:
        s, e, p, v = n
        near = idx.get((s, e), ())
        if any(abs(p - q) in (12, 24) for q in near): moved.append(n)
        else: rest.append(n)
    return rh + moved, rest


def figure_split(rh, lh, TPB, lo_bar, hi_bar, W=0.5):
    """The broken-chord figure, split into its two strands and its two bars.

    Each half-beat group of the figure is four notes -- bass, X, moving, X --
    whose 2nd and 4th are the SAME pitch. That repeated note is a voice: through
    bars 14-16 it is a constant A (the repeated A of the preceding passage), and
    from bar 16 it simply descends, F F / E E / D D. So the figure is not four
    equal semiquavers but a moving line over a bass with a repeated tone inside
    it, and it is also an echo -- the whole figure restates itself bar to bar.

    Both readings are true, so we play both: the repeated tone is separated onto
    its own manual, and which manual carries it SWAPS between the statement bar
    and its echo. The strands trade places, which is what makes the restatement
    read as an echo rather than a repetition.

    -> (ow_extra, rp_extra, consumed) with `consumed` the notes now routed here.
    """
    alln = sorted(rh + lh)
    BAR = 4 * TPB
    groups = []
    b = lo_bar * BAR
    while b < hi_bar * BAR:
        g = sorted(n for n in alln if b <= n[0] < b + W * TPB)
        if len(g) == 4 and g[1][2] == g[3][2] and g[0][2] < g[1][2]:
            groups.append((b, g))
        b += int(W * TPB)
    if not groups:
        return [], [], set()
    # contiguous blocks of figure; inside a block, bars alternate statement/echo
    blocks, cur = [], [groups[0]]
    for prev, nxt in zip(groups, groups[1:]):
        if nxt[0] - prev[0] <= W * TPB * 2.5: cur.append(nxt)
        else: blocks.append(cur); cur = [nxt]
    blocks.append(cur)
    ow, rp, seen = [], [], set()
    for blk in blocks:
        first_bar = blk[0][0] // BAR
        for b0, g in blk:
            echo = ((b0 // BAR) - first_bar) % 2 == 1
            inner = [g[1], g[3]]                 # the repeated tone
            outer = [g[0], g[2]]                 # bass and moving note
            (ow if echo else rp).extend(inner)
            (rp if echo else ow).extend(outer)
            seen.update(g)
    return ow, rp, seen


def main():
    src = mido.MidiFile(SRC); TPB = src.ticks_per_beat
    rh    = read_notes(src, RH_TRACK)
    lh    = read_notes(src, LH_TRACK)
    pedal = read_notes(src, PEDAL_TRACK)

    # Ornaments BEFORE registration (notation -> ornaments -> registration ->
    # agogics). Each hand is matched separately, so a sign lands on the division
    # that actually plays it.
    orns = read_ornament_log(ORN_LOG, TPB)
    # THE OPENING GESTURE IS A MORDENT. This engraving prints \prall, which our
    # engine reads (correctly for that sign) as a trill from above: Bb-A-Bb-A,
    # ending on the lower note of the pair. Ben hears the mordent -- A-G-A,
    # ending on the upper -- which is the reading the piece is known by and the
    # sign its primary source carries; BWV 565 has no autograph to arbitrate.
    # Only the opening gesture (the three fermata-ed A's of bars 1-2) is changed;
    # the fugue's \trill at bar 12 stays a trill.
    orns = [(t, p, d, 'v' if t < 6 * TPB else s_) for t, p, d, s_ in orns]
    figs = realize_ornaments(orns, TPB, D_MINOR)
    rh, n_rh = apply_ornaments(rh, figs, TPB, verbose=False)
    lh, n_lh = apply_ornaments(lh, figs, TPB, verbose=False)
    print("  ornaments: %d on the RH, %d on the LH (of %d)" % (n_rh, n_lh, len(figs)))

    ferm = read_fermatas(ORN_LOG, TPB)
    print("  fermatas: %d, at bars %s" % (len(ferm), [round(t/(4.0*TPB)+1, 1) for t, _ in ferm]))

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    # ARPEGGIOS: the two the engraving marks (the bar-3 diminished chord, rolled
    # across both staves -- the source sets connectArpeggios), plus the toccata's
    # and coda's big sustained chords, which a player spreads as a matter of
    # course and which sound mechanical struck dead flat.
    arp = set(read_arpeggios(ORN_LOG, TPB))
    arp |= set(big_chords(rh + lh, TPB, min_notes=4, min_beats=0.75))
    print("  arpeggios: %d chords rolled (%d notated)"
          % (len(arp), len(read_arpeggios(ORN_LOG, TPB))))

    out.tracks.append(conductor("BWV565 Toccata and Fugue (organ, 2 man.)",
                                src=src, fermatas=ferm, arpeggios=sorted(arp)))
    # ECHOES: the answer half-bars move to the other manual, the way a player
    # moves a hand. Detected from the notes (see find_echoes), not hand-listed.
    BAR = 4 * TPB
    # The figure's lower voice sustains -- and the ENGRAVING says which voice that
    # is, by stem. Confined to the figure (bars 13-22): a sustain is a reading of
    # this texture, not a licence to make the whole toccata legato.
    stems = read_stems(ORN_LOG, TPB)
    rh, h1 = hold_stem_voice(rh, stems, TPB, 13 * 4 * TPB, 22 * 4 * TPB, others=lh)
    lh, h2 = hold_stem_voice(lh, stems, TPB, 13 * 4 * TPB, 22 * 4 * TPB, others=rh)
    print("  stem-voice hold: %d notes sustained (%d stems logged)" % (h1 + h2, len(stems)))

    # 0. an octave doubling is ONE gesture: keep it on one manual
    rh, lh = unify_octave_doublings(rh, lh)
    #    ...and the whole opening declamation belongs on the Oberwerk
    op = [n for n in lh if n[0] < DECLAIM * 4 * TPB]
    lh = [n for n in lh if n[0] >= DECLAIM * 4 * TPB]
    rh = sorted(rh + op)

    # 1. the toccata's broken-chord figure: two strands, trading manuals bar by bar
    fow, frp, used = figure_split(rh, lh, TPB, 13, 22)
    print("  figure: %d notes split into strands (%d/%d), swapping each bar"
          % (len(used), len(fow), len(frp)))
    ow, rp = list(fow), list(frp)
    # 2. the fugue's half-bar echoes: statement on the main manual, answer on the other
    for hand, dflt in ((rh, 'ow'), (lh, 'rp')):
        rest = [n for n in hand if n not in used]
        pairs = find_echoes(rest, BAR, 29, 127)
        stmt, ans, other = split_echoes(rest, pairs)
        ow += stmt; rp += ans                       # statement -> main, answer -> echo
        (ow if dflt == 'ow' else rp).extend(other)  # everything else stays on its hand's manual
        print("  echoes: %d pairs (%d notes to the echo manual)"
              % (len(pairs), len(ans)))
    ow.sort(); rp.sort()

    out.tracks.append(make_channel_track(0, 19, ow, OBERWERK,    TPB, unit='beat'))
    out.tracks.append(make_channel_track(1, 19, rp, RUCKPOSITIV, TPB, unit='beat'))
    out.tracks.append(make_channel_track(2, 19, pedal, PEDAL,       TPB, unit='beat'))
    out.tracks.append(make_channel_track(3, 20, pedal, POSAUNE,     TPB, unit='beat'))
    out.tracks.append(make_channel_track(4, 20, rh + lh, TROMPETTE, TPB, unit='beat'))
    out.save(DST)
    print("wrote %s | TPB %d | %.0fs | Oberwerk %d, Rueckpositiv %d, pedal %d"
          % (DST, TPB, out.length, len(ow), len(rp), len(pedal)))


if __name__ == "__main__":
    main()
