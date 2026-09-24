# Renderer palette — the executable bridge

How a drawn stop becomes sound in `../tuning`. The engine is a physical-model
additive synth. The flue and reed **organ voices are registerable**: one organ
note builds its whole stop list of ranks internally, and you **draw stops with a
CC11 bitfield**, swell with **CC7**, and roll a crescendo with **CC4** — all live,
acting on notes already sounding. (Non-organ voices are one plain series.)

## Control map (the organ: FlueOrgan prog 19, flue AND reed stops)

| MIDI | Role |
|---|---|
| **velocity** | static per-note level / voice balance |
| **CC11** | **stop bitfield** — bit *i* draws rank *i* of the voice's stop list |
| **CC4**  | **crescendo pedal** — 0→127 rolls the stop list in cumulatively (max'd with CC11) |
| **CC7**  | **swell** — one shutter over the division: drops level **and** rolls off the highs |

Selecting an organ program defaults the drawn set to **8′-only**, so an organ
MIDI with no registration automation sounds as a single principal — exactly as
before this feature. Everything you hear beyond that you draw.

### Stop bitfield bits

- **Flue (prog 19)** — bit 0 = 8′, 1 = 4′, 2 = 2′, 3 = 2⅔′, 4 = Principal 16′
  (open), 5 = 5⅓′, **6 = Flute 8′**, **7 = Mixtur III**, and **12 = Bourdon
  16′** (stopped; `reglib.BOURDON16`, drawn with `CC43 = 32`).
- **Which 16′.** The Bourdon is a manual's usual 16′: a stopped pipe, soft,
  gravity *under* an 8′ rather than a second bass line. The open Principal 16′
  is grave and heavy — a pedal foundation, or the full pleno's weight.
- **Reeds — on the same console, prog 19**, bits **8 = reed 8′, 9 = reed 16′,
  10 = reed 4′, 11 = Trumpet 8′**. They used to be their own program, 20, with
  bits 0–3; but GM 20 is a *reed organ* — a free reed, a harmonium — and the
  renderer now plays it as one, so the pipe reeds moved onto the church organ.
  A reed division still gets its own channel: `reglib.console_reed()` takes the
  old 4-bit reed word and moves it up to bits 8–11, and `CONSOLE_PROGRAM` is 19.
  The worked examples below were written with `p20`; their scripts now do this.

The stop word is **14-bit**: **CC11 = bits 0–6**, **CC43 = bits 7–13**. So most
registrations are still one CC11 value = sum of `1<<bit` (8′+4′+2′+2⅔′ = `0b1111`
= 15; add 16′ = `0b11111` = 31; flute alone = 64; trumpet = 8) — but the **Mixtur
(bit 7) is drawn with `CC43=1`**. `CC43=0` (the default) is exactly the old 7-bit
behaviour. Defined in `stop_ranks` in `../tuning/tonelib.py`.

**Mixtur III** is a *compound* stop — one drawstop of several very high ranks
(1⅓′+1′+⅔′). It is the crown of a full Organo Pleno: draw it for the peroration/
climax (with the full plenum), not for ordinary counterpoint.

### The harpsichord is registerable too (prog 6/7)

A harpsichord has no dynamics either — you engage whole **choirs** of strings —
so it uses this same CC11 stop machinery:

- bit 0 = **8′ lower manual** (plucked further from the nut: round)
- bit 1 = **8′ upper manual** (plucked near the nut: nasal, bright)
- bit 2 = **4′ choir**
- bit 3 = **lute/buff stop** (dry, dull, short)

**Coupling = drawing both 8′ choirs** (`0b0011`) — mechanically what a coupler
does; `0b0111` (both 8′s + 4′) is the full *grand jeu*. Terrace the registers by
section exactly as for organ. Since registers are a harpsichord's only "dynamics,"
pair this with the `baroque-agogics` skill (arpégement, inégales) for the rest.

### Rank break-back (why the top never turns shrill)

Upper ranks don't run the full compass. Past a **pipe ceiling** (flue ~2.1 kHz,
reed ~1.6 kHz — reed tongues top out lower) a rank has no pipes and **breaks back
an octave**, folding onto the note's stretched grid so it stays hybrid-locked.
Only upperwork (4′ and above) breaks; the 8′/16′ foundation and a solo reed line
always keep their pipes. A Mixtur's ranks sit so high they fold constantly —
that *is* its "composition," and why an ascending run **re-colors** at the top
instead of climbing into shrillness. Automatic; nothing to set per piece.

**Cross-family stops (Flute on 19, Trumpet on 20).** A `stop_ranks` entry can
carry a 4th field, a *spectrum* class: that rank borrows only the timbre
(BlownPipe for the flute, BrightBrass for the trumpet) while the inharmonicity,
envelope and decay stay the base organ's — so you draw a flute or a chorus reed
as a bit, and it **locks to hybrid like every other stop**. So you no longer need
a separate BlownPipe/brass channel for those colors: it's all 19/20. A 5th field
`dynamic=True` forces a rank onto the flue's dynamic stretch — used on the Trumpet
(a harmonic reed on 20 would *beat* against the stretched flue, a slow phaser;
`dynamic` makes it lock instead).

### Why the ranks lock (inharmonicity)

Each rank is a full harmonic series placed a footage interval away on the note's
**own inharmonic-stretched grid** (4′ at harmonic index 2, 2′ at 4, 2⅔′ at 3,
16′ at 0.5, 5⅓′ at 1.5). A 4′ fundamental therefore lands *exactly* on the 8′'s
stretched 2nd partial, so the ranks reinforce and **lock under `hybrid`** instead
of beating — the alignment is automatic, no per-rank tuning needed. Mixtures ride
the harmonic series (authentic). Footage → interval, for reference:

| Stop | vs 8′ | harmonic index |  | Stop | vs 8′ | harmonic index |
|------|------|---:|-|------|------|---:|
| 16′ | −12 | 0.5 | | 2⅔′ | +19 | 3 |
| 8′  | 0   | 1   | | 2′  | +24 | 4 |
| 4′  | +12 | 2   | | 5⅓′ | +7  | 1.5 |

## Family → voice class (choosing the color)

Organ families you register with CC11/CC4/CC7 on one channel:

| Family | Voice class | Program | Notes |
|--------|-------------|--------:|-------|
| **Principal chorus** | `FlueOrganProperties` | **19** | the registerable flue; principals + mixtures, locks to `hybrid` |
| **Reed chorus** | `ReedOrganProperties` | **20** | the registerable reed; 8′/16′/4′ chorus, hollow reed tone |

Colors the stop list doesn't cover still go on **their own channel** as a plain
(non-registerable) voice — draw them by simply having notes there or not:

| Family | Voice class | Program | Use |
|--------|-------------|--------:|-----|
| Flute (Gedackt) | `BlownPipeProperties` | 72–79 | soft solo / accompaniment |
| String (Gamba) | `BowedStringProperties` | 40–44 | warmth under a chorus |
| Chorus reed (Trompette) | `BrightBrassProperties` | 56 | bright solo reed atop a pleno |
| Pedal reed (Posaune) | `DarkBrassProperties` | 58 | round pedal reed (brass isn't registerable) |

## Realization recipe (CC-driven)

1. **One organ channel per division** — Great on prog 19, Pedal on prog 19 (a
   second channel), a Positiv/reed on prog 19/20 as needed. Independence =
   separate channels, exactly like separate divisions.
2. **Draw the registration per section** with a **CC11** event at each section
   tick (program-change first, then CC11, at the same tick). Terraced, discrete —
   the Baroque way.
3. **Pedal gravity** = draw 16′ (+8′) on the pedal channel — the Principal for
   weight, the Bourdon (`BOURDON16`) for a softer Subbass; a Posaune adds a
   reed channel (prog 20 with 16′, or brass prog 58 on its own channel).
4. **Swell / crescendo** where wanted: a **CC7** ramp for an expressive swell on
   held notes, or a **CC4** sweep to roll stops in as a crescendo. Leave CC7 at
   127 for a purely terraced (stop-only) Baroque registration.

Velocity still sets the static per-voice level; draw the *color and weight* with
stops, not by riding velocity.

## Worked stop masks

- **Organo Pleno (Great flue):** CC11 = `0b1111` (8′+4′+2′+2⅔′).
- **Lighter fugal chorus:** CC11 = `0b11` (8′+4′).
- **Grand close:** Great `0b11111` (add 16′); pedal reed channel drawn.
- **Pedal foundation:** pedal flue CC11 = `0b10001` (16′+8′).
- **Crescendo instead of masks:** hold CC11 = `1` (8′) and sweep CC4 0→127.

## Tuning, reverb, and the clipping ceiling

- **Tuning:** `hybrid` for Baroque (meantone-quality thirds; principals lock).
  See `$tuning-render` and the [[hybrid-tuner-for-baroque]] memory.
- **Reverb:** organs get a **cathedral** — wet and enveloping, big room and
  pre-delay, but not the longest tail:
  `sox DRY OUT vol <V> pad 0 6 reverb 88 15 100 100 28 -3.5 gain -n -1`
  (reverberance 88, HF-damp 15, room 100, stereo 100, pre-delay 28 ms, wet −3.5 dB;
  see [[reverb-by-voice]]). Drop the wet-gain (−5…−9) for a drier chapel.
- **Density is the ceiling.** A full pleno is many simultaneous ranks — it *will*
  clip if `vol` is hot. After reverb **always** run `sox FILE -n stats` and
  require **Flat factor 0.00**; if not, lower `vol` (dense pleno often ~0.5) or
  append `gain -n -1`. Loudness comes from the drawn pyramid, not a hot `vol`.
