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
