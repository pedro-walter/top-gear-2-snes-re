# Tracks, countries and how to reach them

## Reaching any track (headless)
Title menu rows: 1P GAME / START / CONTINUE COUNTRY / OPTIONS / CONTINUE GAME. **CONTINUE COUNTRY** (2 x down, A) shows the
country list (Australasia, Britain, Canada, Egypt, France, Germany, Greece, India, Ireland, Italy, ... 16 countries).
Picking a locked country asks for a password. The check is at `1F:C9CD`: `CMP $1CE3` - `$1CE3` is the highest unlocked
country index; larger -> password screen.  **Poke `$1CE3` (WRAM) = 9 (or 15) and every country is selectable**
(`scripts/unlock.lua`, env `TG_UNLOCK`).  Then A (country) -> A (mode menu RACE) -> A (track info) -> A (car shop) -> Start.
Cursor down presses 1000+15k (k = country index) with `:4` frame length; A at 1250; A 1500/1700/1900; Start 2150 -> green flag ~3000.
All 10 tried countries (0-9) start a race; 4 tracks per country, the 4 sub-tracks are the career steps (this screen picks sub 0 first).

## Variables
| addr | meaning |
|---|---|
| `$01A5` | country cursor (country-select screen) |
| `$7EFE0A` / `$7EFE0E` | country / sub-track chosen (career state block `7E:FE00..`) |
| `$0108` | **track number** = `4*country + sub` (`00:CD31-CD38`) - index of the track table |
| `$1CE3` | highest unlocked country |

## Track table: bank 0A:8000, 8 bytes x 64 tracks (16 countries x 4)
Read as `LDA $8A8006,X` / `$8A8002,X` with `X = $0108*8` (`00:CE68`, `00:CEB3`).
| off | meaning |
|---|---|
| +0 | word ptr (bank 0A) to the segment list |
| +2 | byte N = segment count (word at +2 is the divisor source for `$4206` at `00:CEC0`) |
| +6 | `&7` selects a per-track parameter (via `80:D092`/`7E:FE2E`/`FE57`, `80:D0A2` -> `$0694`, `$06B6`); `ff` in +7 on 11 tracks |
Segment list: N+1 records of 4 bytes, the last repeats the first (closed loop); `rec[3]` = segment length (sum over a lap: 30..262).
Record bytes look like `b6 04 35 08`, `c0 00 00 05`, `80 00 00 06`: byte0 high bits = curve/shape class (`80`,`c0`,`00` common, others are curves),
byte1 = hill/side flags, byte2 = scenery/object id, byte3 = length. Meaning not decoded yet.
`python3 -I tools/trackdump.py ROM [track...]` prints them (entries 64+ in the dump are not tracks, they are segment data).

## Per-country resources (decompressor log, countries 0-9)
Each country loads a small set of streams chosen from tables (all through variant B, all in the menu phase, nothing during the race):
| source | out | dest | content (guess) |
|---|---|---|---|
| `09:DAB5..DCF7` (one per country, ascending) | 8-19 B | WRAM `7E:6200` | small control block |
| `09:B5AB..C6C8` | 0-288 B | `7E:6400` | small control block |
| `0A:9A14..F3D5` / `0A:9A41..F41E` | 28-400 B | `7E:5800` / `7E:5D00` | pairs of small tables (HDMA/colour gradients?) |
| `0D:C572 CDCE D712 DFF4` | 8960 | VRAM | background tile set (shared by several countries) |
| `0E:B393 C3BB D40F` | 8192 | VRAM | tilemap/background |
| `03:8000 04:8000 04:C134 05:8000` | 26-31 KB | VRAM/WRAM `$0000` | big background image set, shared by country groups |
| `07:*` (C720 C4B6 F792 ...) | 2-4.5 KB | | map/tables |
| `12:*` `13:*` `14:*` `15:D882` | 0.4-10 KB | VRAM word addrs `12E0 2CC0 4860 ...` | roadside/scenery sprite & tile graphics |
The 64 KB stream `07:8006` is loaded for every country (common). Nothing is decompressed after the race starts, so per-track data
(segment lists, 0A tables) is read directly from ROM or copied by `MVN` during menu loading (`01:8EBA` copies `0C:8000-85FC` to `7E:8000`, shared by all countries).

## Tools
`scripts/unlock.lua` (poke `$1CE3`), `scripts/mvnlog.lua` (logs every MVN/MVP: frame pc A X Y dst src), `tools/tilesheet.py` (`sheet(bytes, png)` 4bpp grey tile sheet).

## Road builder `08:801C` (first look)
Runs once per race (and the minimap code `08:9B75` reads the same records in the track-info screen). With `X = $0108*8`:
* `$010A = N << 6` (segment count x 64, from `0A:8002`), `$3E = $24 = ptr` (`0A:8000`).
* Loop per segment: `$40/$42` = the segment record (words at `0A:ptr`, `ptr+2`); `X = (ptr-$24)>>2` = segment index.
* `7E:6200,X` (byte per segment) is the stream `09:DAB5..` - e.g. 13 bytes for Auckland's 13 segments, so these 09:Dxxx streams are **per-segment attribute bytes**; `$22` takes it.
* The record is bit-packed indices into lookup tables in bank 09: `$42 & $3F00` -> `09:8000`, `$42 & $FC` -> `09:8800` (words), `($41&$3F0)` -> `09:8C40`, `$40 & $FC0` -> `09:90C0` (+3 = run length `$44`);
  `$40 & $3F` x16 -> `$46`. Results are written to the 16-byte-per-line table at `7E:9000,Y` / `7E:9200,Y` (Y = (0x20 - $3A) x 16, two copies),
  which is the segment table the player update (`00:8A41`) walks with `sub_009BFD`.
* `$0120` (0/1/2) chooses which of three bit-fields of the word stream at `09:0000+X` is used (mode set at `00:CD2A`).
Next: decode the bank-09 tables (curve/slope profiles) and the record bitfields.

## Segment record decode (verified statistically)
32-bit record = `$40` (bytes 0-1), `$42` (bytes 2-3). Correction: **byte3 is not a length**.
| field | bits | table (bank 09) | meaning |
|---|---|---|---|
| curve | rec[3] & 3F | `09:8000` (64 x 16 words, 32 B each) | per-line curvature profile for a 16-line chunk. 1..33 used; odd = right, even = left (sign flips), 0 = straight. Ramp up / plateau / ramp down shape (e.g. idx 1: 80,160 x13,80) |
| hill | (rec[2]>>2) & 3F | `09:8800` | per-line slope profile (idx 1..33 hills, e.g. 13 = bump 0,240,720,0,-240) |
| 3rd | ($41 & 3F0)>>4 | `09:8C40` | 16 equal words, values `0x8xxx` (-32416, -32000 ...) - probably a ground/palette/tile selector, not yet identified |
| stream | rec[0] bits 6-11 | `09:90C0` word ptr -> stream in `09:xxxx` | run-length / object stream, 10-bit words with 3-bit flag `$0380` (see loop `08:80C4`) |
| low | rec[0] & 3F | | x16 -> `$46`, used as offset into `09:B1EB` (side-object table, bit15 = "turn marker") |
Check: summing the curve-profile sums over a lap's records gives about +/-35000..60000 for most tracks (same magnitude = one full
loop of heading), with all indices <= 33 across all 64 tracks. So the track is: N records x 64 lines, curvature/hill integrated per line.
Not yet: how the stream loop at `08:80C4` places objects and sets segment length ($3A/$3C counters).

`tools/trackmap.py ROM K REPS` integrates the curve profiles (REPS=4 chunks of 16 lines per record). With K~3000 per-lap heading
comes out at 0.7-1.3 turns for most tracks (e.g. 0.78, 1.01, 0.89), i.e. one loop, but endpoint closure is only rough (0.03-0.4 of length):
the real game curvature->heading mapping is not linear (and the hill/stream parts are ignored), so treat the maps as approximate.
