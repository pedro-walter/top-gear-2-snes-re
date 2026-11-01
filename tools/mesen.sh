#!/bin/bash
# Headless Mesen2 runner (--testRunner: no window, no X needed).
# Usage: tools/mesen.sh script.lua [args]      ROM chosen with TG2_VER=usa|eur|jpn (default usa) or TG_ROM=path
# LD_PRELOAD works around std::bad_cast in MesenCore.so static init (std::regex vs. static libstdc++).
# HOME is isolated so the user's real ~/.config/Mesen2 is untouched.
D="$(cd "$(dirname "$0")/.." && pwd)"
export TG_ROOT="$D"
case "${TG2_VER:-usa}" in
  usa) R="$D/roms/Top Gear 2 (USA).sfc";;
  eur) R="$D/roms/Top Gear 2 (Europe).sfc";;
  jpn) R="$D/roms/Top Racer 2 (Japan).sfc";;
  *) echo "bad TG2_VER" >&2; exit 2;;
esac
export TG_ROM="${TG_ROM:-$R}"
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6
# per-run HOME copy so parallel runs don't clash on settings/lock
export HOME="$D/tools/mesen-home"
S="$HOME/.config/Mesen2/settings.json"
sed -i 's/"AllowIoOsAccess": false/"AllowIoOsAccess": true/; s/"ScriptTimeout": [0-9]*/"ScriptTimeout": 60/' "$S"
cd "$D"
exec timeout "${TG_TIMEOUT:-600}" "$D/tools/mesen/Mesen" --testRunner "$TG_ROM" "$@"
