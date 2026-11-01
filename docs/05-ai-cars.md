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
