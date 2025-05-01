#!/usr/bin/env python3
import sys
from mido import MidiFile, MetaMessage, tempo2bpm
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

def midi_note_to_name(note: int) -> str:
    octave = (note // 12) - 1
    name = NOTE_NAMES[note % 12]
    return f"{name}{octave}"

@dataclass
class NoteEvent:
    start_tick: int
    stop_tick: int
    note: str
    velocity: int
    channel: int
    voice: int
    patch: int

class MidiParser:
    def __init__(self, path: str):
        self.midi = MidiFile(path)
        self.ticks_per_beat = self.midi.ticks_per_beat
        self.tempo_changes: List[Tuple[int, int]] = []
        self.program_changes: Dict[int, int] = {}
        self.voice_map: Dict[int, int] = {}
        self._collect_meta()

    def _collect_meta(self):
        abs_ticks = 0
        for track in self.midi.tracks:
            abs_ticks = 0
            for msg in track:
                abs_ticks += msg.time
                if msg.type == 'set_tempo':
                    self.tempo_changes.append((abs_ticks, msg.tempo))
        # Ensure default tempo at start
        if not any(bt == 0 for bt, _ in self.tempo_changes):
            self.tempo_changes.insert(0, (0, 500000))

    def ticks_to_beats(self, tick: int) -> float:
        """
        Convert a raw MIDI tick into a beat number.
        """
        return tick / self.ticks_per_beat

    def parse_notes(self) -> List[NoteEvent]:
        # Collect all note and program messages per voice track (skip track 0 which is meta)
        all_events: List[Tuple[int, int, MetaMessage]] = []
        for voice_idx, track in enumerate(self.midi.tracks[1:]):
            abs_tick = 0
            for msg in track:
                abs_tick += msg.time
                all_events.append((abs_tick, voice_idx, msg))

        # Sort events by absolute tick to merge tracks
        all_events.sort(key=lambda x: x[0])

        active: Dict[int, List[Tuple[int, int, int]]] = {}
        note_events: List[NoteEvent] = []

        for abs_tick, voice_idx, msg in all_events:
            # Track program changes per track
            if msg.type == 'program_change':
                self.program_changes[voice_idx] = msg.program
                if voice_idx not in self.voice_map:
                    self.voice_map[voice_idx] = len(self.voice_map)

            # Note on
            if msg.type == 'note_on' and msg.velocity > 0:
                active.setdefault(voice_idx, []).append((abs_tick, msg.note, msg.velocity))
                if voice_idx not in self.voice_map:
                    self.voice_map[voice_idx] = len(self.voice_map)

            # Note off
            elif voice_idx in active and (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)):
                for i, (t0, note, vel) in enumerate(active[voice_idx]):
                    if note == msg.note:
                        ev = NoteEvent(
                            start_tick=t0,
                            stop_tick=abs_tick,
                            note=midi_note_to_name(note),
                            velocity=vel,
                            channel=msg.channel,
                            voice=self.voice_map[voice_idx],
                            patch=self.program_changes.get(voice_idx, 0)
                        )
                        note_events.append(ev)
                        del active[voice_idx][i]
                        break

        if not note_events:
            raise RuntimeError("No note events found in MIDI input.")
        return note_events

class Scheduler:
    def __init__(self, notes: List[NoteEvent], parser: MidiParser):
        self.notes = notes
        self.parser = parser
        self.tpb = parser.ticks_per_beat
        self.timeline: List[float] = []

    def build_timeline(self):
        times = set()
        for n in self.notes:
            times.add(self.parser.ticks_to_beats(n.start_tick))
            times.add(self.parser.ticks_to_beats(n.stop_tick))
        self.timeline = sorted(times)

    def schedule(self) -> Dict[int, Dict[float, str]]:
        self.build_timeline()
        voices = set(n.voice for n in self.notes)
        grid: Dict[int, Dict[float, str]] = {v: {} for v in voices}

        # Debug: print note tick-to-beat mappings
        for n in self.notes:
            b_start = self.parser.ticks_to_beats(n.start_tick)
            b_stop = self.parser.ticks_to_beats(n.stop_tick)
            print(f"DEBUG Note voice {n.voice} pitch {n.note}: "
                  f"tick {n.start_tick}->{b_start:.3f} beats, "
                  f"tick {n.stop_tick}->{b_stop:.3f} beats",
                  file=sys.stderr)

        print("DEBUG timeline beats:", self.timeline, file=sys.stderr)

        for n in self.notes:
            start = self.parser.ticks_to_beats(n.start_tick)
            stop  = self.parser.ticks_to_beats(n.stop_tick)

            # Compute duration in beats exactly once
            dur_beats = (stop - start)
            dur_str   = f":{dur_beats:.2f}".rstrip("0").rstrip(".") if dur_beats != 0 else ""

            vel_str   = f"@{n.velocity}" if n.velocity != 64 else ""
            patch_str = f"~{n.patch}"
            cell      = f"{n.note}{dur_str}{vel_str}{patch_str}"
            grid[n.voice][start] = cell

            # Fill holds
            for t in self.timeline:
                if start < t < stop:
                    grid[n.voice][t] = "-"

        # Fill rests
        for v in voices:
            for t in self.timeline:
                grid[v].setdefault(t, ".")

        return grid
    
class GridEmitter:
    def __init__(self,
                 grid: Dict[int, Dict[float, str]],
                 timeline: List[float],
                 program_changes: Dict[int, int],
                 voice_map: Dict[int, int],
                 tempo_changes: List[Tuple[int, int]],
                 ticks_per_beat: int):
        self.grid = grid
        self.timeline = timeline
        self.program_changes = program_changes
        self.voice_map = voice_map
        self.tempo_changes = tempo_changes
        self.tpb = ticks_per_beat

    def emit(self):
        # header
        print("# midgrid")
        seen = set()
        for tick, tempo in sorted(self.tempo_changes):
            bpm = tempo2bpm(tempo)
            beat = tick / self.tpb
            if bpm not in seen:
                seen.add(bpm)
                if beat > 0:
                    print(f"# tempo {bpm:.2f} {beat:.2f}".rstrip('0').rstrip('.'))
                else:
                    print(f"# tempo {bpm:.2f}")

        # determine labels
        max_voice = max(self.voice_map.values()) + 1
        voice_labels = {v: f"V{v}" for v in range(max_voice)}
        for ch, v in self.voice_map.items():
            lbl = voice_labels[v]
            patch = self.program_changes.get(ch, 0)
            print(f"// Patch {lbl}: {patch}")

        # print header row
        beat_col = "#beat"
        col_widths = [max(len(beat_col), 5)]
        for v in range(len(voice_labels)):
            col_widths.append(max(len(voice_labels[v]), 1))
        # update col widths
        for t in self.timeline:
            bstr = f"{t:.2f}".rstrip('0').rstrip('.')
            col_widths[0] = max(col_widths[0], len(bstr))
            for v in voice_labels:
                col_widths[v+1] = max(col_widths[v+1], len(self.grid[v][t]))

        header = [beat_col.ljust(col_widths[0])]
        for v in range(len(voice_labels)):
            header.append(voice_labels[v].ljust(col_widths[v+1]))
        print(" | ".join(header))

        # print rows
        for t in self.timeline:
            # skip empty
            if all(self.grid[v][t] == "." for v in voice_labels):
                continue
            beat = t
            row = [f"{beat:.2f}".rstrip('0').ljust(col_widths[0])]
            for v in voice_labels:
                row.append(self.grid[v][t].ljust(col_widths[v+1]))
            print(" | ".join(row))

        # events section
        print("\n# events")
        emitted = set()
        for tick, msg in sorted(self.tempo_changes + []):
            pass  # tempo already handled
        # we skip detailed event emission here for brevity

class MidGridEmitter:
    def __init__(self, path: str):
        self.path = path

    def run(self):
        parser = MidiParser(self.path)
        notes = parser.parse_notes()
        scheduler = Scheduler(notes, parser)
        grid = scheduler.schedule()
        emitter = GridEmitter(grid,
                              scheduler.timeline,
                              parser.program_changes,
                              parser.voice_map,
                              parser.tempo_changes,
                              parser.ticks_per_beat)
        emitter.emit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: midgrid_emitter.py <input.mid>")
        sys.exit(1)
    MidGridEmitter(sys.argv[1]).run()