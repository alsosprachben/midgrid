from mido import Message, MidiFile, MidiTrack, MetaMessage
from sys import argv
import re

args = dict(enumerate(argv))
midgrid_in_path = args[1]
midgrid_out_path = args[2]

# Voice aliases
voice_alias = {'S': 0, 'A': 1, 'T': 2, 'B': 3}

# Read file lines and parse patch configs
with open(midgrid_in_path) as f:
    raw_lines = f.readlines()

lines = []
patches = {}  # voice_index -> patch number
patch_directives = []  # (line_index, voice_index, patch_number)

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

# Note converter
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

# Determine voice count from first data line
first_data = lines[0].split('|')
voice_count = len(first_data) - 1

# Fill patch list from default or fallbacks
patch_list = [patches.get(i, 19) for i in range(voice_count)]

# Parse grid data
notes = [[] for _ in range(voice_count)]
annotations = []

for line in lines:
    comment_split = line.split('//')
    core = comment_split[0].strip()
    annotation = comment_split[1].strip() if len(comment_split) > 1 else ""
    annotations.append(annotation)

    parts = core.split('|')
    parts = parts[:voice_count + 1]
    parts = [p.strip() for p in parts]
    while len(parts) < voice_count + 1:
        parts.append('')

    for i in range(voice_count):
        cell_meta = parse_note_cell(parts[i + 1])
        notes[i].append(cell_meta)

# Setup MIDI
mid = MidiFile(ticks_per_beat=480)
meta = MidiTrack()
meta.append(MetaMessage('set_tempo', tempo=int(60_000_000 / 96)))
mid.tracks.append(meta)

tracks = [MidiTrack() for _ in range(voice_count)]
for track in tracks:
    mid.tracks.append(track)

# Write MIDI
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

# Save
mid.save(midgrid_out_path)
print(f"Saved {midgrid_out_path}")
