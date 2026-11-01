# Modding index (USA ROM): where to change what

File offset = `bank*0x8000 + addr - 0x8000`. EUR/JPN differ by small shifts (`tools/portsyms.py`, `docs/07-versions.md`). Data only; patch with IPS of your own bytes.

| what | bank:addr | file offset | notes |
|---|---|---|---|
| Shop prices (x $1000), 10 rows x 4 words (level 0..3): k0 Engine 0,30,50,80; Wet 0,1,2,3; Dry 0,1,2,4; Gearbox 0,10,30,50; Nitro 0,5,15,30; k5 0,1,2,3; armors 0,5,10,20 x3; paint 0 | 1F:AC6F | 0xFAC6F | verified on the shop screens (Engine, Wet, Dry, Gearbox, Nitro) |
| Shop price **strings** (ASCII, NUL-separated, what the shop draws; rows in the same order: 30000 50000 80000 / 1000 2000 3000 / 1000 2000 4000 / 10000 30000 50000 / 5000 15000 30000 / ...) | 1F:B1C4 | 0xFB1C4 | must be patched together with the words above (the buy routine `1F:AB9E` uses the words, `1F:AB43` draws the strings); keep each string's length |
| Prize money per finishing place (x $1000): 10,6,4,3,2,1,0... | 1F:EF46 | 0xFEF46 | read at 1F:ED28 |
| Championship points per place: 10,6,4,3,2,1,0... | 1F:E35D | 0xFE35D | read at 1F:ED13 |
| Driver names (20, NUL-terminated ASCII) + pointer table | 1F:EFA7 | 0xFEFA7 | ASCII, result-screen text |
| Password XOR key table | 1F:D7F9 | 0xFD7F9 | docs/06-password.md |
| Engine acceleration curves (4 engines x 256 words) | 00:BE33 | 0x03E33 | offsets from 00:BE2B = 0,0x200,0x400,0x600 |
| Gear-ratio bytes (rows start at 00:BDF3 offsets 0,5,11,17) | 00:BDFB | 0x03DFB | docs/03-physics.md |
| Drag table (high speed) | 00:CA33 | 0x04A33 | index (speed>>5 - 0xE0) |
| Drag by speed | 00:C833 | 0x04833 |  |
| Engine power index per level (40,44,48,52, 104..116) | 00:D036 | 0x05036 | -> $0698 (sound volume) |
| Armor tables 24,16,12,8,4 / 32,28,16,12,8 | 00:D03E | 0x0503E |  |
| Per-car physics constants (7 tables x 5 cars) | 00:D048 | 0x05048 | stride 10 |
| K5 table 236,240,244,248 | 00:D08E | 0x0508E | speed scale `$068E` |
| Tyre grip by weather class x level | 00:D0A2 | 0x050A2 |  |
| Nitro tables | 00:D0C2 | 0x050C2 |  |
| Number of gears per gearbox level: 5,6,6,7 | 00:D0D2 | 0x050D2 |  |
| Track table, 8 bytes x 64 (seg ptr, seg count => laps = 64/count + 1, +6 weather/class) | 0A:8000 | 0x50000 | docs/04-tracks.md |
| AI launch acceleration / launch-exit speed per grid slot | 00:D6D4 | 0x056D4 | D6FC for the exit speed (docs/05-ai-cars.md) |
| AI target speed: per track (64 words) / per difficulty (0,768,1536) / per grid slot (20 words, 14336 - 230*slot) | 00:D5FE / D67E / D684 | 0x55FE / 0x567E / 0x5684 | docs/05-ai-cars.md |
| AI speed-step acceleration table | 00:F093 | 0x07093 | docs/05-ai-cars.md |
| Roadside descriptor rows (8 words x scenery set) | 09:B1EB | 0x4B1EB | docs/04-tracks.md |
| SPC700 driver (compressed) | 1A:8000 | 0xD0000 | BF14 stream, 3244 bytes decompressed |

Not found yet / not data-driven: number of cars (20, hard-coded loops `X = 0x26..0` in `00:D1D4`), starting money (`$1CE1*10` after a password, `1F:CFF4`), the lap count formula (`00:CEB3`, from the track table), the 16 countries x 4 tracks structure (`$1CE5` bit2 test at `1F:ED4C`).

Patch workflow (phase 3): `tools/asm65816.py` for code, `tools/make_ips.py` for the IPS; for quick experiments poke ROM at run time with `emu.write(file_offset, v, emu.memType.snesPrgRom)` (see `scripts/objid.lua`).

**Pipeline tested** (`patches/cheap_shop.txt`): `python3 -I tools/patch.py "roms/Top Gear 2 (USA).sfc" patches/cheap_shop.txt out/cheap.sfc out/cheap.ips` writes the ROM and an IPS of only the changed bytes; `TG_ROM=$PWD/out/cheap.sfc python3 -I tools/run.py ...` boots the patched ROM headless (engine prices show $10000/$20000/$30000 in the shop). Patch files use `BB:AAAA hex...`, `word BB:AAAA v1 v2...` or `@0xFILEOFF hex...` lines.

## Same tables in Europe and Japan (found by byte-pattern search; contents identical)
| table | USA | EUR | JPN |
|---|---|---|---|
| price words (x $1000) | 1F:AC6F | 1F:ACB5 | 1F:ACB5 |
| price strings | 1F:B1C4 | 1F:B207 | 1F:B20A |
| points per place | 1F:E35D | 1F:E3CC | 1F:E63B |
| prize per place (x $1000) | 1F:EF46 | 1F:F5F3 | 1F:F862 |
| driver names | 1F:EFA7 | 1F:F654 | 1F:F8C3 |
| engine curves | 00:BE33 | 00:BEBC | 00:BEBC |
| gear ratio / accel bytes | 00:BDFB / 00:BE13 | 00:BE84 / 00:BE9C | 00:BE84 / 00:BE9C |
| drag (high speed) | 00:CA33 | 00:CABC | 00:CABC |
| button masks (control types) | 00:D048 | 00:D0D1 | 00:D0D1 |
| `D036` car-setup tables | 00:D036 | 00:D0BF | 00:D0BF |
| track table | 0A:8000 | 0A:8000 | 0A:8000 |
(Bank 00 tables sit `+0x89` later in EUR/JPN: the code before them is 137 bytes longer; bank 0A is unchanged.)
