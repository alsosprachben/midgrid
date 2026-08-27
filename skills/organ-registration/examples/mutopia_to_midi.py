#!/usr/bin/env python3
"""mutopia_to_midi.py -- compile Mutopia LilyPond organ scores to clean MIDI.

Mutopia carries 111 Bach organ works as native LilyPond. They are NOTATION (one
tempo, no interpretation), so everything they yield can take the full agogics
treatment -- but three things must be handled first:

1. **Age.** Sources are \\version 2.8.1-2.12.2; ours is 2.24. `convert-ly -e`
   is mandatory. One file (BWV 582) also starts with a UTF-8 BOM.
2. **Consort doublings.** Several files' MIDI score adds octave-transposed
   recorder/oboe parts so the piece is playable by a recorder consort. The
   organ staves are in the same MIDI, so the fix is to DROP any track that is an
   exact +-12 or +-24 transposition of an earlier one. (Verified on BWV 582, 639,
   659: dropping the duplicates recovers exactly the 3-voice organ texture.)
3. **Meta.** The registration and agogics stages both need the time signature,
   and the agogic grid silently lands on the wrong beats without it.

Usage:  mutopia_to_midi.py CORPUS_DIR OUT_DIR [--only BWV565,BWV582] [--jobs 1]
"""
import os, re, sys, glob, shutil, subprocess, statistics as st
import mido

HERE = os.path.dirname(os.path.abspath(__file__))

# Ornament signs LilyPond can name. The MIDI backend expands NONE of them, so we
# only ever recover them from the event-listener log -- hence the verification.
ORN_NAMES = {'prall', 'mordent', 'prallmordent', 'prallprall', 'upprall',
             'downprall', 'lineprall', 'trill', 'pralldown', 'upmordent',
             'downmordent', 'turn', 'reverseturn'}
ORN_RE = re.compile(r'\\(?:' + '|'.join(sorted(ORN_NAMES)) + r')\b')

DUP_SHIFTS = (12, -12, 24, -24)
STAFFISH = re.compile(r'right|left|pedal|upper|lower|manual|organ|soprano|alt|tenor|bass', re.I)


def notes_of(track):
    t = 0; on = {}; out = []
    for x in track:
        t += x.time
        if x.type == 'note_on' and x.velocity > 0:
            on.setdefault(x.note, []).append(t)
        elif x.type == 'note_off' or (x.type == 'note_on' and x.velocity == 0):
            q = on.get(x.note)
            if q: out.append((q.pop(0), x.note))
    return out


def drop_doublings(mid):
    """Remove tracks that merely transpose an earlier track by an octave or two."""
    info = [(ti, set(notes_of(tr))) for ti, tr in enumerate(mid.tracks)]
    info = [(ti, ns) for ti, ns in info if ns]
    drop = set()
    for a in range(len(info)):
        ia, na = info[a]
        if ia in drop: continue
        for b in range(a + 1, len(info)):
            ib, nb = info[b]
            if ib in drop: continue
            for sh in DUP_SHIFTS:
                shifted = {(s, n + sh) for s, n in nb}
                if na and len(na & shifted) / max(len(na), len(shifted)) > 0.85:
                    drop.add(ib); break
    if drop:
        mid.tracks = [tr for ti, tr in enumerate(mid.tracks) if ti not in drop]
    return sorted(drop)


def describe(mid):
    out = {'tempo_events': 0, 'time_sig': None, 'voices': []}
    for tr in mid.tracks:
        for x in tr:
            if x.type == 'set_tempo': out['tempo_events'] += 1
            elif x.type == 'time_signature' and out['time_sig'] is None:
                out['time_sig'] = "%d/%d" % (x.numerator, x.denominator)
    for ti, tr in enumerate(mid.tracks):
        ns = notes_of(tr)
        if not ns: continue
        p = [n for _, n in ns]
        nm = next((x.name for x in tr if x.type == 'track_name'), '') or \
             next((x.name for x in tr if x.type == 'instrument_name'), '')
        out['voices'].append({'track': ti, 'name': nm.strip(), 'n': len(ns),
                              'median': int(st.median(p)), 'lo': min(p), 'hi': max(p)})
    return out


def convert_one(ly, outdir, timeout=300, ev_timeout=1500):
    """-> (status, midi_path|None, report dict)"""
    base = os.path.splitext(os.path.basename(ly))[0]
    work = os.path.join(outdir, base + ".work")
    os.makedirs(work, exist_ok=True)
    src = os.path.join(work, base + ".ly")
    # copy the whole source dir: many files \include siblings
    for f in glob.glob(os.path.join(os.path.dirname(ly), "*")):
        if os.path.isfile(f): shutil.copy(f, work)
    with open(src, 'rb') as fh: data = fh.read()
    if data[:3] == b'\xef\xbb\xbf':                       # BOM (BWV 582)
        open(src, 'wb').write(data[3:])
    subprocess.run(["convert-ly", "-e", src], capture_output=True, timeout=120)

    # UNFOLD REPEATS. LilyPond's MIDI does not play a \repeat volta -- verified:
    # `\repeat volta 2 { c d e f } g1` yields 5 notes, `\repeat unfold` yields 9.
    # So 137 repeats across 29 works of this corpus were simply not being played,
    # and a chorale prelude that states its melody twice was coming out once.
    # Rewriting volta as unfold is what \unfoldRepeats does, and it survives
    # \alternative correctly (checked: two alternatives, both played, in order).
    # It must happen BEFORE the listener copy is made as well, or the log's
    # moments would no longer line up with the MIDI's.
    txt = open(src, errors='ignore').read()
    n_rep = txt.count("\\repeat volta")
    if n_rep:
        txt = txt.replace("\\repeat volta", "\\repeat unfold")

    # ONE MIDI CHANNEL PER VOICE. LilyPond packs all voices of a staff onto one
    # channel, and where two voices in a staff briefly share a pitch, one voice's
    # note-off ends the other's -- the durations swap, so a held note comes out
    # short and a passing note comes out long. 18 works here put two voices on a
    # staff. reglib.read_notes pairs by (channel, pitch), which only helps if the
    # channels differ, so the mapping has to be set at compile time.
    shutil.copy(os.path.join(HERE, "midi-voice-channels.ly"), work)
    txt = txt.replace("\\version", '\\include "midi-voice-channels.ly"\n\\version', 1)
    open(src, "w").write(txt)
    try:
        subprocess.run(["lilypond", "-dno-print-pages", "-dno-point-and-click",
                        "-o", base, src], cwd=work, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "failed", None, {"error": "lilypond timeout"}
    mids = sorted(glob.glob(os.path.join(work, "*.mid*")))
    if not mids:
        # Some engravings (BWV 651) ship the \midi score commented out with
        # %{ ... %}. Uncomment the block that contains it and retry.
        txt = open(src, errors='ignore').read()
        i, j = txt.rfind("%{"), txt.rfind("%}")
        if i != -1 and j > i and "\\midi" in txt[i:j]:
            open(src, "w").write(txt[:i] + txt[i + 2:j] + txt[j + 2:])
            try:
                subprocess.run(["lilypond", "-dno-print-pages", "-dno-point-and-click",
                                "-o", base, src], cwd=work, capture_output=True, timeout=timeout)
            except subprocess.TimeoutExpired:
                pass
            mids = sorted(glob.glob(os.path.join(work, "*.mid*")))
    if not mids:
        return "failed", None, {"error": "no MIDI produced"}
    # if several \score blocks emitted MIDI, keep the one with the most notes
    best, best_n, best_mid = None, -1, None
    for p in mids:
        try: m = mido.MidiFile(p)
        except Exception: continue
        n = sum(len(notes_of(tr)) for tr in m.tracks)
        if n > best_n: best, best_n, best_mid = p, n, m
    if best_mid is None:
        return "failed", None, {"error": "MIDI unreadable"}
    dropped = drop_doublings(best_mid)
    rep = describe(best_mid)
    rep['dropped_doublings'] = dropped
    rep['source'] = ly
    dst = os.path.join(outdir, base + ".mid")
    best_mid.save(dst)
    # ornaments: an event-listener pass, for the C.P.E. Bach realizer downstream
    ev = os.path.join(work, "ev_" + base + ".ly")
    # Our GUARDED copy of event-listener.ly, not the stock one: LilyPond 2.24.3's
    # listeners divide by a textual tempo mark's absent metronome-count and take
    # the length of duration-less events, either of which aborts the compile and
    # loses the entire log. BWV 565 (\tempo "Adagio", "Prestissimo") hit both, so
    # its ornaments -- including the famous opening mordent -- silently vanished.
    shutil.copy(os.path.join(HERE, "event-listener-safe.ly"), work)
    with open(src) as fh: body = fh.read()
    with open(ev, 'w') as fh:
        fh.write(body.replace('\\version', '\\include "event-listener-safe.ly"\n\\version', 1))
    for f in glob.glob(os.path.join(work, "*.notes")):
        os.remove(f)          # event-listener APPENDS; a stale log would double up
    try:
        subprocess.run(["lilypond", "-dno-print-pages", "-dno-point-and-click",
                        "-o", "ev_" + base, ev], cwd=work, capture_output=True,
                       timeout=ev_timeout)
    except subprocess.TimeoutExpired:
        pass
    rep['notes_logs'] = sorted(glob.glob(os.path.join(work, "*.notes")))

    # VERIFY the ornament pass instead of assuming it. Count the signs the score
    # actually carries and the signs the log captured; a score with ornaments and
    # a log without them means the render will silently lose them, which is
    # exactly how BWV 565 lost the most famous mordent in organ music.
    rep['unfolded_repeats'] = n_rep
    # anacrusis: the agogic bar grid must start from the DOWNBEAT, and 42
    # works in this corpus open with a pickup. Recorded in quarter notes.
    ana = re.search(r'\\\\partial\\s+([0-9]+)(\\.*)', body)
    rep['anacrusis_q'] = (4.0 / int(ana.group(1))) * (1.5 if ana.group(2) else 1.0) if ana else 0.0
    rep['orn_in_source'] = len(ORN_RE.findall(body))
    rep['orn_in_log'] = sum(
        sum(1 for l in open(f) if l.split('\t')[1:2] == ['script']
            and l.split('\t')[2:3] and l.split('\t')[2].strip() in ORN_NAMES)
        for f in rep['notes_logs'])
    # classify
    v = rep['voices']
    status = "clean"
    why = []
    if rep['tempo_events'] != 1: why.append("tempo_events=%d" % rep['tempo_events'])
    if rep['time_sig'] is None: why.append("no time signature")
    if not v: why.append("no notes")
    elif len(v) < 2: why.append("single voice")
    if dropped: why.append("dropped %d doubling(s)" % len(dropped))
    if rep['orn_in_source'] and not rep['orn_in_log']:
        why.append("ORNAMENTS LOST: %d in score, 0 logged" % rep['orn_in_source'])
    if why: status = "attention"
    rep['why'] = why
    return status, dst, rep


def pick_ly(cands, all_of_them=False):
    """Choose the master file of a multi-file work: it must contain a \\score
    (movement includes like Adagio.ly do not), and its name usually matches the
    directory (SonataIV-lys/SonataIV.ly). Falls back to the shortest path."""
    scored = []
    for f in cands:
        try:
            txt = open(f, errors='ignore').read()
        except Exception:
            continue
        base = os.path.splitext(os.path.basename(f))[0].lower()
        parent = os.path.basename(os.path.dirname(f)).lower().replace('-lys', '')
        scored.append(('\\score' in txt,
                       base == parent or base.startswith(parent) or parent.startswith(base),
                       -len(f), f))
    scored.sort(reverse=True)
    if all_of_them:
        return [f for *_, f in scored]
    return scored[0][3] if scored else None


def main():
    corpus, outdir = sys.argv[1], sys.argv[2]
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    os.makedirs(outdir, exist_ok=True)
    lys = []
    for d in sorted(os.listdir(corpus)):
        if only and d not in only: continue
        found = sorted(glob.glob(os.path.join(corpus, d, "*", "*.ly")) +
                       glob.glob(os.path.join(corpus, d, "*", "*", "*.ly")))
        # prefer a4 over letter-paper variants, and the shortest name (the main file)
        found = [f for f in found if '-let' not in os.path.basename(f)]
        ranked = pick_ly(found, all_of_them=True)
        if ranked: lys.append((d, ranked))
    print("converting %d works" % len(lys), flush=True)
    import json
    results = {}
    for d, cands in lys:
        status, dst, rep = "failed", None, {"error": "no candidate compiled"}
        for ly in cands:
            try:
                status, dst, rep = convert_one(ly, outdir)
            except Exception as e:
                status, dst, rep = "failed", None, {"error": repr(e)[:200]}
            if status != "failed":
                break   # some works ship two engravings; take the first that compiles
        results[d] = {"status": status, "midi": dst, **rep}
        v = rep.get('voices', [])
        print("%-9s %-9s %s" % (d, status,
              rep.get('error') or "%d voices, %s, tempo_ev=%d%s" % (
                  len(v), rep.get('time_sig'), rep.get('tempo_events', 0),
                  (" | " + "; ".join(rep['why'])) if rep.get('why') else "")), flush=True)
    # Each work's record is written to its OWN file, then the index is rebuilt
    # from them. A --only rerun must not wipe the other records (it silently did
    # once, which is how BWV 565's lost ornaments stayed hidden) -- and a plain
    # read-modify-write of one shared file cannot survive being run in parallel,
    # which is the obvious way to convert a corpus of this size.
    frag = os.path.join(outdir, "triage.d")
    os.makedirs(frag, exist_ok=True)
    for k, v in results.items():
        with open(os.path.join(frag, k + ".json"), "w") as fh:
            json.dump(v, fh, indent=1)
    merged = {}
    for f in sorted(glob.glob(os.path.join(frag, "*.json"))):
        try:
            with open(f) as fh: merged[os.path.basename(f)[:-5]] = json.load(fh)
        except Exception: pass
    with open(os.path.join(outdir, "triage.json"), "w") as fh:
        json.dump(merged, fh, indent=1)
    n = {"clean": 0, "attention": 0, "failed": 0}
    for r in results.values(): n[r['status']] += 1
    print("\nDONE  clean=%d attention=%d failed=%d" % (n['clean'], n['attention'], n['failed']))


if __name__ == "__main__":
    main()
