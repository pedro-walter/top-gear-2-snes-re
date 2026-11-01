#!/bin/bash
# usage: tools/fuzzdl.sh VER FRAMES SEEDS...  menu fuzz with decompressor-call logging -> out/fd_<ver><seed>_decomp.txt
V=$1; F=$2; shift 2; cd "$(dirname "$0")/.."
export TG_TIMEOUT=1200
for s in "$@"; do
  if [ "$V" = usa ]; then DA=01DC53 DB=01DE85; else DA=${TG_DA:-01DC53} DB=${TG_DB:-01DE85}; fi
  TG_DA=$DA TG_DB=$DB TG_SEED=$s TG_FUZZ_FROM=600 python3 -I tools/run.py --ver $V --frames $F --lua scripts/fuzzdl.lua --tag fd_$V$s >/dev/null 2>&1 &
done; wait
