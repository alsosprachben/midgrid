from mido import Message, MidiFile, MidiTrack, MetaMessage
from sys import argv
import re
import math

args = dict(enumerate(argv))
midgrid_in_path = args[1]
midgrid_out_path = args[2]

# Collect other MIDI events (non-meta, non-voice tracks)
other_midi_events = []

# Voice aliases
voice_alias = {'S': 0, 'A': 1, 'T': 2, 'B': 3}

with open(midgrid_in_path) as f:
    raw_lines = f.readlines()

# Parse tempo changes from raw_lines
tempo_changes = []
seen_tempos = set()
for line in raw_lines:
    line_strip = line.strip()
    if line_strip.startswith("# tempo"):
        parts = line_strip.split()
        if len(parts) >= 3:
            try:
                bpm = float(parts[2])
                if len(parts) >= 4:
                    at_beat = float(parts[3])
                else:
                    at_beat = 0.0
                key = (round(bpm, 6), round(at_beat, 6))
                # Deduplicate tempo changes at same beat and bpm
                if key not in seen_tempos:
                    tempo_changes.append((at_beat, bpm))
                    seen_tempos.add(key)
            except ValueError:
                pass

# Sort tempo changes by beat
tempo_changes.sort(key=lambda x: x[0])

lines = []
patches = {}
patch_directives = []

for line_index, line in enumerate(raw_lines):
    line_strip = line.strip()
    if line_strip.startswith("// Patch"):
        match = re.match(r'//\s*Patch\s+(?:(V\d+)|([A-Z])):\s*(\d+)', line_strip)
        if match:
            v_label = match.group(1)
            s_label = match.group(2)
            patch = int(match.group(3))

            if v_label:
                voice_idx = int(v_label[1:])
            elif s_label:
                voice_idx = voice_alias.get(s_label)
                if voice_idx is None:
                    raise ValueError(f"Unknown voice label '{s_label}' in Patch directive.")
            else:
                raise ValueError("Malformed Patch directive.")

            if line_index == 0:
                patches[voice_idx] = patch
            else:
                # Deduplicate patch directives for same line and voice
                if not any(pd[0] == len(lines) and pd[1] == voice_idx and pd[2] == patch for pd in patch_directives):
                    patch_directives.append((len(lines), voice_idx, patch))
    elif line_strip.startswith("# events"):
        break  # stop collecting grid lines at event section
    elif line_strip and not line_strip.startswith("#"):
        lines.append(line)

    # After collecting raw grid lines and patch directives, use raw_lines for grid parsing
    lines = [l for l in raw_lines if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("//")]

note_map = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11,
            'B-': 10, 'A-': 8, 'E-': 3}

def note_to_midi(pitch):
    if pitch in ('-', '_', '.'):
        return None
    name = pitch[:-1]
    octave = int(pitch[-1])
    return 12 * (octave + 1) + note_map[name]

def parse_note_cell(cell):
    cell = cell.strip()
    if not cell or cell in ('.', '-', '_'):
        return {'velocity': 70, 'patch': None, 'pitch': '.', 'duration': None, 'midi': None}

    # if '//' in cell:
    #     cell = cell.split('//')[0].strip()

    meta = {'velocity': 70, 'patch': None}

    if '~' in cell:
        cell, patch = cell.split('~')
        meta['patch'] = int(patch.strip())

    if '@' in cell:
        cell, vel = cell.split('@')
        meta['velocity'] = int(vel.strip())

    if ':' in cell:
        pitch, dur = cell.split(':')
        meta['pitch'] = pitch.strip()
        meta['duration'] = float(dur.strip())
    else:
        meta['pitch'] = cell.strip()
        meta['duration'] = 1.0

    meta['midi'] = note_to_midi(meta['pitch'])
    return meta

first_data = lines[0].split('|')
voice_count = len(first_data) - 1
patch_list = [patches.get(i, 19) for i in range(voice_count)]

notes = [[] for _ in range(voice_count)]
beats = []

for line in lines:
    comment_split = line.split('//')
    core = comment_split[0].strip()
    parts = core.split('|')
    parts = parts[:voice_count + 1]
    parts = [p.strip() for p in parts]
    while len(parts) < voice_count + 1:
        parts.append('')
    try:
        beat_val = float(parts[0])
        beats.append(beat_val)
    except ValueError:
        # For lines without a valid beat, still append None to keep line alignment
        beats.append(None)
    for i in range(voice_count):
        notes[i].append(parse_note_cell(parts[i + 1]))

# Fill in implicit durations by extending notes only until the next beat row
for v in range(voice_count):
    for i in range(len(notes[v])):
        meta = notes[v][i]
        if meta["duration"] is not None:
            continue
        start_beat = beats[i]
        if start_beat is None:
            meta["duration"] = 1.0
            continue
        # Find next valid beat row (not necessarily a note)
        for j in range(i + 1, len(beats)):
            if beats[j] is not None:
                meta["duration"] = beats[j] - start_beat
                break
        else:
            meta["duration"] = 1.0

mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack()

# Insert tempo changes at correct tick positions
last_tick = 0
last_beat = 0.0
last_tempo = None
for beat, bpm in tempo_changes:
    delta_beats = beat - last_beat
    delta_ticks = int(delta_beats * mid.ticks_per_beat)
    delta_time = max(0, delta_ticks - last_tick)
    tempo = int(60_000_000 / bpm)
    if last_tempo != tempo or abs(beat - last_beat) > 1e-9:
        meta.append(MetaMessage('set_tempo', tempo=tempo, time=delta_time))
        last_tick += delta_time
        last_beat = beat
        last_tempo = tempo

if not tempo_changes:
    meta.append(MetaMessage('set_tempo', tempo=int(60_000_000 / 96)))

mid.tracks.append(meta)

tracks = [MidiTrack() for _ in range(voice_count)]
for track in tracks:
    mid.tracks.append(track)

# Scan all tracks (except meta and voice tracks) for additional events
for track in mid.tracks:
    abs_time = 0
    for msg in track:
        abs_time += msg.time
        if msg.type in ('control_change', 'pitchwheel', 'aftertouch', 'text', 'program_change'):
            beat = abs_time / mid.ticks_per_beat
            event_dict = msg.dict()
            event_dict.pop('time')
            other_midi_events.append((beat, msg.type, event_dict))

current_patches = patch_list.copy()
for i in range(voice_count):
    track = tracks[i]
    if i not in current_patches or current_patches[i] != patch_list[i]:
        track.append(Message('program_change', program=patch_list[i], channel=i))
        current_patches[i] = patch_list[i]
    current_note = None
    current_time = 0  # track elapsed ticks in this track

    row_idx = 0
    for meta in notes[i]:
        for (directive_row, voice_idx, patch_num) in patch_directives:
            if directive_row == row_idx and voice_idx == i:
                if current_patches[i] != patch_num:
                    track.append(Message('program_change', program=patch_num, time=0, channel=i))
                    current_patches[i] = patch_num

        if meta['patch'] is not None and meta['patch'] != current_patches[i]:
            track.append(Message('program_change', program=meta['patch'], time=0, channel=i))
            current_patches[i] = meta['patch']

        note = meta['midi']
        dur = int(meta['duration'] * 480) if meta['duration'] is not None else 480
        vel = meta['velocity']

        if meta['pitch'] == '.':
            # Explicit rest
            track.append(Message('note_off', note=0, velocity=0, time=dur, channel=i))
            current_note = None
        else:
            if note != current_note:
                if current_note is not None:
                    # Turn off previous note
                    track.append(Message('note_off', note=current_note, velocity=70, time=0, channel=i))
                if note is not None:
                    # Start new note
                    track.append(Message('note_on', note=note, velocity=vel, time=0, channel=i))
                current_note = note

            # Hold note for duration
            if note is not None:
                track.append(Message('note_off', note=note, velocity=70, time=dur, channel=i))
                current_note = None
            else:
                track.append(Message('note_off', note=0, velocity=0, time=dur, channel=i))
        row_idx += 1

    if current_note is not None:
        track.append(Message('note_off', note=current_note, velocity=70, time=0, channel=i))

mid.save(midgrid_out_path)
print(f"Saved {midgrid_out_path}")
# === PERCEPTUAL CONTRAPUNTAL REPORT ===

def build_harmonic_complexity_table():
    interval_definitions = {
        0:  ("Unison",       (1, 1)),
        1:  ("Minor 2nd",    (15, 16)),
        2:  ("Major 2nd",    (8, 9)),
        3:  ("Minor 3rd",    (5, 6)),
        4:  ("Major 3rd",    (4, 5)),
        5:  ("Perfect 4th",  (3, 4)),
        6:  ("Tritone",      (32, 45)),
        7:  ("Perfect 5th",  (2, 3)),
        8:  ("Minor 6th",    (5, 8)),
        9:  ("Major 6th",    (3, 5)),
        10: ("Minor 7th",    (7, 9)),
        11: ("Major 7th",    (8, 15)),
        12: ("Octave",       (1, 2)),
    }
    table = {}
    for semitone, (name, (h1, h2)) in interval_definitions.items():
        table[semitone] = {
            "name": name,
            "harmonics": (h1, h2),
            "complexity": h1 + h2,
            "phase_aligned": (h2 & (h2 - 1)) == 0
        }
    return table

def build_extended_harmonic_complexity_table(max_semitones=127):
    base_table = build_harmonic_complexity_table()
    extended_table = {}
    for semitone in range(max_semitones + 1):
        iclass = semitone % 12
        octaves = semitone // 12
        if iclass in base_table:
            b = base_table[iclass]
            h1, h2 = b["harmonics"]
            h1 *= 2 ** octaves
            h2 *= 2 ** octaves
            total_complexity = h1 + h2
            adjusted = total_complexity / (1 + octaves) ** 2
            extended_table[semitone] = {
                "name": f"{b['name']} (+{octaves} oct)" if octaves else b["name"],
                "harmonics": (h1, h2),
                "perceptual_complexity": round(adjusted, 3),
                "phase_aligned": b["phase_aligned"]
            }
        else:
            extended_table[semitone] = {
                "name": "Undefined",
                "harmonics": (1, 99),
                "perceptual_complexity": 100.0,
                "phase_aligned": False
            }
    return extended_table

def build_sounding_notes(notes, beats):
    voice_count = len(notes)
    row_count = len(beats)
    sounding_at_beat = []
    for row_idx, current_beat in enumerate(beats):
        if current_beat is None:
            sounding_at_beat.append([None] * voice_count)
            continue
        current_state = []
        for v in range(voice_count):
            sounding_note = None
            for prev_row in range(row_idx, -1, -1):
                note_meta = notes[v][prev_row]
                start_beat = beats[prev_row]
                if start_beat is None:
                    continue
                duration = note_meta.get("duration", 1.0)
                if duration is None:
                    continue
                end_beat = start_beat + duration
                if start_beat <= current_beat < end_beat:
                    sounding_note = note_meta["midi"]
                    break
            current_state.append(sounding_note)
        sounding_at_beat.append(current_state)
    return sounding_at_beat

def contrapuntal_report(notes, beats):
    table = build_extended_harmonic_complexity_table()
    lines = []
    sounding = build_sounding_notes(notes, beats)
    num_voices = len(notes)
    for row, midis in enumerate(sounding):
        if beats[row] is None:
            continue
        lines.append(f"Beat {beats[row]:.2f}:")
        for i in range(num_voices):
            for j in range(i + 1, num_voices):
                m1, m2 = midis[i], midis[j]
                if m1 is None or m2 is None:
                    interval = "rest"
                    motion = "n/a"
                    pscore = "n/a"
                else:
                    interval = abs(m2 - m1)
                    motion = "unknown"
                    if row > 0:
                        prev1 = sounding[row - 1][i]
                        prev2 = sounding[row - 1][j]
                        if prev1 is not None and prev2 is not None:
                            d1 = m1 - prev1
                            d2 = m2 - prev2
                            if d1 == 0 or d2 == 0:
                                motion = "oblique"
                            elif (d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0):
                                motion = "contrary"
                            elif d1 == d2:
                                motion = "parallel"
                            else:
                                motion = "similar"
                    cx = table.get(interval)
                    pscore = cx["perceptual_complexity"] if cx else "?"
                    interval_name = cx["name"] if cx else f"{interval} semitones"
                    if cx and cx["phase_aligned"]:
                        interval_name += " [phase-aligned]"
                    lines.append(f"  V{i}–V{j}: interval={interval_name}, motion={motion}, perceptual_complexity={pscore}")
    return "\n".join(lines)

report_text = contrapuntal_report(notes, beats)
report_path = midgrid_out_path.replace(".mid", ".report.txt")
with open(report_path, "w") as rep:
    rep.write(report_text)
print(f"Perceptual contrapuntal analysis written to {report_path}")
