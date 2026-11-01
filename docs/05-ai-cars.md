# AI car records (7E:C400 + n*0x40) - first look
Observed with `scripts/carlog.lua` (records 1..4 sampled every 20 frames, player holding X from the green flag; USA Auckland).
Offsets in bytes (word index x2). Record 0 differs (list header: +0..0xE = pointers 0340,0380,...,04C0).
| off | meaning (hypothesis, checked on 4 cars) |
|---|---|
| +0x10 / +0x12 | own index n / next index (linked list 1->2->3...) |
| +0x14 | lateral position (signed, e.g. FFBC, FFCB, FFFC, 0066 = cars side by side) |
| +0x18..0x1A | 24-bit distance along the lap (low word, then high; hi word increments ~0x7 per 20 frames at start); a second copy at +0x30 is the previous-frame / delayed value |
| +0x1C | handler index: `JSR ($E417,X)` picks the per-record routine (table `00:E417`: E423=RTS, E541, E6C4, E6DE, E424, E754 ...) |
| +0x22 | speed/2: distance gained per frame = 2 x this (car 1: 0x2F72 -> 24292/frame) |
Cars advance at a nearly constant rate (24292, 24168, 24174, 22262 per frame for cars 1-4 = different top speeds per car) and slow at the end of the
sampled window (21863, 21751, 19791, 20036) - looks like per-segment speed limits or rubber-banding, not yet traced.
Handler `00:E424` (case 4): tests `$C41A,Y` (record's own position field) against `$06EC`/`$06EA` (player position) +/- `$010A` (lap length, wrap) within a window of 0x60 -> decides whether
the car is near the player (visible/collidable), else JMP `00:E4D0`.


## Handler `00:E541` read in full (per-frame update of one car; Y = record offset, fields = `$C400+Y+off`)
* Window test as in E424: car within 0x60 lines of the player (`$06EC`, or `$06EA` in 2P mode `$0102` bit7) -> set bit0 of flags `+0x2B` ("near"), else clear it (`E607`).
* **Lateral**: `+0x14 += lateral velocity (+0x28) * frame step ($F8)` using the hardware multiplier (`$1B`,`$1C` -> product `$34..$36`).
  The result is clamped between two per-line arrays indexed by the car's line (`+0x1A` x2): `7E:2000,X` (left limit) and `7E:3300,X` (right limit). Hitting a limit
  negates `+0x28` (bounce) - so `7E:2000/3300` are the road-edge tables.
* **Speed**: `+0x1F` (16-bit, fraction in `+0x1E`) approaches target `+0x24`; the step is looked up in the acceleration table `80:F093` indexed by (target-speed)>>8 &FE, times `$F8*2`.
* **Distance**: `+0x18/+0x1A` (24-bit lap position) `+= speed * $F8*2` - same units as the player's `$061C`.
So the earlier "+0x22 = speed/2" is the speed word `+0x1F..` seen shifted; the constant per-car rates are the targets in `+0x24`.
Handlers E424/E541/... are variants of this routine for different car behaviours (the index in `+0x1C`).
Next: find who writes target speed `+0x24` (race AI / rubber band) - watch `7EC424+n*40`.

## Car setup (`00:D1D4..D2CA`, once per race) - where the AI strength comes from
Loop over 20 grid slots (X = 0x26 down to 0, step 2; slot order from the permutation at `7E:FE9E`). For each car:
* start line `+0x1A = $E0` (counts down from lap length-1: cars start behind the line), lateral `+0x14 = $E2` (0x90, then -0x60 per car, wrapping), handler index `+0x1C = 8`;
  lateral velocity `+0x28` from the RNG (`01:E25B`) -> +/- (0x70 + rand&7F).
* **Target speed `+0x24 = -(($E6 & 3FF)) + 1 + table80:D684[slot] + $E8`**: `80:D684` = 14336 descending by 230 per grid slot (slot 0 fastest); `$E6` is random per race;
  `$E8 = table 80:D5FE[track] + table 80:D67E[$0120]`.
* `80:D5FE` (64 words, per track): -1280, -1184, ... rising to +4072 for the last tracks: **AI speed climbs with track number** (Australasia easiest).
  `80:D67E` = 0, 768, 1536: `$0120` is the **difficulty level** (so the "bit-field view" selector in the road builder is difficulty-dependent too - re-check that note).
* `+0x30 = rand&FF + table 80:D6D4[slot]`, `+0x32 = table 80:D6FC[slot]` (ramps 5529..32512 and 8601..15963; per-car aggression/lane-change timers?, unverified).
* Car-record writes seen at runtime: `+0x58/0x5A` (lap position, E680/E689), `+0x6C..6F` (copy by D857/D85D), nothing writes +0x24 after setup, so
  cars hold a fixed target speed; the earlier slowdown in my samples is the speed (`+0x1F`) tracking curve/slope limits in the handlers (not yet traced).

## Handler table `00:E417` (byte index = value at `+0x1C`, verified from the table bytes `23E4 41E5 C4E6 DEE6 24E4 54E7`)
| `+0x1C` | routine | role |
|---|---|---|
| 0 | `E423` | RTS - inactive slot |
| 2 | `E541` | full update (near-player window, lateral motion, speed, lap distance) |
| 4 | `E6C4` | **attached to player 1**: `+0x18/1A += $0212/$0214` (player's distance step), lateral `+0x14 = $0205` (car just follows the player) |
| 6 | `E6DE` | same for player 2 (`$024E/$0250`, `$0241`) |
| 8 | `E424` | **start / launch phase** (value stored by the setup `D1D4`): same window test as `E541`, then (`E4D9`) speed `+0x1F += +0x30 * $F8` (**+0x30 = launch acceleration**, `rand&FF + 80:D6D4[slot]`) until it reaches **+0x32** (`80:D6FC[slot]`), then `+0x1C` is set to 2 and the car runs `E541` for the rest of the race. Lap distance advances as in `E541` |
| 0x0A | `E754` | **post-finish coasting**: speed only (accel `80:F093`, decel `80:F193` indexed by the target-speed error high byte), no lateral motion |
Finish handling (`00:DE9B..`): `+0x22` is the car's lap counter; when it reaches `$019E` (total laps) the car's flag `+0x2B` bit1 is set and, if it is the player's car (`+0x10 == 0`), `sub_E6F8` / `E726` (P2) switch it to handler 0x0A with target speed `$4000` (`$3800` for P2),
bump the finished counter `$06F0`, set `$0634 bit15`, and store the rank (`$06EE`) for the results screen. The 12-word shift at `DE50..DE98` maintains the car order list `$C3E8..$C400` (race positions).
The AI speed approach: error = `+0x24 - +0x1F`; if positive speed += `F093[err>>8] * $F8 * 2` (clamped to the target), if negative the same with `F193` (so braking is stronger than accelerating).

## AI target speed formula (`00:D1BD..D293`, read; the speed target `+0x24` of each AI record)
`+0x24 = 80:D5FE[track]  +  80:D67E[difficulty ($0120)]  +  80:D684[grid slot]  -  (rand & 0x3FF)`  (signed words, same units as the player's speed word `$061D`)
* `80:D5FE` (64 signed words, one per track = `$0108`): -1280 -1184 -1104 -1024 | -576 -560 -416 -384 | 48 128 176 240 | 640 x4 | 1152 x4 | 1440 1472 1536 1568 | 1920 1968 2080 2176 | 2448 2464 2480 2496 | 2768 .. 2816 | 3104 .. 3152 | 3296 .. 3336 | 3472 .. 3496 | 3628 .. 3640 | 3772 .. 3784 | 3916 .. 3928 | 4060 .. 4072: **AI gets faster with every race of the championship** (country 0 slowest, last country +5350 above the first).
* `80:D67E` = 0, 768, 1536 for difficulty 0/1/2 (the `$0120` value of the three levels).
* `80:D684` (20 words, per grid slot): 14336 minus 230 per slot (slot 0 = fastest ... slot 19 = 9966): the starting grid is also the strength order.
* The random part is drawn once per car at race start (`rng` at `01:E25B`), so every race the field is slightly different: up to 1023 slower.
Together with the acceleration steps from `80:F093` and the launch fields (`+0x30/+0x32`), this is the whole AI strength model found so far; there is **no per-lap rubber banding in this setup code** (handler `E541` only moves the speed towards `+0x24`).
Check (`scripts/` ad-hoc Lua, Auckland = track 0, difficulty 0, frame 3050): `+0x24` of records 1..19 = 12396, 11963, 11706, ... down to 7935 for the last grid slot, all inside `D684[slot] - 1280 - [0,1023]` (slot 0: 12033..13056; slot 19: 7663..8686). Records are in grid order `X = 0x26 .. 0`, and record 0 (id 0 = the player's car) also gets a target (12345) that the race does not use for the player.
