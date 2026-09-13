#!/usr/bin/env python3
"""Comma Ascent II -- density tracks the temperament.

The first version proved the idea and little else: subject, drone, fifth. This
one keeps the same argument -- entries climbing the circle of fifths so that
Werckmeister III widens the third under them -- and adds the counterpoint the
argument deserves, on one rule: TEXTURE FOLLOWS THE GRADIENT. Pure keys are
thin and slow; as the thirds widen the entries overlap, a countersubject
arrives, and at F# the stretto is two beats apart in four voices. The collapse
to F strips back to two voices at the same instant the third purifies, so
relief arrives in texture and tuning together.
"""
MAJ = [0, 2, 4, 5, 7, 9, 11]          # scale degrees -> semitones
def deg(d, alt=0): return MAJ[(d - 1) % 7] + 12 * ((d - 1) // 7) + alt

# subject: 1(2) 3(2) 2(1) 5(1) 4(1) 3(1) -- the third held, exposed
SUBJ = [(deg(1), 2.0), (deg(3), 2.0), (deg(2), 1.0),
        (deg(5), 1.0), (deg(4), 1.0), (deg(3), 1.0)]
# countersubject: moves where the subject holds, and leans on the 7th
CSUB = [(deg(5), 1.0), (deg(6), 1.0), (deg(7), 1.0), (deg(8), 1.0),
        (deg(7), 2.0), (deg(6), 1.0), (deg(5), 1.0)]
# episode cell: a falling sequence spun from the subject's tail
EPIS = [(deg(5), 0.5), (deg(4), 0.5), (deg(3), 0.5), (deg(2), 0.5)]

def scale(root, n):
    """midi of the nth diatonic degree above root (n may be negative)."""
    return root + MAJ[n % 7] + 12 * (n // 7)

def episode(b, root, hi, lo, vhi, vlo, vel):
    """A falling sequence in parallel diatonic THIRDS over the pedal.

    The first draft ran two voices through the same cell an octave apart; the
    evaluator heard that as fusion, and was right -- an octave is rooted, so
    common fate merges them. Thirds are not rooted that way: the sequence
    stays two voices, and it is the ordinary baroque episode texture."""
    t = b
    for i in range(8):
        d = hi - i
        ev.append((vhi, t, scale(root, d), 0.5, vel))
        ev.append((vlo, t, scale(root, d - 2), 0.5, vel - 6))
        t += 0.5
    return t

ev = []                                # (voice, beat, midi, dur, vel)
def put(v, b, root, pat, vel, oct=0, trim=None):
    t = b
    for i, (off, d) in enumerate(pat):
        if trim is not None and i >= trim: break
        ev.append((v, t, root + off + 12 * oct, d, vel))
        t += d
    return t

def hold(v, b, midi, dur, vel): ev.append((v, b, midi, dur, vel))

C, G, D, A, E, B, FS, F = 0, 7, 2, 9, 4, 11, 6, 5      # pitch classes
# ---------------------------------------------------------------- I. thin
put(1, 0,  60, SUBJ, 72)                      # S in C, alto, alone
hold(3, 0,  48, 8, 62)                        # pedal C2
put(0, 8,  67, SUBJ, 76)                      # answer in G, soprano
put(1, 8,  55, CSUB, 64)                      # countersubject arrives
hold(3, 8,  43, 8, 64)                        # pedal G1
# ---------------------------------------------------------------- episode -> D
episode(16, 62, 11, None, 0, 1, 68)        # over D, falling thirds
hold(3, 16, 50, 4, 60)
# ---------------------------------------------------------------- II. D, +9.7
put(2, 20, 50, SUBJ, 78)                      # S in D, tenor
put(0, 20, 62, CSUB, 68)   # D, with its subject (was A: G# over a D pedal)
hold(3, 20, 38, 8, 66)
put(1, 24, 62, SUBJ, 70, trim=4)              # overlap begins: partial entry
# ---------------------------------------------------------------- episode -> A
episode(28, 57, 11, None, 0, 1, 70)        # over A, inner pair
hold(3, 28, 45, 4, 62)
# ---------------------------------------------------------------- III. A, +15.7
put(1, 32, 57, SUBJ, 80)                      # S in A
put(0, 32, 69, CSUB, 72)   # A, with its subject
put(2, 36, 45, SUBJ, 74, trim=4)              # stretto at 4 beats
hold(3, 32, 45, 8, 68)
# ---------------------------------------------------------------- IV. E, +15.7
put(0, 40, 76, SUBJ, 82)                      # S in E
put(1, 40, 64, CSUB, 74)
put(2, 44, 52, SUBJ, 76, trim=4)
hold(3, 40, 40, 8, 70)
# ---------------------------------------------------------------- V. B, +15.7
put(2, 48, 59, SUBJ, 84)                      # S in B
put(0, 48, 83, CSUB, 76)
put(1, 52, 71, SUBJ, 78, trim=4)
hold(3, 48, 47, 8, 72)
# ---------------------------------------------------------------- VI. F#, +21.5  STRETTO
put(2, 56, 54, SUBJ, 84)                      # entries two beats apart
put(1, 58, 66, SUBJ, 86)
put(0, 60, 78, SUBJ, 88)
hold(3, 56, 42, 8, 76)
put(2, 64, 61, SUBJ, 86, trim=4)
put(1, 66, 73, SUBJ, 88, trim=4)
put(0, 68, 85, SUBJ, 90, trim=4)
hold(3, 64, 42, 8, 78)
# ---------------------------------------------------------------- the peak, held
hold(0, 72, 85, 8, 90); hold(1, 72, 78, 8, 88)
hold(2, 72, 73, 8, 86); hold(3, 72, 42, 8, 80)   # F# major, widest third
# ---------------------------------------------------------------- collapse: F, +3.9
put(0, 80, 77, SUBJ, 68)                      # two voices only
hold(3, 80, 41, 8, 60)
# ---------------------------------------------------------------- home
put(1, 88, 60, SUBJ, 64)
hold(3, 88, 48, 8, 58)
hold(0, 92, 76, 4, 58)
hold(0, 96, 84, 8, 56); hold(1, 96, 76, 8, 54)
hold(2, 96, 67, 8, 52); hold(3, 96, 36, 8, 50)   # pure third, four octaves of C

# ---------------------------------------------------------------- emit
rows = {}
for v, b, m, d, vel in ev:
    rows.setdefault(round(b, 3), {})[v] = (m, d, vel)
NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
def nn(m): return "%s%d" % (NAMES[m % 12], m // 12 - 1)
ends = {v: 0.0 for v in range(4)}
out = []
for b in sorted(rows):
    cells = []
    for v in range(4):
        if v in rows[b]:
            m, d, vel = rows[b][v]; ends[v] = b + d
            cells.append("%s@%d" % (nn(m), vel))
        else:
            cells.append("-" if ends[v] > b + 1e-6 else ".")
    out.append("%-5g | %-9s | %-9s | %-9s | %-9s" % (b, *cells))

hdr = __doc__.strip().splitlines()
head = ["# Title: Comma Ascent II -- density follows the temperament",
        "# tempo 56", "# Voices: V0 soprano, V1 alto, V2 tenor, V3 pedal", "#"]
head += ["# " + l for l in hdr[2:]]
head += ["// Patch V%d: 19" % v for v in range(4)] + [""]
open('comma_ascent2.midgrid', 'w').write("\n".join(head + out) + "\n")
print("wrote comma_ascent2.midgrid: %d rows, %d events, last beat %g"
      % (len(out), len(ev), max(rows)))
