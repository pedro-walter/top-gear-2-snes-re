#!/bin/bash
# prints the ROM path for a version: tools/rompath.sh usa|eur|jpn
D="$(cd "$(dirname "$0")/.." && pwd)"
case "$1" in usa) echo "$D/roms/Top Gear 2 (USA).sfc";; eur) echo "$D/roms/Top Gear 2 (Europe).sfc";; jpn) echo "$D/roms/Top Racer 2 (Japan).sfc";; *) exit 2;; esac
