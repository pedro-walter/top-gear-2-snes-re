#!/usr/bin/env python3 -I
"""Headless Mesen2 session driver.  python3 -I tools/run.py [options]   (no window, no X server)

  --ver usa|eur|jpn   ROM (default usa)         --frames N      frames to run
  --input "300:start,420:start,600:a+right:30"  button presses  frame:buttons[:len]
  --shots 300,600     screenshots  -> out/<tag>_<frame>.png
  --dumps 600         WRAM/VRAM/CGRAM/OAM dumps -> out/<tag>_<frame>.{wram,vram,cgram,oam}
  --state 600         save state   -> out/<tag>_<frame>.mss      --load file.mss  load one at frame 1
  --trace             execution coverage -> out/<tag>_trace.txt  (seeds for tools/disasm.py)
  --watch 7E0010-7E0012:w,00B6D1:x   log writes/reads/execs -> out/<tag>_watch.txt
  --lua file.lua      extra script (may define on_frame(f), on_input(f)->buttons, on_finish())
  --preset race       prepend the menu navigation that starts a race (see PRESETS)
  --tag name          output prefix (default 's')
Buttons: a b x y l r start select up down left right
"""
import argparse, os, subprocess, sys
ap = argparse.ArgumentParser()
ap.add_argument('--ver', default='usa'); ap.add_argument('--frames', type=int, default=600)
ap.add_argument('--input', default=''); ap.add_argument('--shots', default=''); ap.add_argument('--dumps', default='')
ap.add_argument('--state', default=''); ap.add_argument('--load'); ap.add_argument('--trace', action='store_true')
ap.add_argument('--watch'); ap.add_argument('--lua'); ap.add_argument('--tag', default='s')
ap.add_argument('--preset', choices=['race'], help="race: menu -> 1P START -> RACE -> car shop -> race (green flag ~frame 2900)")
ap.add_argument('--quiet', action='store_true', help='hide emulator log noise (default hides "Uninitialized memory read")')
a = ap.parse_args()
PRESETS = {'usa': '700:down,780:a,1000:a,1200:a,1500:start',   # USA menu has a START row
           'eur': '700:down,730:down,760:down,800:a,1100:a,1300:a,1500:start',   # EUR/JPN: cursor to RACE GAME
           'jpn': '700:down,730:down,760:down,800:a,1100:a,1300:a,1500:start'}
if a.preset: a.input = PRESETS[a.ver] + (',' + a.input if a.input else '')
if False: a.input = a.input + (',' + a.input if a.input else '')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = dict(os.environ, TG2_VER=a.ver, TG_FRAMES=str(a.frames), TG_INPUT=a.input, TG_SHOTS=a.shots, TG_DUMPS=a.dumps,
           TG_STATE=a.state, TG_TAG=a.tag, TG_TRACE='1' if a.trace else '0')
for k, v in (('TG_LOAD', a.load), ('TG_WATCH', a.watch), ('TG_LUA', a.lua)):
    if v: env[k] = os.path.abspath(v)
os.makedirs(os.path.join(root, 'out'), exist_ok=True)
p = subprocess.run([os.path.join(root, 'tools/mesen.sh'), os.path.join(root, 'scripts/session.lua')], env=env, capture_output=True, text=True)
for l in (p.stdout + p.stderr).splitlines():
    if 'Uninitialized memory read' not in l: print(l)
sys.exit(p.returncode)
