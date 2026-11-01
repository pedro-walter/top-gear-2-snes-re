# Top Gear 2 (SNES) reverse engineering

Sister project of `../snes-rea` (Top Gear 1; read its `docs/` and `README.md` for method, 65816 conventions and the
randomizer/assembler workflow). Phases: **1 environment (done)**, 2 understand the code, 3 modify it.

## ROMs (`roms/`, gitignored, 1 MB LoROM FastROM `$30`, no header, no SRAM)
| ver | file | `--ver` | country byte | checksum |
|---|---|---|---|---|
| USA | Top Gear 2 (USA).sfc | usa | 01 | 1CD4 |
| Europe | Top Gear 2 (Europe).sfc | eur | 02 | 15E7 |
| Japan | Top Racer 2 (Japan).sfc | jpn | 00 | see romcmp |
Native NMI/IRQ vectors are `$0000/$0004` = WRAM stubs again (same trick as TG1); code is decompressed to WRAM at boot, so
disassembly needs a runtime trace + WRAM image (the Makefile does it).

## Headless emulator (no window, no X server)
Mesen2 `--testRunner` + Lua, binary in `tools/mesen/` (copied from snes-rea; gitignored), isolated HOME in `tools/mesen-home/`.
~300 fps; a 3000-frame race boot takes ~10 s. Several runs can be launched in parallel.
* `python3 -I tools/run.py --ver usa --preset race --frames 3300 --input "3000:x:300" --shots 3300 --dumps 3300 --tag foo`
  (`python3 -I tools/run.py -h` for everything: input script, screenshots, WRAM/VRAM/CGRAM/OAM dumps, save states, exec trace, watchpoints, extra Lua)
* `scripts/session.lua` is the engine; write probes as a Lua file with `on_frame(f)` / `on_input(f)` and pass `--lua`.
  Helpers: `R.rd/R.rw` (CPU bus), `R.ram/R.ramw` (WRAM 0..1FFFF), `R.pc()`, `R.shot(name)`. Paths come from `os.getenv("TG_ROOT")`.
* `tools/montage.py out.png a.png b.png ...` tiles screenshots so one Read shows many frames. **Look at screenshots to verify.**
* Emulator noise "[CPU] Uninitialized memory read" is filtered by run.py. Outputs go to `out/` (gitignored).
* `--preset race` navigates the menus to a 1P race on Auckland (green flag ~frame 2900; USA/EUR/JPN menus differ, handled per version).
  Menu: title ~600 -> press Start toggles 1P/2P (leave on 1P!) -> down to START / RACE GAME -> A -> mode menu (RACE) -> A -> track -> A -> car shop -> Start -> race.
  In a race: **X accelerates**; Start pauses (L+R quits). Europe/Japan HUD in km/h, 50 Hz in Europe.

## Tools (`python3 -I tools/<x>.py`)
`disasm.py` (65816 recursive disassembler, M/X tracking, trace seeds), `asm65816.py` (assembler for patches), `romcmp.py`,
`asmdiff.py` (compare versions), `make_ips.py`, `sheet.py`/`vramview.py` (tile/VRAM viewers), `montage.py`. Ported from TG1; they may need
adapting to TG2's differences (1 MB, different data layout).

## Make targets
`make smoke | race VER=eur | trace VER=jpn | disasm VER=usa`

## Conventions
* Keep notes in `docs/NN-topic.md` as findings are verified (like snes-rea). Hand-verified labels go in `disasm/names_<ver>.txt`.
* Never commit ROMs or derived data; patches only as IPS of our bytes.
