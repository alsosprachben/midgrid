#!/usr/bin/env python3
"""Motivic derivative analysis for MidGrid scores.

Represents each voice as a stack of melodic derivatives and scores segment
similarity per layer instead of matching booleans:

    layer 0  pitch            (position; transposition-variant)
    layer 1  chromatic d1     (semitones; invariant under chromatic transposition)
    layer 1' diatonic d1      (scale steps from spelling; invariant under
                               modal/tonal transposition)
    layer 2  contour sign(d1) (direction; the coarsest, perceptually strongest)

The layer at which similarity breaks classifies the transformation:
    chromatic d1 exact        -> REAL echo (strict transposition; 0 = restatement)
    diatonic d1 exact only    -> DIATONIC echo (modal transposition; the
                                 chromatic mismatch positions are the "note
                                 distance adjustments")
    mismatches only at head   -> TONAL answer (head adjusted — the classic
                                 fifth-to-fourth swap — tail exact)
    negated d1 match          -> INVERSION (rectus/inversus pairing)
    otherwise, high contour   -> FREE echo

Also reports per-voice verbatim recalls (episode rhymes), cross-voice
directional correlation (melodic fusion: two voices running the same
predictor), and motivic economy (fraction of attacks inside subject-family
spans).

Usage:
    python3 midgrid_motif.py FILE [--subject V1:0-8] [--min-score 0.7]
                                  [--compare V1:0-8 V0:8-16]
                                  [--write-json OUT.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NOTE_RE = re.compile(r"^([A-G])([#-]?)(\d+):([\d.]+)(?:@(\d+))?")
CHROMA = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
LETTER = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}

CONTOUR_W, DIAT_W, CHROM_W = 0.40, 0.35, 0.25


def parse_pitch(token: str):
    m = NOTE_RE.match(token)
    if not m:
        return None
    letter, acc, octave, dur, vel = m.groups()
    octv = int(octave)
    midi = (octv + 1) * 12 + CHROMA[letter] + (1 if acc == "#" else -1 if acc == "-" else 0)
    diat = octv * 7 + LETTER[letter]
    return dict(name=f"{letter}{acc}{octave}", midi=midi, diat=diat,
                dur=float(dur), vel=int(vel) if vel else None)


def parse_midgrid(path: Path):
    """Return list of voices; each voice is a list of attacks
    {beat, name, midi, diat, dur}."""
    voices: list[list[dict]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        parts = [c.strip() for c in line.split("|")]
        if len(parts) < 2:
            continue
        try:
            beat = float(parts[0])
        except ValueError:
            continue
        cells = parts[1:]
        while len(voices) < len(cells):
            voices.append([])
        for vi, cell in enumerate(cells):
            note = parse_pitch(cell)
            if note:
                note["beat"] = beat
                voices[vi].append(note)
    for v in voices:
        v.sort(key=lambda n: n["beat"])
    return voices


def d1_chrom(notes):
    return [b["midi"] - a["midi"] for a, b in zip(notes, notes[1:])]


def d1_diat(notes):
    return [b["diat"] - a["diat"] for a, b in zip(notes, notes[1:])]


def sign(x):
    return (x > 0) - (x < 0)


def agree(xs, ys):
    if not xs:
        return 0.0
    return sum(1 for x, y in zip(xs, ys) if x == y) / len(xs)


def layer_scores(sub_notes, seg_notes, invert=False):
    sc, sd = d1_chrom(sub_notes), d1_diat(sub_notes)
    if invert:
        sc, sd = [-x for x in sc], [-x for x in sd]
    ec, ed = d1_chrom(seg_notes), d1_diat(seg_notes)
    contour = agree([sign(x) for x in sc], [sign(x) for x in ec])
    diat = agree(sd, ed)
    chrom = agree(sc, ec)
    weighted = CONTOUR_W * contour + DIAT_W * diat + CHROM_W * chrom
    mism = [i for i, (x, y) in enumerate(zip(sc, ec)) if x != y]
    mism_d = [i for i, (x, y) in enumerate(zip(sd, ed)) if x != y]
    return dict(contour=contour, diatonic=diat, chromatic=chrom,
                weighted=weighted, chromatic_mismatch_at=mism,
                diatonic_mismatch_at=mism_d)


def classify(scores, invert, n_intervals):
    if scores["chromatic"] == 1.0:
        kind = "real"
    elif scores["diatonic"] == 1.0:
        kind = "diatonic"
    else:
        # TONAL answer: every mismatch (either unit) confined to the head
        # window, tail exact — the fifth-to-fourth head swap.
        head = max(2, n_intervals // 3)
        mism = set(scores["chromatic_mismatch_at"]) | set(scores["diatonic_mismatch_at"])
        if mism and max(mism) < head and scores["contour"] >= 0.85:
            kind = "tonal"
        elif scores["contour"] >= 0.8:
            kind = "free"
        else:
            kind = "weak"
    return ("inv-" + kind) if invert else kind


def find_echoes(voices, sub_voice, sub_start_idx, sub_notes, min_score):
    n = len(sub_notes)
    candidates = []
    for vi, notes in enumerate(voices):
        for i in range(len(notes) - n + 1):
            if vi == sub_voice and i == sub_start_idx:
                continue
            seg = notes[i:i + n]
            for invert in (False, True):
                sc = layer_scores(sub_notes, seg, invert)
                if sc["weighted"] < min_score:
                    continue
                candidates.append(dict(
                    voice=vi, note_index=i,
                    beat_start=seg[0]["beat"], beat_end=seg[-1]["beat"],
                    transposition=seg[0]["midi"] - sub_notes[0]["midi"],
                    diat_offset=seg[0]["diat"] - sub_notes[0]["diat"],
                    kind=classify(sc, invert, n - 1), inverted=invert, **sc))
    # non-maximum suppression per voice: keep best-scoring, reject heavy overlap
    candidates.sort(key=lambda c: -c["weighted"])
    accepted = []
    for c in candidates:
        clash = False
        for a in accepted:
            if a["voice"] != c["voice"]:
                continue
            lo = max(a["note_index"], c["note_index"])
            hi = min(a["note_index"] + n, c["note_index"] + n)
            if hi - lo > n // 4:
                clash = True
                break
        if not clash:
            accepted.append(c)
    accepted.sort(key=lambda c: (c["beat_start"], c["voice"]))
    return accepted


def find_recalls(voices, min_len=6):
    """Per-voice verbatim recalls: repeated (chromatic d1, dur) substrings."""
    recalls = []
    for vi, notes in enumerate(voices):
        seq = [(b["midi"] - a["midi"], a["dur"]) for a, b in zip(notes, notes[1:])]
        found = set()
        for i in range(len(seq) - min_len):
            for j in range(i + min_len, len(seq) - min_len + 1):
                if any(i < e and s < i + min_len for s, e in found):
                    break
                k = 0
                while (j + k < len(seq) and i + k < j
                       and seq[i + k] == seq[j + k]):
                    k += 1
                if k >= min_len:
                    recalls.append(dict(
                        voice=vi, length=k + 1,
                        first=dict(beat_start=notes[i]["beat"],
                                   beat_end=notes[i + k]["beat"]),
                        second=dict(beat_start=notes[j]["beat"],
                                    beat_end=notes[j + k]["beat"]),
                        transposition=notes[j]["midi"] - notes[i]["midi"]))
                    found.add((i, i + k))
                    found.add((j, j + k))
    return recalls


def lattice_pitches(voices, step=0.5):
    """Half-beat pitch lattice per voice (holds sustain the pitch)."""
    end = max((n["beat"] + n["dur"] for v in voices for n in v), default=0.0)
    ticks = int(round(end / step))
    grids = []
    for notes in voices:
        grid = [None] * (ticks + 1)
        for n in notes:
            a = int(round(n["beat"] / step))
            b = min(int(round((n["beat"] + n["dur"]) / step)), ticks)
            for t in range(a, b + 1):
                grid[t] = n["midi"] if t == a or grid[t] is None else grid[t]
            grid[a] = n["midi"]
            for t in range(a + 1, b):
                grid[t] = n["midi"]
        grids.append(grid)
    return grids, step


def melodic_fusion(voices, window_beats=4.0, min_comoves=5, min_agree=0.85):
    """Cross-voice directional correlation: sliding windows where two voices
    co-move in the same direction — same-predictor (fused) melodic motion."""
    grids, step = lattice_pitches(voices)
    ticks = len(grids[0]) if grids else 0
    win = int(round(window_beats / step))
    regions = []
    for a in range(len(grids)):
        for b in range(a + 1, len(grids)):
            da = [None if grids[a][t] is None or grids[a][t - 1] is None
                  else grids[a][t] - grids[a][t - 1] for t in range(1, ticks)]
            db = [None if grids[b][t] is None or grids[b][t - 1] is None
                  else grids[b][t] - grids[b][t - 1] for t in range(1, ticks)]
            cur = None
            for t0 in range(0, len(da) - win):
                co = [(x, y) for x, y in zip(da[t0:t0 + win], db[t0:t0 + win])
                      if x not in (None, 0) and y not in (None, 0)]
                if len(co) < min_comoves:
                    ok = False
                else:
                    same = sum(1 for x, y in co if sign(x) == sign(y))
                    locked = sum(1 for x, y in co if x == y)
                    ok = same / len(co) >= min_agree
                if ok:
                    beat0, beat1 = t0 * step, (t0 + win) * step
                    if cur and beat0 <= cur["beat_end"]:
                        cur["beat_end"] = beat1
                        cur["comoves"] = max(cur["comoves"], len(co))
                        cur["locked"] = max(cur["locked"], locked)
                    else:
                        if cur:
                            regions.append(cur)
                        cur = dict(pair=f"V{a}-V{b}", beat_start=beat0,
                                   beat_end=beat1, comoves=len(co),
                                   locked=locked)
                elif cur:
                    regions.append(cur)
                    cur = None
            if cur:
                regions.append(cur)
    regions.sort(key=lambda r: (-(r["beat_end"] - r["beat_start"]), r["beat_start"]))
    return regions


def rhythmic_fusion(voices, window_beats=8.0, min_attacks=6, min_co=0.9,
                    max_ratio=1.5):
    """Homorhythm regions: sliding windows where two voices attack at the
    same instants (co-attack fraction >= min_co) at SIMILAR rates (attack
    count ratio < max_ratio). Both conditions matter: a running-eighths
    line over a theme in augmentation co-attacks at every theme note but
    is rate-stratified (the Contrapunctus IX regime, ratio >= max_ratio);
    harmonization is same clock at the same rate."""
    regions = []
    step = 1.0
    end = max((n["beat"] for v in voices for n in v), default=0.0)
    for a in range(len(voices)):
        for b in range(a + 1, len(voices)):
            atk_a = sorted(n["beat"] for n in voices[a])
            atk_b = sorted(n["beat"] for n in voices[b])
            cur = None
            t0 = 0.0
            while t0 + window_beats <= end + step:
                wa = set(t for t in atk_a if t0 <= t < t0 + window_beats)
                wb = set(t for t in atk_b if t0 <= t < t0 + window_beats)
                ok = False
                if len(wa) >= min_attacks and len(wb) >= min_attacks:
                    co = len(wa & wb) / min(len(wa), len(wb))
                    ratio = max(len(wa), len(wb)) / min(len(wa), len(wb))
                    ok = co >= min_co and ratio < max_ratio
                if ok:
                    if cur and t0 <= cur["beat_end"]:
                        cur["beat_end"] = t0 + window_beats
                        cur["co_attacks"] = max(cur["co_attacks"], len(wa & wb))
                    else:
                        if cur:
                            regions.append(cur)
                        cur = dict(pair=f"V{a}-V{b}", beat_start=t0,
                                   beat_end=t0 + window_beats,
                                   co_attacks=len(wa & wb),
                                   rate_ratio=round(max(len(wa), len(wb))
                                                    / min(len(wa), len(wb)), 2))
                elif cur:
                    regions.append(cur)
                    cur = None
                t0 += step
            if cur:
                regions.append(cur)
    regions.sort(key=lambda r: (r["beat_start"], r["pair"]))
    return regions


def homorhythm_fractions(voices):
    """Per-pair fraction of the pair's active span spent in homorhythm
    regions (from rhythmic_fusion). 1.0 = the pair shares one attack clock
    throughout (harmonization); low values = rate-stratified counterpoint
    (Contrapunctus IX regime)."""
    from collections import defaultdict
    regs = rhythmic_fusion(voices)
    spans = {}
    for a in range(len(voices)):
        for b in range(a + 1, len(voices)):
            if not voices[a] or not voices[b]:
                continue
            lo = max(voices[a][0]["beat"], voices[b][0]["beat"])
            hi = min(voices[a][-1]["beat"], voices[b][-1]["beat"])
            if hi > lo:
                spans[f"V{a}-V{b}"] = (lo, hi)
    homo = defaultdict(float)
    for r in regs:
        homo[r["pair"]] += r["beat_end"] - r["beat_start"]
    return {pair: min(1.0, homo.get(pair, 0.0) / (hi - lo))
            for pair, (lo, hi) in spans.items()}


def parse_segment(spec: str, voices):
    m = re.match(r"^V(\d+):([\d.]+)-([\d.]+)$", spec)
    if not m:
        raise SystemExit(f"bad segment spec {spec!r} (want e.g. V1:0-8)")
    vi, lo, hi = int(m.group(1)), float(m.group(2)), float(m.group(3))
    notes = [n for n in voices[vi] if lo <= n["beat"] < hi]
    if len(notes) < 2:
        raise SystemExit(f"segment {spec} has fewer than 2 notes")
    return vi, notes


def default_subject(voices):
    """First voice to sound, up to the entry of the next voice."""
    firsts = [(v[0]["beat"], vi) for vi, v in enumerate(voices) if v]
    firsts.sort()
    sub_voice = firsts[0][1]
    cutoff = firsts[1][0] if len(firsts) > 1 else float("inf")
    notes = [n for n in voices[sub_voice] if n["beat"] < cutoff]
    if len(notes) < 4:
        notes = voices[sub_voice][:8]
    return sub_voice, notes


def fmt_d1(xs):
    return " ".join(f"{x:+d}" for x in xs)


def compare_report(sub_notes, seg_notes):
    lines = ["idx | subject        | echo           | chrom | diat | dir"]
    sc, ec = d1_chrom(sub_notes), d1_chrom(seg_notes)
    sd, ed = d1_diat(sub_notes), d1_diat(seg_notes)
    for i in range(min(len(sc), len(ec))):
        mark_c = " " if sc[i] == ec[i] else "*"
        mark_d = " " if sd[i] == ed[i] else "*"
        mark_s = " " if sign(sc[i]) == sign(ec[i]) else "*"
        lines.append(
            f"{i:3d} | {sub_notes[i]['name']:>4}->{sub_notes[i+1]['name']:<4} "
            f"{sc[i]:+3d} | {seg_notes[i]['name']:>4}->{seg_notes[i+1]['name']:<4} "
            f"{ec[i]:+3d} | {sc[i]:+3d}/{ec[i]:+3d}{mark_c} | "
            f"{sd[i]:+d}/{ed[i]:+d}{mark_d} | {mark_s}")
    return "\n".join(lines)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", type=Path)
    ap.add_argument("--subject", help="segment spec, e.g. V1:0-8 (end exclusive)")
    ap.add_argument("--min-score", type=float, default=0.70)
    ap.add_argument("--compare", nargs=2, metavar="SEG",
                    help="print derivative diff of two segments and exit")
    ap.add_argument("--write-json", type=Path)
    args = ap.parse_args(argv)

    voices = parse_midgrid(args.file)

    if args.compare:
        _, a = parse_segment(args.compare[0], voices)
        _, b = parse_segment(args.compare[1], voices)
        sc = layer_scores(a, b)
        print(compare_report(a, b))
        print(f"\ncontour {sc['contour']:.2f}  diatonic {sc['diatonic']:.2f}  "
              f"chromatic {sc['chromatic']:.2f}  weighted {sc['weighted']:.2f}")
        return 0

    if args.subject:
        sub_voice, sub_notes = parse_segment(args.subject, voices)
    else:
        sub_voice, sub_notes = default_subject(voices)
    sub_start_idx = voices[sub_voice].index(sub_notes[0])

    echoes = find_echoes(voices, sub_voice, sub_start_idx, sub_notes,
                         args.min_score)
    recalls = find_recalls(voices)
    fusion = melodic_fusion(voices)

    total_attacks = sum(len(v) for v in voices)
    covered = len(sub_notes)
    for e in echoes:
        covered += len(sub_notes)
    economy = covered / total_attacks if total_attacks else 0.0

    print(f"Subject: V{sub_voice} beats {sub_notes[0]['beat']:g}-"
          f"{sub_notes[-1]['beat']:g} ({len(sub_notes)} notes): "
          + " ".join(n["name"] for n in sub_notes))
    print(f"  chromatic d1: {fmt_d1(d1_chrom(sub_notes))}")
    print(f"  diatonic  d1: {fmt_d1(d1_diat(sub_notes))}")
    print(f"\nEchoes (min weighted score {args.min_score}):")
    for e in echoes:
        adj = ""
        if e["kind"] == "diatonic" and e["chromatic_mismatch_at"]:
            adj = " adjusted at interval " + ",".join(
                str(i) for i in e["chromatic_mismatch_at"])
        elif e["kind"] == "tonal":
            adj = " head-adjusted at interval " + ",".join(
                str(i) for i in sorted(set(e["chromatic_mismatch_at"])
                                       | set(e["diatonic_mismatch_at"])))
        print(f"  V{e['voice']} beats {e['beat_start']:g}-{e['beat_end']:g}  "
              f"{e['kind'].upper():<12} t={e['transposition']:+d}  "
              f"contour {e['contour']:.2f} diat {e['diatonic']:.2f} "
              f"chrom {e['chromatic']:.2f} [w {e['weighted']:.2f}]{adj}")
    print(f"\nVerbatim recalls (episode rhymes):")
    for r in recalls:
        print(f"  V{r['voice']} beats {r['first']['beat_start']:g}-"
              f"{r['first']['beat_end']:g} == beats "
              f"{r['second']['beat_start']:g}-{r['second']['beat_end']:g} "
              f"({r['length']} notes, t={r['transposition']:+d})")
    print(f"\nMelodic fusion regions (same-direction co-movement):")
    for r in fusion[:8]:
        print(f"  {r['pair']} beats {r['beat_start']:g}-{r['beat_end']:g} "
              f"(comoves {r['comoves']}, locked {r['locked']})")
    strata = homorhythm_fractions(voices)
    if strata:
        mean_h = sum(strata.values()) / len(strata)
        print(f"\nHomorhythm (co-attack clock): mean {mean_h:.2f}  " +
              " ".join(f"{k}:{v:.2f}" for k, v in sorted(strata.items())))
    print(f"\nMotivic economy: {economy:.0%} of {total_attacks} attacks "
          f"in subject-family spans")

    if args.write_json:
        args.write_json.write_text(json.dumps(dict(
            file=str(args.file),
            subject=dict(voice=sub_voice,
                         beat_start=sub_notes[0]["beat"],
                         beat_end=sub_notes[-1]["beat"],
                         notes=[n["name"] for n in sub_notes],
                         chromatic_d1=d1_chrom(sub_notes),
                         diatonic_d1=d1_diat(sub_notes)),
            echoes=echoes, recalls=recalls, fusion=fusion,
            homorhythm=strata, motivic_economy=economy), indent=2))
        print(f"\nJSON written to {args.write_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
