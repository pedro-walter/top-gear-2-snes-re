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
Next: trace E541/E6C4/E6DE/E754 and find what changes +0x22.
