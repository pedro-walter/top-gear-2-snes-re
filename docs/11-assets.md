# Decompression calls seen at run time (menu -> shop -> several races)

Produced by `scripts/declog.lua` (exec hooks on `1F:BF14`, `01:DC53`, `01:DE85`, logging A/X/Y and the return address) + `tools/declogdump.py ROM out/declog.txt out/dec` (decompresses each unique stream, writes `.bin` and a 4bpp sheet `.png`).
Columns: source `bank:addr`, decompressor, caller (return address; a `9Fxxxx` caller is the front-end, `00xxxx` race loader), A (low byte = bank, bit 8 = destination 7E/7F... i.e. `7F9x` = WRAM `7F`, `7E89` = `7E`), Y = destination offset, compressed -> output bytes.
All of them decompress without error with `tools/bf14.py` / `tools/tg2decomp.py` (variant a = `DC53`, b = `DE85`), which also checks both ports on streams the static scan could not see.
Observations:
* Race loader callers: `00:8810/8826/8884/88A1` (track-dependent scenery/backgrounds in banks 0C-0E, 08), `00:D273..D33E` (car/sprite graphics in 07, 0D), `00:D4AC/D4EF/D53C` (the big 03/04/07 blocks: 30-31 KB each, **03:8000 = USA track set 1, 04:8000 = set 2**; `07:8006` = 64 KB blob; `07:9D2C`), `00:D8F6/D90F/D930/8861` (small per-track tables to `7E:8900-8A00`), `00:D9AE` = the **opponent car sprite sets**, one call per car type into `7F:xxxx` with banks 11-15 and destinations `Y` = `$12E0, $2080, $2CC0, $3C60, $4860, $65A0 ...`.
* Front-end callers: `1F:913E` / `1F:90F5` (menu/shop graphics, banks 18-1E), `1F:F07D/F0D7/F0FD` (sound driver and song sets, banks 1A-1B), `1F:B2F1/B317/B36A/B3D9/B3F4` (the title/mode-select blocks: `03:8000`, `04:8000`, `07:9D2C`, `07:8006`, `1E:ED01`, `00:8800`), `1F:EC12` (results screen, `18:AA55`).
* **`1F:BF14` and `01:DE85` implement the same format (variant B)**: the same stream (`03:8000`, `04:8000`, `07:8006`, `07:9D2C`) decompressed with `tools/bf14.py` and with `tools/tg2decomp.py` variant b gives byte-identical output. The front-end has its own copy of the routine (bank 1F cannot call bank 01's WRAM-DMA path), the race uses `01:DE85`. So `tools/bf14.py` == `tg2decomp.py` 'b'; only `01:DC53` (variant A, one caller `1F:F81F`) is a different format.

| source | decomp | caller | dest A / Y | comp -> out |
|---|---|---|---|---|
| 1A:8000 | BF14 | 9FF07D | A=7F9A Y=0000 | 2598 -> 3244 |
| 18:801C | BF14 | 9F913E | A=7F98 Y=0000 | 4686 -> 14336 |
| 1E:EDC0 | BF14 | 9F913E | A=7F9E Y=0000 | 2414 -> 8192 |
| 1D:AAFB | BF14 | 9FC3AE | A=7F9D Y=0000 | 901 -> 7172 |
| 1B:81A4 | BF14 | 9FF0D7 | A=7F9B Y=0000 | 328 -> 1038 |
| 1B:8544 | BF14 | 9FF0FD | A=7F9B Y=0000 | 2036 -> 7780 |
| 1C:85E9 | BF14 | 9F90F5 | A=7F9C Y=0000 | 3727 -> 6016 |
| 1C:8158 | BF14 | 9F90F5 | A=7F9C Y=0000 | 138 -> 896 |
| 1C:9796 | BF14 | 9F90F5 | A=7F9C Y=0000 | 129 -> 384 |
| 1C:9817 | BF14 | 9F90F5 | A=7F9C Y=0000 | 38 -> 112 |
| 1C:983D | BF14 | 9FA2B6 | A=7F9C Y=0000 | 140 -> 3840 |
| 1C:9478 | BF14 | 9F90F5 | A=7F9C Y=8000 | 165 -> 896 |
| 1F:BDE7 | BF14 | 9F913E | A=7F9F Y=0000 | 301 -> 768 |
| 1C:A1B0 | BF14 | 9F913E | A=7F9C Y=0000 | 2080 -> 2880 |
| 1D:95F7 | BF14 | 9F913E | A=7F9D Y=0000 | 4738 -> 10784 |
| 03:8000 | BF14 | 9FB2F1 | A=7F83 Y=0000 | 18488 -> 30144 |
| 07:9D2C | BF14 | 9FB317 | A=7F87 Y=0000 | 2343 -> 3072 |
| 07:8006 | BF14 | 9FB36A | A=7F87 Y=0000 | 7461 -> 65536 |
| 1E:ED01 | BF14 | 9FB3D9 | A=7F9E Y=0700 | 191 -> 1792 |
| 00:8800 | BF14 | 9FB3F4 | A=7F80 Y=0700 | 568 -> 2350 |
| 1C:98C9 | BF14 | 9F9119 | A=7F9C Y=0000 | 2279 -> 5600 |
| 1E:EA8F | BF14 | 9FA702 | A=7F9E Y=0380 | 348 -> 760 |
| 1E:D129 | BF14 | 9FA713 | A=7F9E Y=0780 | 6502 -> 20928 |
| 18:B2AB | BF14 | 9FF0D7 | A=7F98 Y=0000 | 2076 -> 10342 |
| 19:8000 | BF14 | 9FF0FD | A=7F99 Y=0000 | 529 -> 1038 |
| 0E:B393 | DE85 | 008810 | A=7F8E Y=0000 | 4136 -> 8192 |
| 0C:F787 | DE85 | 008826 | A=7F8C Y=0000 | 1741 -> 4576 |
| 03:8000 | DE85 | 00D4AC | A=7F83 Y=0000 | 18488 -> 30144 |
| 07:8006 | DE85 | 00D4EF | A=7F87 Y=0000 | 7461 -> 65536 |
| 07:9D2C | DE85 | 00D53C | A=7F87 Y=0000 | 2343 -> 3072 |
| 09:DAB5 | DE85 | 008861 | A=7E89 Y=6200 | 8 -> 13 |
| 0D:C572 | DE85 | 008884 | A=7F8D Y=0000 | 2139 -> 8960 |
| 08:EAEB | DE85 | 0088A1 | A=7F88 Y=0000 | 4776 -> 23760 |
| 0D:B848 | DE85 | 00D328 | A=7F8D Y=0000 | 1331 -> 12160 |
| 0D:B560 | DE85 | 00D33E | A=7F8D Y=0000 | 743 -> 3072 |
| 07:C720 | DE85 | 00D2D8 | A=7F87 Y=0000 | 1881 -> 4544 |
| 07:C4B6 | DE85 | 00D2EE | A=7F87 Y=0000 | 617 -> 2048 |
| 09:B5AB | DE85 | 00D8F6 | A=7E89 Y=6400 | 41 -> 96 |
| 0A:9A14 | DE85 | 00D90F | A=7E8A Y=5800 | 45 -> 44 |
| 0A:9A41 | DE85 | 00D930 | A=7E8A Y=5D00 | 48 -> 52 |
| 15:D882 | DE85 | 00D9AE | A=7F95 Y=0000 | 382 -> 4832 |
| 12:9C20 | DE85 | 00D9AE | A=7F92 Y=12E0 | 772 -> 3488 |
| 14:BE18 | DE85 | 00D9AE | A=7F94 Y=2080 | 607 -> 3136 |
| 13:B4F6 | DE85 | 00D9AE | A=7F93 Y=2CC0 | 1443 -> 4000 |
| 14:C078 | DE85 | 00D9AE | A=7F94 Y=3C60 | 1283 -> 3072 |
| 14:8000 | DE85 | 00D9AE | A=7F94 Y=4860 | 4489 -> 7488 |
| 12:85F4 | DE85 | 00D9AE | A=7F92 Y=65A0 | 1071 -> 4352 |
| 18:952F | BF14 | 9F913E | A=7F98 Y=0000 | 5414 -> 17600 |
| 18:AA55 | BF14 | 9FEC12 | A=7F98 Y=0000 | 914 -> 7168 |
| 1C:F2CD | BF14 | 9F913E | A=7F9C Y=0000 | 1640 -> 3168 |
| 1D:B343 | BF14 | 9F913E | A=7F9D Y=0000 | 240 -> 4096 |
| 1A:8B1E | BF14 | 9FF0D7 | A=7F9A Y=0000 | 1651 -> 4473 |
| 1B:82EC | BF14 | 9FF0FD | A=7F9B Y=0000 | 532 -> 1038 |
| 09:DABD | DE85 | 008861 | A=7E89 Y=6200 | 14 -> 13 |
| 09:B630 | DE85 | 00D8F6 | A=7E89 Y=6400 | 70 -> 104 |
| 0A:9B2B | DE85 | 00D90F | A=7E8A Y=5800 | 71 -> 72 |
| 0A:9B72 | DE85 | 00D930 | A=7E8A Y=5D00 | 74 -> 76 |
| 11:FC20 | DE85 | 00D9AE | A=7F91 Y=3C60 | 767 -> 4064 |
| 13:9A84 | DE85 | 00D9AE | A=7F93 Y=4C40 | 2232 -> 4128 |
| 15:B78E | DE85 | 00D9AE | A=7F95 Y=5C60 | 1802 -> 3616 |
| 15:B338 | DE85 | 00D9AE | A=7F95 Y=6A80 | 1110 -> 3008 |
| 13:D5E8 | DE85 | 00D9AE | A=7F93 Y=7640 | 1241 -> 4192 |
| 12:B50E | DE85 | 00D9AE | A=7F92 Y=86A0 | 1588 -> 3232 |
| 04:8000 | BF14 | 9FB2F1 | A=7F84 Y=0000 | 16692 -> 31680 |
| 18:BAC7 | BF14 | 9FF0D7 | A=7F98 Y=0000 | 1469 -> 4683 |
| 19:8211 | BF14 | 9FF0FD | A=7F99 Y=0000 | 514 -> 1038 |
| 0E:C3BB | DE85 | 008810 | A=7F8E Y=0000 | 4179 -> 8192 |
| 04:8000 | DE85 | 00D4AC | A=7F84 Y=0000 | 16692 -> 31680 |
| 09:DACB | DE85 | 008861 | A=7E89 Y=6200 | 15 -> 17 |
| 0D:CDCE | DE85 | 008884 | A=7F8D Y=0000 | 2372 -> 8960 |
| 07:F900 | DE85 | 00D273 | A=7F87 Y=0000 | 17 -> 352 |
| 07:F882 | DE85 | 00D289 | A=7F87 Y=0000 | 125 -> 2048 |
| 09:B702 | DE85 | 00D8F6 | A=7E89 Y=6400 | 1 -> 0 |
| 0A:9CDE | DE85 | 00D90F | A=7E8A Y=5800 | 29 -> 28 |
| 0A:9CFB | DE85 | 00D930 | A=7E8A Y=5D00 | 30 -> 32 |
| 0E:F929 | DE85 | 00D9AE | A=7F8E Y=0000 | 1000 -> 4416 |
| 12:A2D4 | DE85 | 00D9AE | A=7F92 Y=1140 | 1157 -> 3296 |
| 13:AF9C | DE85 | 00D9AE | A=7F93 Y=1E20 | 1370 -> 4000 |
| 13:CF04 | DE85 | 00D9AE | A=7F93 Y=2DC0 | 1764 -> 4576 |
