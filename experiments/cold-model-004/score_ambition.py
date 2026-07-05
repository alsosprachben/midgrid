#!/usr/bin/env python3
"""Ambition metrics for cold-model-004 submissions (pattern from 002)."""
import sys, glob, re

def metrics(path):
    rows = []
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        parts = [c.strip() for c in line.split('|')]
        if len(parts) < 2:
            continue
        try:
            beat = float(parts[0])
        except ValueError:
            continue
        rows.append((beat, parts[1:]))
    if not rows:
        return None
    attacks = []
    durs = set()
    for beat, cells in rows:
        for cell in cells:
            m = re.match(r"^([A-G][#-]?\d+):([\d.]+)@(\d+)", cell)
            if m:
                attacks.append((beat, float(m.group(2))))
                durs.add(float(m.group(2)))
    length = max(b for b, _ in rows)
    n = len(attacks)
    eighth = sum(1 for _, d in attacks if d == 0.5)
    sync = sum(1 for b, d in attacks if (b % 1.0) == 0.5 and d >= 1.0)
    return dict(length=length, attacks=n, apb=n / length,
                eighth_frac=eighth / n, syncopes=sync, ndur=len(durs))

for path in sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1
                             else 'experiments/cold-model-004/submissions/*.midgrid')):
    m = metrics(path)
    name = path.split('/')[-1].replace('.midgrid', '')
    print(f"{name}: length={m['length']:.1f} attacks={m['attacks']} "
          f"apb={m['apb']:.2f} eighth_frac={m['eighth_frac']:.2f} "
          f"syncopes={m['syncopes']} ndur={m['ndur']}")
