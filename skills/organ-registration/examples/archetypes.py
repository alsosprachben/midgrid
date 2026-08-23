#!/usr/bin/env python3
"""archetypes -- classify an organ piece's texture and give it a registration.

Ninety-six of the 111 Mutopia works are chorale preludes, and hand-designing a
bespoke registration for each is neither tractable nor useful: they fall into a
few textures whose registration is largely determined by the texture itself.
This module reads a converted MIDI, decides which archetype it is, assigns the
divisions, and returns stop-mask timelines. The famous ones then get hand-tuned
on top; the rest are good by construction.

The four archetypes and what identifies them:

  cantus_firmus  one voice moves in much longer notes than the others -- the
                 chorale tune. It wants a SOLO stop (the Flute, or a reed for a
                 big CF) against a quieter accompaniment, which is the whole
                 point of the genre: the congregation must hear the tune.
  trio           three voices of comparable activity, one of them the pedal.
                 Two manuals plus pedal, each light and distinct, nothing
                 doubled -- the texture only works if the lines stay separable.
  organo_pleno   four or more voices, dense, pedal present. The big
                 Clavier-Uebung settings: plenum, gravity, no solo.
  manualiter     no pedal at all (the CU III fughettas). One manual, modest.

Nothing here terraces much: a chorale prelude is two to four minutes long and
its registration is a *choice of colour*, not an arc. The free works get bespoke
treatment instead.
"""
import statistics as st
import mido
from reglib import (F8, F4, F2, F223, F16, FLUTE, MIXTUR, R8, R16, TRUMPET,
                    PLENUM, PEDAL_FOUND)


def voices_of(mid):
    """Per-track note statistics, skipping empty tracks."""
    TPB = mid.ticks_per_beat
    out = []
    for ti, tr in enumerate(mid.tracks):
        t = 0; on = {}; ns = []
        for x in tr:
            t += x.time
            if x.type == 'note_on' and x.velocity > 0:
                on.setdefault(x.note, []).append(t)
            elif x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0):
                q = on.get(x.note)
                if q:
                    s = q.pop(0); ns.append((s / TPB, (t - s) / TPB, x.note))
        if not ns: continue
        name = (next((x.name for x in tr if x.type == 'track_name'), '') or
                next((x.name for x in tr if x.type == 'instrument_name'), '')).strip()
        p = [n for _, _, n in ns]; d = [dd for _, dd, _ in ns]
        out.append({'track': ti, 'name': name, 'n': len(ns),
                    'median_pitch': st.median(p), 'lo': min(p), 'hi': max(p),
                    'median_dur': st.median(d),
                    'span': max(s + dd for s, dd, _ in ns) - min(s for s, _, _ in ns),
                    'density': len(ns) / max(1e-6, max(s + dd for s, dd, _ in ns))})
    return out


def assign(mid):
    """-> dict(pedal=track|None, cf=track|None, manuals=[tracks], archetype=str)"""
    vs = voices_of(mid)
    if not vs:
        return {'pedal': None, 'cf': None, 'manuals': [], 'archetype': 'empty', 'voices': vs}
    # PEDAL: a track named so, else the lowest voice if it really sits below the rest
    ped = next((v for v in vs if 'pedal' in v['name'].lower() or 'ped' == v['name'].lower()), None)
    if ped is None and len(vs) > 1:
        low = min(vs, key=lambda v: v['median_pitch'])
        others = [v['median_pitch'] for v in vs if v is not low]
        if others and st.median(others) - low['median_pitch'] >= 7:   # a fifth clear
            ped = low
    rest = [v for v in vs if v is not ped]
    # CANTUS FIRMUS: a manual voice in markedly longer notes than its fellows
    cf = None
    if len(rest) >= 2:
        cand = max(rest, key=lambda v: v['median_dur'])
        others = [v['median_dur'] for v in rest if v is not cand]
        if others and cand['median_dur'] >= 2.0 * st.median(others):
            cf = cand
    if ped is None:
        arch = 'manualiter'
    elif cf is not None:
        arch = 'cantus_firmus'
    elif len(rest) == 2:
        arch = 'trio'
    else:
        arch = 'organo_pleno'
    return {'pedal': ped['track'] if ped else None,
            'cf': cf['track'] if cf else None,
            'manuals': [v['track'] for v in rest if cf is None or v is not cf],
            'archetype': arch, 'voices': vs}


def registration(arch, end_beat):
    """Stop-mask timelines per division, as [(beat, mask)].

    `lift` is a modest brightening for the final phrase -- a chorale prelude
    closes, it does not peroration. Everything is deliberately restrained: the
    colour IS the registration here.
    """
    lift = max(0.0, end_beat - 8)
    if arch == 'cantus_firmus':
        return {'cf':      [(0, FLUTE)],                     # the tune, on a solo flute
                'manual':  [(0, F8)],                        # quiet accompaniment
                'pedal':   [(0, PEDAL_FOUND)],
                'posaune': [(0, 0)]}
    if arch == 'trio':
        return {'cf':      None,
                'manual':  [(0, F8 | F4)],                   # RH chorus
                'manual2': [(0, FLUTE)],                     # LH on a contrasting flute
                'pedal':   [(0, F8)],                        # light: a trio's bass is a LINE
                'posaune': [(0, 0)]}
    if arch == 'organo_pleno':
        return {'cf':      None,
                'manual':  [(0, PLENUM), (lift, PLENUM | F16)],
                'pedal':   [(0, PEDAL_FOUND)],
                'posaune': [(0, R8 | R16)]}
    return {'cf': None, 'manual': [(0, F8 | F4)], 'pedal': None, 'posaune': None}  # manualiter


def describe(a):
    v = a['voices']
    bits = ["%s: %d voices" % (a['archetype'], len(v))]
    if a['pedal'] is not None: bits.append("pedal=tr%d" % a['pedal'])
    if a['cf'] is not None: bits.append("CF=tr%d" % a['cf'])
    bits.append("manuals=%s" % a['manuals'])
    return ", ".join(bits)


if __name__ == "__main__":
    import sys, glob, os
    for p in sorted(sum([glob.glob(x) for x in sys.argv[1:]], [])):
        try:
            a = assign(mido.MidiFile(p))
            print("%-28s %s" % (os.path.basename(p), describe(a)))
        except Exception as e:
            print("%-28s ERROR %s" % (os.path.basename(p), repr(e)[:60]))
