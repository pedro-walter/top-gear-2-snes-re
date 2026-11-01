#!/bin/bash
# usage: tools/fuzz.sh VER MODE SEEDS...   MODE=menu (from boot) | race (preset race, then fuzz holding X)
export TG_TIMEOUT=2400; V=$1; M=$2; shift 2; cd "$(dirname "$0")/.."
for s in "$@"; do
  if [ "$M" = race ]; then
    TG_SEED=$s TG_FUZZ_FROM=3000 TG_FUZZ_HOLD=x python3 -I tools/run.py --ver $V --preset race --frames 24000 --trace --lua scripts/fuzz.lua --tag f_${V}_${M}$s &
  else
    TG_SEED=$s TG_FUZZ_FROM=600 python3 -I tools/run.py --ver $V --frames 24000 --trace --lua scripts/fuzz.lua --tag f_${V}_${M}$s --shots 24000 &
  fi
done; wait
