#!/usr/bin/env python3
"""Comma Ascent IV.

Three complaints against the last draft, all mine:

  - The subject was a function, not a tune: 1-3-2-5-4-3, shaped only to expose
    the third. Nothing to recognise when it entered.
  - The keys did not modulate, they abutted. Stop, move the pedal up a fifth,
    start again -- seven panels rather than a journey, which undercuts the
    whole arc, since the arc IS the piece.
  - The ending resolved by fiat: four octaves of C, sustained, unearned.

The subject now opens with a rising major SIXTH onto the third and holds it
there -- one gesture, recognisable, and it arrives at the note the piece is
about by leap instead of by default. It inverts about THAT NOTE rather than
about the tonic: the axis of the mirror is the third itself, so the leap turns
over into a falling sixth while the held note stays exactly where it was. The
transformation leaves the subject of the piece invariant, which is the whole
argument in one device.

Each section now spends its last two beats on the NEXT key's dominant, so the
new key arrives as a resolution instead of a reset, and F at the end is both
the subdominant of the cadence and the purest third in the temperament -- the
harmony and the tuning finally wanting the same note.
"""
MAJ = [0, 2, 4, 5, 7, 9, 11]
def scale(root, n): return root + MAJ[n % 7] + 12 * (n // 7)

#            up a 6th to the 3rd, hold it, fall away, reach, settle
STEPS = [(-3, 1.0), (2, 3.0), (1, 1.0), (0, 1.0), (3, 1.0), (2, 1.0)]
AXIS  = 2                      # mirror about the third, not the tonic
# complements the subject rhythmically: moves where the subject holds, holds
# where it moves, and leans a 2nd onto the reach so it resolves to a 3rd
CSTEP = [(5, 1.0), (7, 1.0), (6, 1.0), (5, 1.0), (4, 4.0)]

def subject(root, invert=False, k=1.0):
    return [(scale(root, (2 * AXIS - n) if invert else n), d * k) for n, d in STEPS]
def csub(root):
    return [(scale(root, n), d) for n, d in CSTEP]

ev = []
def put(v, b, notes, vel, trim=None):
    t = b
    for i, (m, d) in enumerate(notes):
        if trim is not None and i >= trim: break
        ev.append((v, t, m, d, vel)); t += d
    return t
def hold(v, b, m, d, vel): ev.append((v, b, m, d, vel))
def suspend(v, b, root, vel, d=2.0):
    ev.append((v, b, scale(root, 3), d, vel))
    ev.append((v, b + d, scale(root, 2), d, vel - 4))
def episode(b, root, hi, vhi, vlo, vel, n=8):
    for i in range(n):
        d = hi - i
        ev.append((vhi, b + i * .5, scale(root, d), .5, vel))
        ev.append((vlo, b + i * .5, scale(root, d - 2), .5, vel - 6))

def pedal(b, tonic, nxt, span, vel):
    """Tonic for most of the span, then the NEXT key's dominant, so the
    following entry arrives as a resolution rather than a fresh start."""
    hold(3, b, tonic, span - 2, vel)
    hold(3, b + span - 2, nxt, 2, vel)

# ------------------------------------------------------------- I. the ascent
put(1, 0, subject(60), 72);            pedal(0, 48, 50, 8, 62)    # C  +3.9
put(0, 8, subject(67), 76)                                        # G  +9.7
put(1, 8, csub(55), 64);               pedal(8, 43, 45, 8, 64)
episode(16, 62, 11, 0, 1, 68);         hold(3, 16, 50, 4, 62)
put(2, 20, subject(50), 78)                                       # D  +9.7
put(0, 20, csub(62), 68)
suspend(1, 25, 62, 70);                pedal(20, 38, 40, 8, 66)
put(1, 28, subject(57), 80)                                       # A  +15.7
put(0, 28, csub(69), 72)
put(2, 33, subject(45), 74, trim=3);   pedal(28, 45, 47, 10, 68)
put(0, 38, subject(76), 82)                                       # E  +15.7
put(1, 38, csub(64), 74)
suspend(2, 41, 52, 72);                pedal(38, 40, 42, 8, 70)
put(2, 46, subject(59), 84)                                       # B  +15.7
put(0, 46, csub(83), 76)
put(1, 50, subject(71), 78, trim=3);   pedal(46, 47, 42, 8, 72)
# ------------------------------------------------------------- II. F#, the peak
put(3, 54, subject(42, k=2.0), 80)                                # augmented
put(2, 55, subject(54), 84)                                       # +21.5
put(1, 57, subject(66), 86)
put(0, 59, subject(78), 88)
put(2, 63, subject(61), 86, trim=3)
put(1, 65, subject(73), 88, trim=3)
put(0, 67, subject(85), 90, trim=3)
hold(3, 70, 42, 8, 82)
hold(0, 72, 85, 6, 90); hold(2, 72, 73, 6, 86)
suspend(1, 72, 66, 88, d=3.0)          # the peak resolves onto its own third
# ------------------------------------------------------------- III. descent
for i, (rt, v, ped, vel) in enumerate([(78, 0, 42, 84), (71, 1, 47, 80),
                                       (76, 2, 40, 78), (69, 0, 45, 74),
                                       (74, 1, 38, 70), (67, 2, 43, 66)]):
    b = 78 + 4 * i
    put(v, b, subject(rt, invert=True, k=0.5), vel)
    hold(3, b, ped, 4, 76 - 3 * i)
# ------------------------------------------------------------- IV. the cadence
put(0, 102, subject(77), 68)                                      # F  +3.9
hold(1, 102, 60, 4, 58); hold(1, 106, 65, 4, 56)
pedal(102, 41, 43, 8, 60)              # subdominant, then the dominant
suspend(0, 110, 55, 66, d=2.0)         # 4-3 over G: the cadence, prepared
hold(1, 110, 62, 4, 58); hold(3, 110, 43, 4, 58)
hold(0, 114, 84, 8, 60); hold(1, 114, 76, 8, 56)                   # C, earned
hold(2, 114, 67, 8, 54); hold(3, 114, 48, 8, 52)

rows = {}
for v, b, m, d, vel in ev: rows.setdefault(round(b, 3), {})[v] = (m, d, vel)
NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
nn = lambda m: "%s%d" % (NAMES[m % 12], m // 12 - 1)
ends = {v: 0.0 for v in range(4)}; out = []
for b in sorted(rows):
    cells = []
    for v in range(4):
        if v in rows[b]:
            m, d, vel = rows[b][v]; ends[v] = b + d
            cells.append("%s@%d" % (nn(m), vel))
        else: cells.append("-" if ends[v] > b + 1e-6 else ".")
    out.append("%-5g | %-9s | %-9s | %-9s | %-9s" % (b, *cells))
head = ["# Title: Comma Ascent IV -- the third as axis", "# tempo 56",
        "# Voices: V0 soprano, V1 alto, V2 tenor, V3 pedal", "#"]
head += ["# " + l for l in __doc__.strip().splitlines()[2:]]
head += ["// Patch V%d: 19" % v for v in range(4)] + [""]
open('comma_ascent4.midgrid', 'w').write("\n".join(head + out) + "\n")
print("wrote comma_ascent4.midgrid: %d rows, %d events, last beat %g"
      % (len(out), len(ev), max(rows)))
