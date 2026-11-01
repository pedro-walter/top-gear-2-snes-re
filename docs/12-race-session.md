# Race session: start, frame loop, exit (bank 01 `8145..83BD`, read from the disassembly + traces)

Entered from the front-end through the race vector (`JSL` from `1F` after the shop); `$0102` bit15 selects **split-screen (2P) vs 1P**.

## Start (1P path `01:8145`; 2P path `01:840B` is the same with `08:D63F` / `0B:818A` as the 2P renderers and `01:90BD` instead of `01:8FAB`)
1. `00:CD09` (not yet read), `01:8717`, **`00:CD5E` car setup from the shop state** (see `09-car-setup.md`), `01:8FAB` (1P setup), `01:EF37` (DMA/copy of `$0400` bytes `7E:C910`->VRAM `$7800`?), **`00:D0DA`** (race/AI setup incl. `D1D4`, `05-ai-cars.md`).
2. First frame of `road_render` (`08:CB74`) and `hdma_build` (`0B:8000`); `$001A` (frame counter) is reset.
3. HDMA channels 0-6 are programmed here (`$4300-$4367`, source banks `7E`/`87`..; destinations `$2143..` PPU regs, mode 3/4 = scroll/colour/window tables built each frame), `$420C` = `$7F` (HDMA on for channels 0-6). `$0634/$0636` = per-player flag words, `$06F4 = $01E0`.

## Frame loop (`01:8272`)
```
wait: $0122 bit15 = 0              ; NMI (01:E2F2) copies $0122 -> $22 / frame sync (bit15 set = "frame consumed")
$1E++ ; $F8 = $1A - $F6 ; $F6 = $1A ; dt = frames since the last pass (1 normally, 2 when the game is slow)
01:83BF  pause / quit test (below); carry set -> leave the race
00:8A41  player car update (physics, 03-physics.md)
00:D726  walk the 20 car records (05-ai-cars.md)
08:8BCA  race_frame_b (HUD / sprites / objects)
08:CB74  road_render (scanline tables)
0B:8000  hdma_build
```
then: sound mailbox bits (`$0500..$0506`, `$0514`, see `08-sound.md`), the finish logic, `BRL 8272`.
* `dt` (`$F8`) multiplies every speed/accel/timer in the physics and AI code, so the game is frame-rate independent (a pass can cover several vblanks).
* **Pause/quit** (`01:83BF`): bit12 of `$0030` (Start edge) pauses: the loop at `83E3` waits a frame at a time (the screen shows PAUSED / PRESS L+R TO QUIT); `$0028 & $30 == $30` (L+R held) returns carry set = quit race (`jmp_01839D`: fade the screen out with `$58 -= $80` per frame, then leave). Another Start press unpauses.
* **Finish** (`$06F0` = number of local players that finished, `$06EE` = number of cars that have finished, 20 = all): once the player has finished, `$06F2` runs a countdown (`7ED4` + dt per frame); when the fade/countdown is done and **not all 20 cars have finished**, the loop at `01:836C` **fast-forwards the race**: `$F8 = $11`, `$1A += $11`, `JSL 00:D726` repeatedly until `$06EE >= 20` (AI cars are simulated at 17 ticks per call without rendering), so the standings (`7E:FE9E`, `7E:FEC6`) are complete for the results screen.
* **Exit** (`01:8388`): `$0076/$0078 = 7E:FF16/FF18` (return vector saved by the front-end), `$0596 = 0`, `SEI`, `JML [$0076]` -> `1F:809B` (`10-game-flow.md`).

## Variables seen here
`$0100` (=`$FFFF` while quitting), `$0122` frame sync, `$00F8` dt, `$00FC` (value `$F8`/`$08`/`$F7`: sound/master volume fade), `$0024/$0026` (race-start / countdown: `$26 >= $0600` and `$74` select the pre-race wait), `$7E:FF1A` (set = skip the pre-race, used when the front-end enters straight into a race), `$0A16/$0A32` (P1/P2 final place), `$0674` (player-in-race flag), `$0514` (non-zero = holds `$0122`).
