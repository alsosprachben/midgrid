#!/usr/bin/env python3
"""Re-register BuxWV 140 the CC-driven way (replaces the 8-channel octave hack).

One organ channel per division; the renderer stacks the ranks itself from a
CC11 stop bitfield, terraced per section. Drops the redundant Manual II doubling
and strips the source's old CC7/CC11 automation (repurposed now).

  Great  ch0  prog 19 (flue)  <- S,A,T   Prelude 8+4+2+2 2/3 | Fugue 8+4 | Close +16
  Pedal  ch1  prog 19 (flue)  <- B        16+8 throughout
  P.Reed ch2  prog 20 (reed)  <- B        Posaune 16+8, Prelude & Close only (rests in fugue)

CC11 bitfield bits: flue 0=8' 1=4' 2=2' 3=2 2/3' 4=16' 5=5 1/3';
                    reed 0=8' 1=16' 2=4'.
"""
import mido

SRC = "/home/ben/Downloads/buxtehude_buxwv140_flat.mid"
DST = "/home/ben/Downloads/buxtehude_buxwv140_registered_cc.mid"
TPB = 480
B = TPB
PRELUDE_END = 120 * B
FUGUE_END   = 636 * B

GREAT_VOICES = [1, 2, 3]   # S, A, T
PEDAL_VOICE  = 4           # bass -> pedal

# per-section CC11 masks
GREAT = {"prelude": 0b001111, "fugue": 0b000011, "close": 0b011111}   # +16' in the close
PEDAL = {"prelude": 0b010001, "fugue": 0b010001, "close": 0b010001}   # 16'+8' (bits 0,4)
REED  = {"prelude": 0b000011, "fugue": 0b000000, "close": 0b000011}   # reed 8'+16'; silent in fugue
# NEW: a Great Trompette (reed bit3, dynamic-locks to hybrid) crowns the close only.
TRUMPET = {"prelude": 0b000000, "fugue": 0b000000, "close": 0b001000}   # trumpet stop, close peroration

def read_notes(mid, ti):
    t = 0; on = {}; out = []
    for msg in mid.tracks[ti]:
        t += msg.time
        if msg.type == 'note_on' and msg.velocity > 1:
            on.setdefault(msg.note, []).append((t, msg.velocity))
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity <= 1):
            q = on.get(msg.note)
            if q:
                s, v = q.pop(0); out.append((s, t, msg.note, v))
    return out

def make_channel_track(ch, prog, notes, masks):
    # events: (tick, order, mido.Message) -- order keeps prog_change < CC < notes at a tick
    ev = [(0, 0, mido.Message('program_change', channel=ch, program=prog, time=0))]
    ev.append((0,               1, mido.Message('control_change', channel=ch, control=11, value=masks["prelude"])))
    ev.append((PRELUDE_END,     1, mido.Message('control_change', channel=ch, control=11, value=masks["fugue"])))
    ev.append((FUGUE_END,       1, mido.Message('control_change', channel=ch, control=11, value=masks["close"])))
    for s, e, n, v in notes:
        ev.append((s, 2, mido.Message('note_on',  channel=ch, note=n, velocity=v, time=0)))
        ev.append((e, 3, mido.Message('note_off', channel=ch, note=n, velocity=0, time=0)))
    ev.sort(key=lambda x: (x[0], x[1]))
    tr = mido.MidiTrack(); last = 0
    for tick, _, msg in ev:
        msg.time = tick - last; last = tick
        tr.append(msg)
    tr.append(mido.MetaMessage('end_of_track', time=0))
    return tr

def main():
    src = mido.MidiFile(SRC)
    great = []
    for ti in GREAT_VOICES: great += read_notes(src, ti)
    pedal = read_notes(src, PEDAL_VOICE)

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    cond = mido.MidiTrack()
    cond.append(mido.MetaMessage('set_tempo', tempo=500000, time=0))
    cond.append(mido.MetaMessage('track_name', name='BuxWV140 CC-registered', time=0))
    cond.append(mido.MetaMessage('end_of_track', time=0))
    out.tracks.append(cond)
    out.tracks.append(make_channel_track(0, 19, great, GREAT))
    out.tracks.append(make_channel_track(1, 19, pedal, PEDAL))
    out.tracks.append(make_channel_track(2, 20, pedal, REED))
    out.tracks.append(make_channel_track(3, 20, great, TRUMPET))   # Great Trompette (close)
    out.save(DST)
    print("wrote", DST, "| type", out.type, "| tracks", len(out.tracks),
          "| len %.1fs" % out.length, "| great", len(great), "pedal", len(pedal))

if __name__ == "__main__":
    main()
