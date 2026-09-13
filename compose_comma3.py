#!/usr/bin/env python3
"""Comma Ascent III -- the subject transformed.

The first version proved the idea and little else: subject, drone, fifth. This
one keeps the same argument -- entries climbing the circle of fifths so that
Werckmeister III widens the third under them -- and adds the counterpoint the
argument deserves, on one rule: TEXTURE FOLLOWS THE GRADIENT. Pure keys are
thin and slow; as the thirds widen the entries overlap, a countersubject
arrives, and at F# the stretto is two beats apart in four voices. The collapse
to F strips back to two voices at the same instant the third purifies, so
relief arrives in texture and tuning together.
"""
MAJ = [0, 2, 4, 5, 7, 9, 11]

def scale(root, n):
    """midi of the nth diatonic step above root (n may be negative)."""
    return root + MAJ[n % 7] + 12 * (n // 7)

# The subject as diatonic STEPS from the tonic, so it can be inverted and
# augmented without leaving the key: 1 3 2 5 4 3, the third held and exposed.
STEPS = [(0, 2.0), (2, 2.0), (1, 1.0), (4, 1.0), (3, 1.0), (2, 1.0)]
CSTEP = [(4, 1.0), (5, 1.0), (6, 1.0), (7, 1.0), (5, 2.0), (4, 1.0), (2, 1.0)]

def subject(root, invert=False, scale_by=1.0):
    """Upright, or mirrored about the tonic. Inverted, the major third the
    piece is about becomes a minor SIXTH below -- the same tempered interval
    heard from underneath, which beats at a different rate for the same comma."""
    return [(scale(root, -n if invert else n), d * scale_by) for n, d in STEPS]

ev = []
def put(v, b, notes, vel, trim=None):
    t = b
    for i, (m, d) in enumerate(notes):
        if trim is not None and i >= trim: break
        ev.append((v, t, m, d, vel)); t += d
    return t

def hold(v, b, m, d, vel): ev.append((v, b, m, d, vel))

def suspend(v, b, root, vel):
    """4-3 over the entry: the upper voice holds the fourth across the bar and
    falls to the third exactly where the subject reaches its own third, so the
    interval the whole piece is about arrives as a RESOLUTION rather than a
    drone. How sweet or sour that arrival is, is the temperament talking."""
    ev.append((v, b, scale(root, 3), 2.0, vel))
    ev.append((v, b + 2, scale(root, 2), 2.0, vel - 4))

def episode(b, root, hi, vhi, vlo, vel):
    """Falling sequence in parallel diatonic thirds (not octaves: an octave is
    rooted, and the evaluator hears common fate there as one merged voice)."""
    t = b
    for i in range(8):
        d = hi - i
        ev.append((vhi, t, scale(root, d), 0.5, vel))
        ev.append((vlo, t, scale(root, d - 2), 0.5, vel - 6))
        t += 0.5
    return t

# ---------------------------------------------------------------- I. ascent
put(1, 0, subject(60), 72);                 hold(3, 0, 48, 8, 62)      # C  +3.9
put(0, 8, subject(67), 76)                                             # G  +9.7
put(1, 8, [(scale(55, n), d) for n, d in CSTEP], 64)
hold(3, 8, 43, 8, 64)
episode(16, 62, 11, 0, 1, 68);              hold(3, 16, 50, 4, 60)
put(2, 20, subject(50), 78)                                            # D  +9.7
put(0, 20, [(scale(62, n), d) for n, d in CSTEP], 68)
suspend(1, 24, 62, 70);                     hold(3, 20, 38, 8, 66)
episode(28, 57, 11, 0, 1, 70);              hold(3, 28, 45, 4, 62)
put(1, 32, subject(57), 80)                                            # A  +15.7
put(0, 32, [(scale(69, n), d) for n, d in CSTEP], 72)
put(2, 36, subject(45), 74, trim=4);        hold(3, 32, 45, 8, 68)
put(0, 40, subject(76), 82)                                            # E  +15.7
put(1, 40, [(scale(64, n), d) for n, d in CSTEP], 74)
suspend(2, 44, 52, 72);        hold(3, 40, 40, 8, 70)
put(2, 48, subject(59), 84)                                            # B  +15.7
put(0, 48, [(scale(83, n), d) for n, d in CSTEP], 76)
put(1, 52, subject(71), 78, trim=4);        hold(3, 48, 47, 8, 72)
# ---------------------------------------------------------------- II. F# peak
# the subject AUGMENTED in the pedal -- twice the note values, so the widest
# third in the temperament is held four beats instead of two
put(3, 56, subject(42, scale_by=2.0), 80)
put(2, 57, subject(54), 84)                                            # F# +21.5
put(1, 59, subject(66), 86)
put(0, 61, subject(78), 88)
put(2, 65, subject(61), 86, trim=4)
put(1, 67, subject(73), 88, trim=4)
put(0, 69, subject(85), 90, trim=4)
hold(0, 72, 85, 8, 90); hold(1, 72, 78, 4, 88)
suspend(1, 76, 66, 88)                      # the peak resolves onto its own third
hold(2, 72, 73, 8, 86); hold(3, 72, 42, 8, 82)
# ---------------------------------------------------------------- III. descent
# inverted and halved: the return is faster than the climb, and the third is
# now heard as a sixth below
for i, (rt, v, vel) in enumerate([(78, 0, 84), (71, 1, 80), (76, 2, 78),
                                  (69, 0, 74), (74, 1, 70), (67, 2, 66)]):
    b = 80 + 4 * i
    put(v, b, subject(rt, invert=True, scale_by=0.5), vel)
    hold(3, b, [42, 47, 40, 45, 38, 43][i], 4, 74 - 3 * i)
# ---------------------------------------------------------------- IV. home
put(0, 104, subject(77), 68);               hold(3, 104, 41, 8, 60)    # F  +3.9
put(1, 112, subject(60), 64)
suspend(0, 116, 72, 60)                     # last suspension, onto the pure third
hold(3, 112, 48, 8, 58)
hold(0, 120, 84, 8, 56); hold(1, 120, 76, 8, 54)
hold(2, 120, 67, 8, 52); hold(3, 120, 36, 8, 50)

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
head = ["# Title: Comma Ascent III -- the subject transformed", "# tempo 56",
        "# Voices: V0 soprano, V1 alto, V2 tenor, V3 pedal", "#"]
head += ["# " + l for l in __doc__.strip().splitlines()[2:]] if __doc__ else []
head += ["// Patch V%d: 19" % v for v in range(4)] + [""]
open('comma_ascent3.midgrid', 'w').write("\n".join(head + out) + "\n")
print("wrote comma_ascent3.midgrid: %d rows, %d events, last beat %g"
      % (len(out), len(ev), max(rows)))
