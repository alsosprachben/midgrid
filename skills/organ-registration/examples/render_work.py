#!/usr/bin/env python3
"""render_work.py -- run one work end-to-end, from the engraving to the mp3.

The pipeline has four stages and a fixed order:

    notation -> ORNAMENTS -> registration -> agogics -> render

and every stage has a setting that is a musical decision (which stops, where the
movements divide, how fast, how much the phrase breathes). Those decisions were
living in shell history, which meant a render could not be reproduced or
adjusted -- and, worse, that a stage could be skipped without anything saying
so. BWV 565 was registered and performed without ever having its ornaments
applied, and the famous opening mordent was simply absent from the render; the
same was true of BWV 582's fugue trill. Nothing in the pipeline noticed.

So the decisions live in WORKS below, one entry per work, and this script runs
them. Adding a work is adding a table entry.

    ./render_work.py bwv565            # register -> split -> perform -> render
    ./render_work.py bwv565 --no-render   # stop before the (slow) audio stage

Multi-movement works are split at a seam BEAT, performed separately (each
movement wants its own tempo and its own closing ritardando), then handed to
render_organ.sh together so the movements share one reverb and one normalise.
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AGOGICS = os.path.abspath(os.path.join(HERE, "..", "..", "baroque-agogics",
                                       "examples", "perform_baroque.py"))
OUT_DIR = os.path.expanduser(os.environ.get("ORGAN_OUT",
                                            "~/Downloads/bach-organ-renders"))
WORK_DIR = os.path.expanduser("~/Downloads/organ-work")

# Shared by everything: editorial trills at structural closes only (a phrase end
# is not a cadence -- see baroque-agogics/SKILL.md). Everything else, the TOUCH
# included, is left at perform_baroque's defaults, which is what these renders
# were auditioned with. Do not add overrides here casually: --gap-frac/-cap/-min
# are the separation that reads as dynamics on a fixed-volume instrument, and
# tightening them quietly makes the whole corpus more legato.
COMMON = ["--cadential-trills"]

# NOTE ON THE NUMBERS BELOW. They are the values Ben auditioned and approved, not
# fresh guesses. Two of the parameters are easy to get backwards:
#   --rit-amount is a MULTIPLIER on beat length (1.0 + (amount-1)*smoothstep), so
#     1.6 broadens the close by 60% and anything BELOW 1.0 is an accelerando into
#     the cadence -- which is never what is wanted.
#   --tension lengthens every beat carrying a sounding dissonance. In chromatic
#     writing that is most beats, so it belongs at a few percent (0.02-0.03).
#     At 0.4 the music lurches continuously and reads as heavy rubato.
# Both were wrong in the first version of this table and both were audible.

WORKS = {
    # --- BWV 565, Toccata and Fugue in D minor -------------------------------
    "bwv565": dict(
        register="register_bwv565.py",
        mid="~/Downloads/bwv565_organ.mid",
        tuner="hybridharm",
        movements=[
            # The toccata is improvisatory: slow, freely shaped, its passagework
            # heavily damped so the flourishes flow instead of being measured out.
            dict(name="toccata", upto=116, bpm=62,
                 flags=["--agogic", "0.10", "--phrase", "0.17",
                        "--density-damp", "0.85", "--tension", "0.03",
                        "--rit-beats", "5", "--rit-amount", "1.8",
                        # The broken-chord figures (bars 16-17 and their kin) put
                        # the harmony in the lowest note of each half-beat group;
                        # the engraving writes it as a 32nd plus a rest, so
                        # without this the passage is a flat run of semiquavers
                        # with nothing under it.
                        "--arpeggio-hold", "0.5"]),
            # The fugue drives: quicker, lighter shaping, a big final broadening.
            dict(name="fugue", bpm=84,
                 flags=["--agogic", "0.09", "--phrase", "0.09",
                        "--density-damp", "0.7", "--tension", "0.02",
                        "--rit-beats", "10", "--rit-amount", "2.0"]),
        ]),
    # --- BWV 582, Passacaglia and Fugue in C minor ---------------------------
    "bwv582": dict(
        register="register_bwv582.py",
        mid="~/Downloads/bwv582_organ.mid",
        tuner="hybridharm",
        movements=[
            # A passacaglia is a ground: steady, its shaping in the variations,
            # not in the bar. Keep the agogic light or the ostinato limps.
            dict(name="passacaglia", upto=505, bpm=66,
                 flags=["--agogic", "0.09", "--phrase", "0.10",
                        "--density-damp", "0.75", "--tension", "0.025",
                        "--rit-beats", "6", "--rit-amount", "1.6"]),
            # The seam is 505, NOT bar 170's barline: the Thema fugatum's g2 is a
            # two-beat anacrusis INTO that bar, and cutting at the barline left
            # the subject's first note behind in the passacaglia.
            dict(name="fugue", bpm=72,
                 flags=["--agogic", "0.09", "--phrase", "0.09",
                        "--density-damp", "0.7", "--tension", "0.02",
                        "--rit-beats", "12", "--rit-amount", "2.0"]),
        ]),
}


def run(cmd, **kw):
    print("   $", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work", choices=sorted(WORKS))
    ap.add_argument("--no-render", action="store_true",
                    help="stop after the performed MIDIs (skips the slow audio)")
    ap.add_argument("--keep-wav", action="store_true",
                    help="keep the WAVs (default: mp3 only -- a corpus of WAVs is tens of GB)")
    a = ap.parse_args()
    w = WORKS[a.work]
    os.makedirs(WORK_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    print("== 1. registration (ornaments are applied inside, before the stops)")
    run([sys.executable, os.path.join(HERE, w["register"])])
    mid = os.path.expanduser(w["mid"])

    print("== 2. split into movements")
    sys.path.insert(0, HERE)
    from reglib import split_at
    movs = w["movements"]
    parts, rest, done = [], mid, 0.0
    for i, m in enumerate(movs[:-1]):
        A = os.path.join(WORK_DIR, "%s_%d_%s.mid" % (a.work, i, m["name"]))
        B = os.path.join(WORK_DIR, "%s_rest%d.mid" % (a.work, i))
        # seam beats in the table are absolute in the ENGRAVING; each split
        # rebases the remainder's timeline to zero, so subtract what we cut off.
        split_at(rest, m["upto"] - done, A, B)
        parts.append(A); rest = B; done = m["upto"]
    last = os.path.join(WORK_DIR, "%s_%d_%s.mid" % (a.work, len(movs) - 1, movs[-1]["name"]))
    if rest != mid:
        os.replace(rest, last); rest = last
    parts.append(rest)

    print("== 3. agogics, per movement")
    performed = []
    for m, src in zip(movs, parts):
        dst = os.path.join(WORK_DIR, "%s_%s_perf.mid" % (a.work, m["name"]))
        run([sys.executable, AGOGICS, src, dst, "--bpm", m["bpm"]] + COMMON + m["flags"])
        performed.append(dst)

    if a.no_render:
        print("\nperformed MIDIs:", *performed, sep="\n  ")
        return

    print("== 4. render (one reverb and one normalise across the whole work)")
    env = dict(os.environ, OUT_DIR=OUT_DIR, KEEP_WAV="1" if a.keep_wav else "0")
    run([os.path.join(HERE, "render_organ.sh"), ",".join(performed),
         w["tuner"], a.work], env=env)
    print("\n>> %s/%s.mp3" % (OUT_DIR, a.work))


if __name__ == "__main__":
    main()
