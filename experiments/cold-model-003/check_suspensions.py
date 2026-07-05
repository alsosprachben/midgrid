#!/usr/bin/env python3
"""Deterministic suspension-grammar checker for cold-model-003.

Section 8-15, V0 (answer) vs V1 (syncopated countersubject):
 - compliance: V1 attacks only on half-beats (dur >= 1), except sustains.
 - suspension: dissonant downbeat (interval class not in consonant set),
   prepared as a consonance at the previous half-beat attack, resolved
   down by step (1-2 semitones) at the next half-beat attack.
Outputs counts and violations as JSON.
"""
import json, re, sys

CONSONANT = {0, 3, 4, 7, 8, 9}

def parse(path):
    rows = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith(("#", "//")): continue
        parts = [p.strip() for p in s.split("|")]
        try: b = float(parts[0])
        except ValueError: continue
        rows.append((b, parts[1:]))
    return rows

NOTE = re.compile(r"([A-G])([#-]?)(\d)(?::([0-9.]+))?")
def midi(cell):
    m = NOTE.match(cell)
    if not m: return None, None
    base = {"C":0,"D":2,"E":4,"F":5,"G":7,"A":9,"B":11}[m.group(1)]
    base += {"#":1,"-":-1,"":0}[m.group(2)]
    return base + 12*(int(m.group(3))+1), float(m.group(4) or 1)

def main(path):
    rows = parse(path)
    v0, v1 = {}, {}   # beat -> (midi, dur)
    for b, cells in rows:
        if len(cells) >= 1:
            m, d = midi(cells[0])
            if m is not None: v0[b] = (m, d)
        if len(cells) >= 2:
            m, d = midi(cells[1])
            if m is not None: v1[b] = (m, d)

    def sounding(vm, t):
        best = None
        for b, (m, d) in vm.items():
            if b <= t < b + d and (best is None or b > best[0]):
                best = (b, m)
        return best[1] if best else None

    sect = [b for b in v1 if 8 <= b < 16]
    on_beats = [b for b in sect if b == int(b) and b > 8]
    off_attacks = [b for b in sect if b != int(b)]
    compliant = len(on_beats) == 0 and len(off_attacks) >= 5

    suspensions, violations = [], []
    for b in sorted(off_attacks):
        m, d = v1[b]
        down = b + 0.5
        if down >= 16: continue
        other = sounding(v0, down)
        if other is None: continue
        ic = abs(other - m) % 12
        if ic in CONSONANT: continue
        # dissonant downbeat sustained: check prep and resolution
        prep_other = sounding(v0, b)
        prep_ok = prep_other is not None and abs(prep_other - m) % 12 in CONSONANT
        res = v1.get(down + 0.5)
        res_ok = res is not None and 0 < m - res[0] <= 2
        if prep_ok and res_ok:
            suspensions.append(down)
        else:
            violations.append({"beat": down,
                               "prepared": prep_ok, "resolved_down": res_ok})
    print(json.dumps({
        "syncope_compliant": compliant,
        "onbeat_attacks_in_cs": on_beats,
        "offbeat_attacks": len(off_attacks),
        "valid_suspensions": len(suspensions), "at": suspensions,
        "grammar_violations": violations,
        "meets_budget": len(suspensions) >= 3,
    }, indent=1))

main(sys.argv[1])
