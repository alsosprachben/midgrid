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

# Touch and shaping shared by everything: baroque separation, a mean-preserving
# agogic breath, cadential trills reserved for structural closes (a phrase end is
# not a cadence -- see baroque-agogics/SKILL.md).
COMMON = ["--gap-frac", "0.14", "--gap-cap", "0.09", "--gap-min", "0.012",
          "--cadential-trills", "--trill-min-bars", "8.0", "--trill-arrival", "1.8"]

WORKS = {
    # --- BWV 565, Toccata and Fugue in D minor -------------------------------
    "bwv565": dict(
        register="register_bwv565.py",
        mid="~/Downloads/bwv565_organ.mid",
        tuner="hybridharm",
        movements=[
            # The toccata is improvisatory: slower, freer, strongly shaped.
            dict(name="toccata", upto=116, bpm=76,
                 flags=["--agogic", "0.06", "--phrase", "0.09",
                        "--density-damp", "0.5", "--tension", "0.5",
                        "--rit-beats", "8", "--rit-amount", "0.34"]),
            # The fugue drives: quicker, lighter shaping, a big final broadening.
            dict(name="fugue", bpm=96,
                 flags=["--agogic", "0.04", "--phrase", "0.05",
                        "--density-damp", "0.35", "--tension", "0.4",
                        "--rit-beats", "12", "--rit-amount", "0.42"]),
        ]),
    # --- BWV 582, Passacaglia and Fugue in C minor ---------------------------
    "bwv582": dict(
        register="register_bwv582.py",
        mid="~/Downloads/bwv582_organ.mid",
        tuner="hybridharm",
        movements=[
            # A passacaglia is a ground: steady, its shaping in the variations,
            # not in the bar. Keep the agogic light or the ostinato limps.
            dict(name="passacaglia", upto=505, bpm=72,
                 flags=["--agogic", "0.035", "--phrase", "0.06",
                        "--density-damp", "0.45", "--tension", "0.4",
                        "--rit-beats", "8", "--rit-amount", "0.30"]),
            # The seam is 505, NOT bar 170's barline: the Thema fugatum's g2 is a
            # two-beat anacrusis INTO that bar, and cutting at the barline left
            # the subject's first note behind in the passacaglia.
            dict(name="fugue", bpm=80,
                 flags=["--agogic", "0.04", "--phrase", "0.05",
                        "--density-damp", "0.35", "--tension", "0.45",
                        "--rit-beats", "14", "--rit-amount", "0.44"]),
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
