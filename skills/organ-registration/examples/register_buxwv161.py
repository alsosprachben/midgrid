#!/usr/bin/env python3
"""My CC-driven registration of Buxtehude's Passacaglia in D minor, BuxWV 161.

The piece is a ground bass (tr5) under continuous variations (tr2-4), in the
classic d-F-a-d tonal scheme (sections at beats 0/180/360/540). Registration
grows with the form -- moderate, brighten for the F-major lift, fuller for
a minor, full pleno + pedal reed for the d-minor return and Picardy close --
while the pedal ground stays clearly present throughout.

  Great  ch0 p19 (flue) <- tr2,3,4 (variations)   8+4 -> +2 -> +2 2/3 -> full+16
  Pedal  ch1 p19 (flue) <- tr5 (ground)           8+4 -> 16+8 (gravity from F)
  P.Reed ch2 p20 (reed) <- tr5                     Posaune 16+8, final section only

CC11 flue bits: 0=8' 1=4' 2=2' 3=2 2/3' 4=16' 5=5 1/3';  reed: 0=8' 1=16' 2=4'.
"""
import mido

SRC = "/home/ben/Downloads/buxtehude_passacaglia.mid"
DST = "/home/ben/Downloads/buxtehude_passacaglia_registered.mid"
TPB = 1024
SECT = [0, 180 * TPB, 360 * TPB, 540 * TPB]   # d, F, a, d-return  (ticks)

GREAT_TRACKS = [2, 3, 4]
PEDAL_TRACK  = 5

# per-section CC11 masks (4 sections: d / F / a / d-return)
GREAT = [0b000011, 0b000111, 0b001111, 0b011111]   # 8+4 / +2 / +2 2/3 / +16
PEDAL = [0b000011, 0b010001, 0b010001, 0b010001]   # 8+4 / 16+8 ...
REED  = [0b000000, 0b000000, 0b000000, 0b000011]   # reed Posaune only in the return
# NEW: a Great Trompette (reed bit3, dynamic-locks to hybrid) crowns the d-return climax.
TRUMPET = [0b000000, 0b000000, 0b000000, 0b001000]  # trumpet stop, d-return only

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
    ev = [(0, 0, mido.Message('program_change', channel=ch, program=prog, time=0))]
    for tick, mask in zip(SECT, masks):
        ev.append((tick, 1, mido.Message('control_change', channel=ch, control=11, value=mask)))
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
    for ti in GREAT_TRACKS: great += read_notes(src, ti)
    pedal = read_notes(src, PEDAL_TRACK)

    out = mido.MidiFile(type=1, ticks_per_beat=TPB)
    cond = mido.MidiTrack()
    cond.append(mido.MetaMessage('set_tempo', tempo=454545, time=0))   # 132 bpm, matches source
    cond.append(mido.MetaMessage('track_name', name='BuxWV161 registered', time=0))
    cond.append(mido.MetaMessage('end_of_track', time=0))
    out.tracks.append(cond)
    out.tracks.append(make_channel_track(0, 19, great, GREAT))
    out.tracks.append(make_channel_track(1, 19, pedal, PEDAL))
    out.tracks.append(make_channel_track(2, 20, pedal, REED))
    out.tracks.append(make_channel_track(3, 20, great, TRUMPET))   # Great Trompette (d-return climax)
    out.save(DST)
    print("wrote", DST, "| tracks", len(out.tracks), "| len %.1fs" % out.length,
          "| great", len(great), "pedal", len(pedal))

if __name__ == "__main__":
    main()
