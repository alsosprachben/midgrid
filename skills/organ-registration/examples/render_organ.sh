#!/usr/bin/env bash
# render_organ.sh -- the full organ pipeline in one command:
#   block-render (with headroom)  ->  cathedral reverb  ->  peak-normalise  -> mp3
#
# The renderer (../tuning/blockrender.py) plays the physical-model organ; the
# reverb and headroom are post-render sox steps, so they live here rather than in
# the tuning code. Produces <out>.dry.wav (keep it -- re-reverb without
# re-rendering), <out>.wav (wet), and <out>.mp3 if lame is present.
#
# Usage:
#   render_organ.sh INPUT.mid [tuner] [outbase]
#     tuner    adaptive tuning temperament (default: hybrid, for Baroque)
#     outbase  output basename (default: INPUT without .mid)
#
# Env overrides:
#   TUNING_DIR        path to the ../tuning repo (default: sibling of the midgrid
#                     repo, i.e. .../repos/tuning)
#   TUNING_MASTER_DB  render headroom in dB (default: -16). A dense plenum + the
#                     reverb tail will clip at the stock level; render quiet, let
#                     the final normalise bring it back to -1 dBFS. No clip = no
#                     baked-in distortion on the climaxes.
#   REVERB            sox reverb args (default: the Ben-approved cathedral,
#                     "reverb 88 15 100 100 28 -3.5"). Drop the wet-gain toward
#                     -5..-9 for a drier chapel/hall.
set -euo pipefail

IN="${1:?usage: render_organ.sh INPUT.mid [tuner] [outbase]}"
TUNER="${2:-hybrid}"
OUT="${3:-${IN%.mid}}"

# ../tuning is a sibling of the midgrid repo: examples -> organ-registration ->
# skills -> midgrid -> repos, then /tuning.
DEFAULT_TUNING="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/tuning"
TUNING_DIR="${TUNING_DIR:-$DEFAULT_TUNING}"
export TUNING_MASTER_DB="${TUNING_MASTER_DB:--16}"
REVERB="${REVERB:-reverb 88 15 100 100 28 -3.5}"

BLK="$TUNING_DIR/blockrender.py"
[ -f "$BLK" ] || { echo "blockrender.py not found at $BLK -- set TUNING_DIR" >&2; exit 1; }

DRY="${OUT}.dry.wav"
WET="${OUT}.wav"

echo ">> render:    $IN  (tuner=$TUNER, headroom=${TUNING_MASTER_DB} dB)"
python3 "$BLK" "$IN" "$DRY" "$TUNER"

echo ">> cathedral: sox ... vol 0.6 pad 0 6 $REVERB gain -n -1"
sox "$DRY" "$WET" vol 0.6 pad 0 6 $REVERB gain -n -1

FF="$(sox "$WET" -n stats 2>&1 | awk '/Flat factor/{print $3; exit}')"
echo ">> Flat factor: $FF   (must be 0.00 -- if not, lower TUNING_MASTER_DB)"

if command -v lame >/dev/null 2>&1; then
  lame --quiet -V2 "$WET" "${OUT}.mp3" && echo ">> wrote ${OUT}.mp3"
fi
echo ">> wrote $WET (and $DRY)"
