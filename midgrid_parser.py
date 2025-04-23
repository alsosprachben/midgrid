from mido import Message, MidiFile, MidiTrack, MetaMessage
from sys import argv
import re
import math

args = dict(enumerate(argv))
midgrid_in_path = args[1]
midgrid_out_path = args[2]

# Voice aliases
voice_alias = {'S': 0, 'A': 1, 'T': 2, 'B': 3}

with open(midgrid_in_path) as f:
    raw_lines = f.readlines()

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
                patch_directives.append((len(lines), voice_idx, patch))
    elif line_strip and not line_strip.startswith("#"):
        lines.append(line)

note_map = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11,
            'B-': 10, 'A-': 8, 'E-': 3}

def note_to_midi(pitch):
    if pitch == '-' or pitch == '_':
        return None
    name = pitch[:-1]
    octave = int(pitch[-1])
    return 12 * (octave + 1) + note_map[name]

def parse_note_cell(cell):
    if '//' in cell:
        cell = cell.split('//')[0].strip()

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
    beats.append(float(parts[0]))
    for i in range(voice_count):
        notes[i].append(parse_note_cell(parts[i + 1]))

mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack()
meta.append(MetaMessage('set_tempo', tempo=int(60_000_000 / 96)))
mid.tracks.append(meta)

tracks = [MidiTrack() for _ in range(voice_count)]
for track in tracks:
    mid.tracks.append(track)

current_patches = patch_list.copy()
for i in range(voice_count):
    track = tracks[i]
    track.append(Message('program_change', program=current_patches[i], channel=i))
    current_note = None

    row_idx = 0
    for meta in notes[i]:
        for (directive_row, voice_idx, patch_num) in patch_directives:
            if directive_row == row_idx and voice_idx == i:
                track.append(Message('program_change', program=patch_num, time=0, channel=i))
                current_patches[i] = patch_num

        if meta['patch'] is not None and meta['patch'] != current_patches[i]:
            track.append(Message('program_change', program=meta['patch'], time=0, channel=i))
            current_patches[i] = meta['patch']

        note = meta['midi']
        dur = int(meta['duration'] * 480)
        vel = meta['velocity']

        if note != current_note:
            if current_note is not None:
                track.append(Message('note_off', note=current_note, velocity=70, time=0, channel=i))
            if note is not None:
                track.append(Message('note_on', note=note, velocity=vel, time=0, channel=i))
            current_note = note

        track.append(Message('note_off', note=0, velocity=0, time=dur, channel=i))
        row_idx += 1

    if current_note is not None:
        track.append(Message('note_off', note=current_note, velocity=70, time=0, channel=i))

mid.save(midgrid_out_path)
print(f"Saved {midgrid_out_path}")

# === CONTRAPUNTAL REPORT WITH SUSTAINED NOTES AND HARMONIC COMPLEXITY ===

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
            "complexity": h1 + h2
        }
    return table

def build_extended_harmonic_complexity_table(max_semitones=127):
    base_table = build_harmonic_complexity_table()
    extended_table = {}
    for semitone in range(max_semitones + 1):
        iclass = semitone % 12
        octaves = semitone // 12
        if iclass in base_table:
            h1, h2 = base_table[iclass]["harmonics"]
            h1 *= 2 ** octaves
            h2 *= 2 ** octaves
            extended_table[semitone] = {
                "name": f"{base_table[iclass]['name']} (+{octaves} oct)" if octaves else base_table[iclass]["name"],
                "harmonics": (h1, h2),
                "complexity": h1 + h2
            }
        else:
            extended_table[semitone] = {
                "name": "Undefined",
                "harmonics": (1, 99),
                "complexity": 100
            }
    return extended_table

def build_sounding_notes(notes, beats):
    voice_count = len(notes)
    row_count = len(beats)
    sounding_at_beat = []
    for row_idx, current_beat in enumerate(beats):
        current_state = []
        for v in range(voice_count):
            sounding_note = None
            for prev_row in range(row_idx, -1, -1):
                note = notes[v][prev_row]
                start_beat = beats[prev_row]
                end_beat = start_beat + note["duration"]
                if start_beat <= current_beat < end_beat:
                    sounding_note = note["midi"]
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
        lines.append(f"Beat {beats[row]:.2f}:")
        for i in range(num_voices):
            for j in range(i + 1, num_voices):
                m1, m2 = midis[i], midis[j]
                if m1 is None or m2 is None:
                    interval = "rest"
                    motion = "n/a"
                    complexity = "n/a"
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
                    complexity = cx["complexity"] if cx else "?"
                    interval_name = cx["name"] if cx else f"{interval} semitones"
                    lines.append(f"  V{i}–V{j}: interval={interval_name}, motion={motion}, complexity={complexity}")
    return "\n".join(lines)

# Save contrapuntal report
report_text = contrapuntal_report(notes, beats)
report_path = midgrid_out_path.replace(".mid", ".report.txt")
with open(report_path, "w") as rep:
    rep.write(report_text)
print(f"Contrapuntal analysis written to {report_path}")