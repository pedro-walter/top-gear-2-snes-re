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

## `$0120` = difficulty (verified)
`$0120` is loaded from `7E:FE06` by `00:CD09` (a game-setup copy: `FE04`->`$0102` mode, `FE3E`/`FE67`->`$0104/$0106` chosen cars, `FE0A*4+FE0E` -> `$0108`).
Poking `7EFE06` = 2 vs 0 before the race raises the AI cars' speed field (0x2FE6 -> 0x3435 for car 1) - same as the D67E table in `docs/05-ai-cars.md`.
So the road builder's 3 views of the `09:xxxx` word stream (10-bit fields at bits 0-9 / 2-11 / 4-13) are **per-difficulty** versions of the same object/traffic stream.
`7EFF1A` != 0 selects special modes (override of `$0102`, `$0108` from `80:F2D7/F2DD`, difficulty forced 0) - probably championship/challenge races.

## Roadside object stream (`08:80C4..`, partly verified by decoding the data)
* Source: `09:0000 + X`, X = `$44` starting at `09:90C0[(rec0>>6)&3F] + 3`, advancing **4 bytes per entry**. Each 32-bit entry packs **three 10-bit codes, one per difficulty** (bits 0-9 / 10-19 / 20-29, read as unaligned words at X, X+1, X+2 and masked; `$0120` picks which).
* Code `v` (10 bits): `v>>7 & 7` = category, low 7 bits = parameter.
  * category 0: **gap**: `$48 = v`, i.e. skip that many road lines (output 0) - `0:4` = four empty lines.
  * category 1..7: an object on this line. `$4A = v`; the category (x2) indexes `88:EABB` (1,2,4,...,128 bit mask) which is ANDed with `$22` (a per-line byte from `$6200`, derived from `$3E-$24`): if the bit is set the object is suppressed (a distance/LOD or visibility mask).
    Otherwise the descriptor = `09:B1EB[(rec0&3F)*16 + category*2]` (one 8-word row per "scenery set" = `rec[0]&3F`).
    * positive descriptor: low 8 bits = object/tile id, upper bits from `$49`; stored in the line word at `$9006,Y` / `$9206,Y`.
    * negative descriptor: bit14 set -> no object; else a **multi-line object**: the line index `$30` is pushed on a ring buffer at `$9800` (`$2E`, wraps at 0x200), `$6400+$30 |= 0x40`, and `$30` advances by `desc & 0x3FFF` (resets to 0 when equal to `$00`).
* Typical Auckland data: segment 1 = `0:4, 2:88` repeating (a category-2 object every 5 lines, e.g. roadside posts), segment 2 = `1:40, 0:4` repeating. Difficulty views were identical in these samples, they differ on other tracks.
* Descriptor rows (`09:B1EB`): row 0 = `0000 002C 0030 0008 004E 004F 8002 0049`, row 4 = `0000 004B x6 0000` (all-same fence/wall object).
* Still open: the meaning of the 3rd-field table `09:8C40` and what `$3A/$3C` (line within segment / segment length) do exactly; what id values 0x2C, 0x4B... draw (sprite or BG tile).

### Object id experiment (ROM poke)
`scripts/objid.lua` (env `TG_ID`, `TG_CAT`, `TG_NSETS`) overwrites the descriptor of one category in the first scenery sets of `09:B1EB` at frame 1 (`emu.write(file_offset, v, emu.memType.snesPrgRom)` really changes what the CPU reads; file offset of `09:B1EB` = `0x4B1EB`). Rewriting more than ~8 rows (`TG_NSETS=64`) blacks out the game (rows beyond the used ones overlap other data), 8 is safe. Result on Auckland (category 2 in the start segment): id `0x10` draws nothing, `0x2C` and `0x4B` draw a **tyre stack** at the left roadside (seen close to the car at frame 3250 only: at the start line all objects are too small to distinguish). To catalogue ids, take the screenshots later in a lap or place the car with `$14/$16` (position) before shooting.

## All 64 tracks (from `0A:8000`, USA)

| track | country | race | segments | laps | class (+6 &7) | +6 | +7 |
|---|---|---|---|---|---|---|---|
| 0 | Australasia | 1 | 13 | 5 | 2 | 02 | 00 |
| 1 | Australasia | 2 | 13 | 5 | 2 | 02 | 00 |
| 2 | Australasia | 3 | 17 | 4 | 6 | 06 | 00 |
| 3 | Australasia | 4 | 37 | 2 | 3 | 03 | FF |
| 4 | Britain | 1 | 19 | 4 | 5 | 05 | 00 |
| 5 | Britain | 2 | 20 | 4 | 2 | 02 | 00 |
| 6 | Britain | 3 | 32 | 3 | 2 | 02 | 00 |
| 7 | Britain | 4 | 25 | 3 | 2 | 02 | 00 |
| 8 | Canada | 1 | 16 | 5 | 2 | 02 | 00 |
| 9 | Canada | 2 | 31 | 3 | 3 | 03 | FF |
| 10 | Canada | 3 | 33 | 2 | 2 | 02 | 00 |
| 11 | Canada | 4 | 31 | 3 | 6 | 06 | FF |
| 12 | Egypt | 1 | 8 | 9 | 2 | 02 | 00 |
| 13 | Egypt | 2 | 10 | 7 | 2 | 02 | 00 |
| 14 | Egypt | 3 | 13 | 5 | 6 | 06 | 00 |
| 15 | Egypt | 4 | 19 | 4 | 2 | 02 | 00 |
| 16 | France | 1 | 13 | 5 | 2 | 02 | 00 |
| 17 | France | 2 | 22 | 3 | 6 | 06 | 00 |
| 18 | France | 3 | 27 | 3 | 2 | 02 | 00 |
| 19 | France | 4 | 30 | 3 | 3 | 03 | FF |
| 20 | Germany | 1 | 14 | 5 | 3 | 03 | FF |
| 21 | Germany | 2 | 23 | 3 | 2 | 02 | 00 |
| 22 | Germany | 3 | 19 | 4 | 5 | 05 | 00 |
| 23 | Germany | 4 | 32 | 3 | 4 | 04 | 00 |
| 24 | Greece | 1 | 12 | 6 | 6 | 06 | FF |
| 25 | Greece | 2 | 29 | 3 | 2 | 02 | 00 |
| 26 | Greece | 3 | 30 | 3 | 2 | 02 | 00 |
| 27 | Greece | 4 | 29 | 3 | 2 | 02 | 00 |
| 28 | India | 1 | 10 | 7 | 2 | 02 | 00 |
| 29 | India | 2 | 16 | 5 | 2 | 02 | 00 |
| 30 | India | 3 | 24 | 3 | 2 | 02 | 00 |
| 31 | India | 4 | 28 | 3 | 2 | 02 | 00 |
| 32 | Ireland | 1 | 18 | 4 | 2 | 02 | 00 |
| 33 | Ireland | 2 | 15 | 5 | 2 | 02 | 00 |
| 34 | Ireland | 3 | 21 | 4 | 3 | 03 | FF |
| 35 | Ireland | 4 | 21 | 4 | 2 | 02 | 00 |
| 36 | Italy | 1 | 19 | 4 | 2 | 02 | 00 |
| 37 | Italy | 2 | 27 | 3 | 2 | 02 | 00 |
| 38 | Italy | 3 | 29 | 3 | 6 | 06 | 00 |
| 39 | Italy | 4 | 27 | 3 | 2 | 02 | 00 |
| 40 | Japan | 1 | 22 | 3 | 2 | 02 | 00 |
| 41 | Japan | 2 | 33 | 2 | 6 | 06 | FF |
| 42 | Japan | 3 | 35 | 2 | 2 | 02 | 00 |
| 43 | Japan | 4 | 30 | 3 | 2 | 02 | 00 |
| 44 | Scandinavia | 1 | 17 | 4 | 2 | 02 | 00 |
| 45 | Scandinavia | 2 | 20 | 4 | 4 | 04 | 00 |
| 46 | Scandinavia | 3 | 24 | 3 | 4 | 04 | 00 |
| 47 | Scandinavia | 4 | 24 | 3 | 5 | 05 | 00 |
| 48 | SouthAmerica | 1 | 19 | 4 | 2 | 02 | 00 |
| 49 | SouthAmerica | 2 | 27 | 3 | 2 | 02 | 00 |
| 50 | SouthAmerica | 3 | 33 | 2 | 2 | 02 | 00 |
| 51 | SouthAmerica | 4 | 29 | 3 | 6 | 06 | 00 |
| 52 | Spain | 1 | 10 | 7 | 2 | 02 | 00 |
| 53 | Spain | 2 | 14 | 5 | 6 | 06 | FF |
| 54 | Spain | 3 | 28 | 3 | 3 | 03 | FF |
| 55 | Spain | 4 | 25 | 3 | 2 | 02 | 00 |
| 56 | Switzerland | 1 | 19 | 4 | 2 | 02 | 00 |
| 57 | Switzerland | 2 | 21 | 4 | 2 | 02 | 00 |
| 58 | Switzerland | 3 | 26 | 3 | 6 | 06 | 00 |
| 59 | Switzerland | 4 | 34 | 2 | 4 | 04 | 00 |
| 60 | UnitedStates | 1 | 26 | 3 | 6 | 06 | 00 |
| 61 | UnitedStates | 2 | 25 | 3 | 2 | 02 | 00 |
| 62 | UnitedStates | 3 | 35 | 2 | 4 | 04 | 00 |
| 63 | UnitedStates | 4 | 29 | 3 | 5 | 05 | 00 |

Country order (`1F:DB32`, `$1CE1` / `$0108>>2`): Australasia, Britain, Canada, Egypt, France, Germany, Greece, India, Ireland, Italy, Japan, Scandinavia, South America, Spain, Switzerland, United States (16 x 4 races). Race 3 of Australasia is a night race (class 6), race 4 has 37 segments and 2 laps (class 3 = wet tyres). `+7 = FF` marks the final race of a country on the first tracks (meaning unverified). The class byte probably also picks the sky/palette set (class 2 = Auckland day and Ayers Rock sunset, 6 = night): not decoded.
