#!/usr/bin/env python3

import sys
from mido import MidiFile, tempo2bpm
from collections import defaultdict

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_name(note):
    octave = (note // 12) - 1
    name = NOTE_NAMES[note % 12]
    return f"{name}{octave}"

def emit_midgrid_from_midi(midi_path, ticks_per_beat=480):
    midi = MidiFile(midi_path)

    # Track tempo changes, default tempo 500000 microseconds per beat (120 bpm)
    tempo = 500000
    tempo_changes = [(0, tempo)]  # list of (abs_time, tempo)
    # Track program changes per channel
    program_changes = defaultdict(lambda: 0)  # default instrument 0 (Acoustic Grand Piano)
    # Store note on events: key = channel, value = list of (start_time, velocity)
    active_notes = defaultdict(list)
    # Store finalized notes: list of dicts with keys: start_beat (float), note_name, duration, velocity, channel, voice
    finalized_notes = []

    # Voice assignment: map channel to voice number
    voice_map = {}
    next_voice = 0

    # Accumulate all messages with absolute time including meta events
    all_events = []
    for track in midi.tracks:
        abs_time = 0
        for msg in track:
            abs_time += msg.time
            if msg.type == 'program_change':
                program_changes[msg.channel] = msg.program
                if msg.channel not in voice_map:
                    voice_map[msg.channel] = next_voice
                    next_voice += 1
            all_events.append((abs_time, msg))
            if msg.type == 'set_tempo':
                tempo_changes.append((abs_time, msg.tempo))

    # Sort all events by absolute time to process in order
    all_events.sort(key=lambda x: x[0])

    # For beat calculation, we need to convert ticks to beats with tempo changes considered.
    # However, midgrid format appears to use beat numbers relative to ticks_per_beat, so we will use float beats = abs_time / ticks_per_beat
    # Tempo is output as metadata header, but does not affect beat calculation here.

    # Process events to track tempo and program changes first, and process notes
    for abs_time, msg in all_events:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            tempo_changes.append((abs_time, tempo))
        # Removed redundant program_change handling here since handled earlier
        elif msg.type == 'note_on' and msg.velocity > 0:
            key = msg.channel
            active_notes[key].append((abs_time, msg.note, msg.velocity))
            if key not in voice_map:
                voice_map[key] = next_voice
                next_voice += 1
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            key = msg.channel
            if key in active_notes:
                # Match the corresponding note_on by pitch
                for idx, (start_time, start_note, velocity) in enumerate(active_notes[key]):
                    if start_note == msg.note:
                        # Finalize this note
                        active_notes[key].pop(idx)
                        duration_ticks = abs_time - start_time
                        start_beat = start_time / ticks_per_beat
                        duration_beats = max(0.01, duration_ticks / ticks_per_beat)
                        finalized_notes.append({
                            'start_beat': start_beat,
                            'note_name': note_name(start_note),
                            'duration': duration_beats,
                            'velocity': velocity,
                            'channel': key,
                            'voice': voice_map[key]
                        })
                        break

    # Sort finalized notes by start_beat, then voice
    finalized_notes.sort(key=lambda x: (x['start_beat'], x['voice']))

    print("# midgrid")

    # Output tempo metadata header, avoiding duplicate tempos at the start
    seen_tempos = set()
    for abs_time, t in tempo_changes:
        bpm = tempo2bpm(t)
        if bpm in seen_tempos:
            continue
        seen_tempos.add(bpm)
        beat = abs_time / ticks_per_beat
        print(f"# tempo {bpm:.2f} {beat:.3f}" if beat > 0 else f"# tempo {bpm:.2f}")


    # Reverse mapping from voice to channel for patch lines
    voice_to_channel = {}
    for channel, voice in voice_map.items():
        voice_to_channel[voice] = channel

    # Assign SATB labels if possible
    # Mapping program numbers to SATB: Flute (73) → S, Clarinet (71) → A, Strings (48) → T, Organ (19) → B
    satb_map = {73: 'S', 71: 'A', 48: 'T', 19: 'B'}

    # Collect program numbers per voice
    voice_labels = {}
    used_labels = set()
    satb_labels = ['S', 'A', 'T', 'B']

    # First, try to assign SATB labels only if all voices have unique SATB programs with no duplicates
    programs = []
    for voice_id in range(next_voice):
        channel = voice_to_channel.get(voice_id, None)
        program_number = program_changes[channel] if channel is not None else 0
        programs.append(program_number)

    # Check if all programs are in satb_map and are unique
    if all(p in satb_map for p in programs) and len(set(programs)) == len(programs):
        # Assign labels based on program number
        assigned_labels = {}
        for voice_id in range(next_voice):
            channel = voice_to_channel.get(voice_id, None)
            program_number = program_changes[channel] if channel is not None else 0
            label = satb_map[program_number]
            voice_labels[voice_id] = label
    else:
        # Fallback to V0, V1, ...
        for voice_id in range(next_voice):
            voice_labels[voice_id] = f"V{voice_id}"

    # Print patch lines for each voice
    for voice_id in range(next_voice):
        channel = voice_to_channel.get(voice_id, None)
        program_number = program_changes[channel] if channel is not None else 0
        label = voice_labels[voice_id]
        print(f"// Patch {label}: {program_number}")

    # Build grid

    # Determine all voices count
    total_voices = next_voice

    # Build a sorted set of all real beats (start and end)
    beat_positions = sorted(set(
        round(n['start_beat'], 6) for n in finalized_notes
    ).union(set(
        round(n['start_beat'] + n['duration'], 6) for n in finalized_notes
    )))

    # Initialize timeline: voice -> beat -> symbol string
    timeline = {v: {b: '.' for b in beat_positions} for v in range(total_voices)}

    # Track current patch per voice to detect patch changes
    current_patch = {v: None for v in range(total_voices)}

    # Place notes in timeline
    for note in finalized_notes:
        voice = note['voice']
        start = round(note['start_beat'], 6)
        duration = note['duration']
        velocity = note['velocity']
        note_str = note['note_name']

        # Format note as NOTE[:duration][@velocity]
        duration_str = ""
        if duration != 1.0:
            duration_str = f":{duration:.3g}".rstrip('0').rstrip('.')
        velocity_str = f"@{velocity}" if velocity != 64 else ""  # default velocity 64 not shown

        # Determine patch for this note
        channel = voice_to_channel.get(voice, None)
        patch = program_changes[channel] if channel is not None else 0

        # Add patch change inline if different from current patch
        patch_str = ""
        if current_patch[voice] != patch:
            patch_str = f"~{patch}"
            current_patch[voice] = patch

        note_repr = f"{note_str}{duration_str}{velocity_str}{patch_str}"

        # Mark note start
        timeline[voice][start] = note_repr

        # Fill with '-' until next real note or end of duration
        end = round(note['start_beat'] + note['duration'], 6)
        for b in beat_positions:
            if start < b < end and timeline[voice][b] == '.':
                timeline[voice][b] = '-'

    # Placeholder for beat comments mapping
    # This dictionary maps beat position (float) to comment string
    # In future, comments could be parsed and stored in finalized_notes or elsewhere
    # For now, it is empty or can be populated as needed
    beat_comments = {}

    # Calculate column widths for aligned output
    # First column: beat column
    beat_col_width = max(len(f"{beat:.3g}") for beat in beat_positions)
    beat_col_width = max(5, beat_col_width, len("#beat"))

    # Voice columns: find max width per voice
    voice_col_widths = []
    for v in range(total_voices):
        label = voice_labels.get(v, f"V{v}")
        max_cell = len(label)
        for beat in beat_positions:
            cell = timeline[v][beat]
            if len(cell) > max_cell:
                max_cell = len(cell)
        voice_col_widths.append(max_cell)

    # Print header with alignment
    header_cols = [f"{'#beat':<{beat_col_width}}"]
    for v in range(total_voices):
        label = voice_labels.get(v, f"V{v}")
        header_cols.append(f"{label:<{voice_col_widths[v]}}")
    print(" | ".join(header_cols))

    # Print each beat row with aligned columns
    for beat in beat_positions:
        if all(timeline[v][beat] == '.' for v in range(total_voices)):
            continue
        row = [f"{beat:.3g}".ljust(beat_col_width)]
        for v in range(total_voices):
            cell = timeline[v][beat]
            row.append(cell.ljust(voice_col_widths[v]))
        line = " | ".join(row)
        comment = beat_comments.get(beat)
        if comment:
            line += f" // {comment}"
        print(line)

    # After grid, print events section
    print("\n# events")
    emitted_program_changes = set()
    for abs_time, msg in all_events:
        beat = abs_time / ticks_per_beat
        if msg.type == 'program_change':
            key = (beat, msg.channel)
            if key in emitted_program_changes:
                continue
            emitted_program_changes.add(key)
        if msg.type in ('control_change', 'pitchwheel', 'aftertouch', 'text', 'program_change'):
            parts = [f"{k}={v}" for k, v in msg.dict().items() if k != 'time']
            if msg.type == 'text':
                parts = [f"\"{msg.text}\""]
            print(f"[{beat:.3f}] {msg.type} " + " ".join(parts))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: midgrid_emitter.py input.mid")
        sys.exit(1)
    emit_midgrid_from_midi(sys.argv[1])