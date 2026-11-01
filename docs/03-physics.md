# Player car update (00:8A41) - first pass

`00:8A41` runs once per race frame with **DP = $0600**: the player car's state page. (Earlier I called it road-scroll maths; it is the car physics and movement.)
Found by watching writes: use the *bank 00* address for WRAM below $2000 (`00061C`, not `7E061C`); a `7E` watch never fires for low RAM.

* Speed: 24-bit at `$061C-$061E` (so DP `$1C/$1D/$1E`). The word at `$061D` is `~0x1784` at 83 mph. `$0610 = speed/4` (made at `00:D836` from the multiplier result), `$01A4` = HUD mph.
* Per frame: `speed += accel(gear, speed) * dt - drag(speed) * dt`, `dt = $00F8`. Every product goes through the PPU signed multiplier (`$211B` twice, `$211C`, read `$2134-36`).
  Tables: `80:BE2B/BE33` (accel by gear `$8C` and speed>>5), `80:C633` (accel when no gear/automatic), `80:CA33` (high speed), `80:C833` (drag, indexed by speed>>2).
* Position along the track: `$14/$16 += speed*dt*8` (`00:9179`), lateral/segment indices `$D6/$D8`, then looks up the track segment table at `7E:9006` (`sub_009BFD` per segment crossed).
* Timers `$2C/$64/$6C` count down by dt (boost/collision recovery); `$34` is a flag word (bit0 set at 8F4F, bit1 = alternate speed in `$24`).
* The 20 car records at `7E:C400` are the AI/other cars; the player is separate (page `$0600`).
Open: what `$34` bits mean, the `$D4/$D5/$88` parameters per car model (car-shop upgrades should change them), and the steering/collision code after `00:9260`.

## Acceleration curves and gear table (decoded from ROM)

* `$8C` is the **engine level (0..3)**. `80:BE2B[$8C*2]` = byte offset (0, 0x200, 0x400, 0x600) of that engine's curve in `80:BE33`: 256 words, indexed by `((speedhi + $BC) >> 5) & ~1` (`$1D` = speed high word, `$BC` = a bias; index must be < 0x200 else the curve is skipped and only drag applies).
* Curve values fall with speed: engine 0 starts at 23944 and reaches 0 at the top (index ~0xF0), engine 3 starts at 27448 and holds ~16.6k through the mid range before collapsing near the top. Higher engine = higher start and a later collapse (more top speed). Sample (every 8th entry): E0 `23944 21900 20732 ... 12556 ... 0`, E3 `27448 26280 ... 16644 ... 0`.
* The picked value is multiplied by `$D5` (per-car acceleration constant), then by `dt` (`$00F8`, doubled while `$64` or `$2C` is non-zero = boost/recovery), and added to speed (`$1C/$1D`, or `$24` when `$34` bit1 is set).
* Above index 0xE0 the drag table `80:CA33` (starts 0, then -146.. descending) is added, giving the speed limit.
* `80:BDF3` = `{0,5,11,17}`: byte offset per **gearbox level** (`$8A`) into the gear-ratio byte table `80:BDFB`. Each row begins with `0xE0` (neutral/launch) followed by the gear ratios:
  * gearbox 0: 64 77 90 103 (4 gears)
  * gearbox 1: 64 75 86 97 111 (5)
  * gearbox 2: 64 77 91 104 118 (5)
  * gearbox 3: 64 77 89 102 114 127 (6)
  This matches `$06C0` going 5 -> 7 (rows include the 0xE0 entry, and `$06C0` = gears+1 for level 0..3: 5,6,6,7).
  `$30` = current gear index; the ratio is used as the 8-bit multiplier operand against speed (`$1D/$1E`) at `00:8CAE` etc.
