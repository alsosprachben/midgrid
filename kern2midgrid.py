#!/usr/bin/env python3
"""Convert Sapp's monophonic-spine **kern Art-of-Fugue file directly to midgrid,
preserving Bach's enharmonic spelling and register order (V0 soprano..V3 bass).
Exact Fraction arithmetic so triplets never drift."""
import re, sys
from fractions import Fraction as F

PC = {'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}
# Canonical midgrid spelling: sharps, plus B-/A-/E- as the only allowed flats
# (matches the repo's other fugues and the linter). Pitch is unchanged.
CANON = {0:'C',1:'C#',2:'D',3:'E-',4:'E',5:'F',6:'F#',7:'G',8:'A-',9:'A',10:'B-',11:'B'}

def kern_parse(tok):
    m = re.search(r'(\d+)(\.*)', tok)          # duration is the only digit-run
    if not m:
        return None
    num = int(m.group(1)); dots = len(m.group(2))
    dur = F(4, num) * (F(2) - F(1, 2**dots))   # quarter-beats, exact
    rest = tok[m.end():]
    tie = 'start' if '[' in tok else ('end' if ']' in tok else ('mid' if '_' in tok else None))
    if 'r' in rest:
        return ('rest', None, dur, tie)
    lm = re.search(r'([a-gA-G]+)', rest)
    if not lm:
        return ('rest', None, dur, tie)
    letters = lm.group(1); n = len(letters); low = letters[0].islower()
    octave = (3 + n) if low else (4 - n)
    midi = 12*(octave+1) + PC[letters[0].lower()] + rest.count('#') - rest.count('-')
    name = CANON[midi % 12] + str(midi // 12 - 1)
    return ('note', name, dur, tie)

def parse_voice(tokens):
    notes = []; t = F(0); pending = None
    for tok in tokens:
        p = kern_parse(tok)
        if p is None:
            continue
        kind, name, dur, tie = p
        if kind == 'rest':
            if pending: notes.append(pending); pending = None
            t += dur; continue
        if pending is not None and tie in ('mid', 'end') and name == pending['name']:
            pending['dur'] += dur; t += dur
            if tie == 'end':
                notes.append(pending); pending = None
            continue
        if pending is not None:
            notes.append(pending); pending = None
        if tie == 'start':
            pending = {'onset': t, 'dur': dur, 'name': name}; t += dur
        else:
            notes.append({'onset': t, 'dur': dur, 'name': name}); t += dur
    if pending: notes.append(pending)
    return notes

def fmt_beat(fr):
    s = f"{float(fr):.2f}".rstrip('0')
    return s if s.endswith('.') else s        # keep trailing dot like the emitter

def fmt_dur(fr):
    return f"{float(fr):.2f}".rstrip('0').rstrip('.')

def main(inp, outp):
    cols = [[], [], [], []]                    # kern order: bass,tenor,alto,soprano
    for ln in open(inp):
        ln = ln.rstrip('\n')
        if not ln or ln[0] in '!*':
            continue
        parts = ln.split('\t')
        if len(parts) < 4 or parts[0].startswith('='):
            continue
        for i in range(4):
            if parts[i] and parts[i] != '.':
                cols[i].append(parts[i])
    voices = [parse_voice(c) for c in cols]
    order = [3, 2, 1, 0]                        # soprano..bass -> V0..V3
    vnotes = [voices[ci] for ci in order]

    times = set()
    for vn in vnotes:
        for nt in vn:
            times.add(nt['onset']); times.add(nt['onset'] + nt['dur'])
    timeline = sorted(times)

    grid = [dict() for _ in range(4)]
    for vi, vn in enumerate(vnotes):
        for nt in vn:
            on = nt['onset']; off = on + nt['dur']
            grid[vi][on] = f"{nt['name']}:{fmt_dur(nt['dur'])}@80"
            for t in timeline:
                if on < t < off:
                    grid[vi][t] = "-"
    for vi in range(4):
        for t in timeline:
            grid[vi].setdefault(t, ".")

    labels = ["V0", "V1", "V2", "V3"]
    widths = [max(5, max(len(fmt_beat(t)) for t in timeline))]
    for vi in range(4):
        widths.append(max(2, max(len(grid[vi][t]) for t in timeline)))

    out = []
    out.append("# Title: Contrapunctus XIV (BWV 1080/19) -- \"Fuga a 3 soggetti\", unfinished fragment (bars 1-239, breaks off mid-bar)")
    out.append("# Source: CCARH/KernScores artfugue-019.krn (Bach-Gesellschaft ed.); kern->midgrid, Bach's enharmonic spelling preserved")
    out.append("# tempo 92")
    out.append("# Voices: V0 soprano, V1 alto, V2 tenor, V3 bass")
    header = ["#beat".ljust(widths[0])] + [labels[v].ljust(widths[v+1]) for v in range(4)]
    out.append(" | ".join(header))
    for t in timeline:
        if all(grid[v][t] == "." for v in range(4)):
            continue
        row = [fmt_beat(t).ljust(widths[0])] + [grid[v][t].ljust(widths[v+1]) for v in range(4)]
        out.append(" | ".join(row).rstrip())
    open(outp, "w").write("\n".join(out) + "\n")
    print("wrote", outp)
    print("note counts V0..V3 (sop..bass):", [len(vn) for vn in vnotes])
    print("last onset beat:", float(timeline[-1]))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
