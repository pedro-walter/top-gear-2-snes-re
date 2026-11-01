#!/bin/bash
# usage: tools/champ.sh VER FRAMES TAG [A_PERIOD] [START_PERIOD] : championship autopilot (scripts/champ.lua) with trace -> out/f_<VER>_<TAG>_trace.txt
export TG_TIMEOUT=${TG_TIMEOUT:-7000}; V=$1; N=$2; T=$3; AP=${4:-70}; SP=${5:-400}; cd "$(dirname "$0")/.."
I="3000:x:$N"; for f in $(seq 7000 $AP $N); do I="$I,$f:a:4"; done; for f in $(seq 7200 $SP $N); do I="$I,$f:start:4"; done
python3 -I tools/run.py --ver $V --preset race --frames $N --input "$I" --lua scripts/champ.lua --trace --tag f_${V}_$T
