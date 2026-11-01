# Sound: SPC700 upload (first look; code read, not yet verified with an APU trace)

* Front-end entry calls `1F:F04E` (`called from 1F:8051`): zeroes the sound-state bytes `$D0-$DA,$CF,$D6` (DP=$0100), decompresses the **SPC driver** with `1F:BF14` from `9A:8000` to **WRAM `7F:0000`**, then
  `1F:F230` uploads it through the standard **SPC700 IPL protocol** (waits `$BBAA` on `$2140`, then blocks `[length][dest][bytes...]` via ports 0-2 with the echo handshake; pointer in `[$C5]` = `7F:0000`) and finishes by waiting for the driver to answer `$77` on `$2141`.
* `1F:F0A3` (called from `1F:8139`, `1F:8323`, `1F:C440`) loads a **song**: `$C1` = song id; `9B:8000 + 2*id` is a pointer into bank 1B (`0x8008, 0x8072, 0x80E2, 0x814C` = 4 songs/sound sets).
  Header (offsets inside the entry): three 4-byte descriptors (word source + bank) for **three decompressed pieces** (each `1F:BF14` -> `7F:0000` -> `1F:F180` + `1F:F28F` upload; the `1F:F28F` path is the *driver's own* protocol: byte `$AB` on port 3, answered `$CD`, then `[word]` commands with port-3 toggling),
  a word at `+0x0C` (`$C9`, SPC destination address, e.g. `$4040`) and from `+0x0E` a list of 6-byte records **(start word, end word, bank word)** = raw sample/sequence blocks in banks 1A/1B (e.g. `9A:DBDB-E1C3`, `9A:B538-BCF4`...) uploaded with `1F:F423` until a zero start word.
* `1F:BF14` is a **third compressor** (a jump table at `1F:BF2F` indexed by the control byte `&0xFE`, per-range handlers `C02F, C075, C0AB, C0DD, C165, C1E2, C20D`), different from the graphics compressors A/B; it is used 27 times (all the front-end/shop graphics too). **Decoded and verified** (`tools/bf14.py`, byte-exact against the WRAM image at `7F:0000` after the driver decompression, 3244 bytes; see the format in its docstring). Note: `E0-FF` copies `b2+5` bytes (the word-copy loops add 4).
* `tools/bf14dump.py ROM disasm OUT` decompresses all statically-known streams (16 found; 9 more call sites load their args dynamically). Examples: `1A:8000` = SPC driver (SPC700 code starting `mov $f4,#0; mov x,#$cf; mov sp,x` ...), `1E:D129` (20928 B) = **car-shop icon/tile sheet** (clean 4bpp tiles), `1C:98C9` = car/shop background tiles, `1D:8000`.. = more shop/menu tiles, `1E:82E9` (39136 B -> `7E`) = not 4bpp tiles (probably tilemap/other data).
* Open: disassemble the SPC driver, find the music/sfx command interface used in-race (writes to `$2140-$2143` during a race).

## In-race sound mailbox (`01:DA29..DAD4`, called once per frame, DP switched to `$0500`; read from code)
* Wait until the SPC answers `$77` on `$2141` (driver idle), then send up to four 4-byte commands, each as ports 1,2,3 first and port 0 last (port 0 = command id | `$80` request bit; the SPC clears bit7 when it consumed it):
  1. `$0598/$0599/$059A` (`$98/$99/$9A`) - first command; `$0598` is **engine pitch/volume** (`ADC $00FC`, clamped at `$FF`), port 0 = `((STAT78>>3)&2) | $AE | $80` (the PAL/NTSC bit goes to the driver).
  2. two sets `$9B..$9D` / `$9E..$A0` chosen by bit 4 of `$AE` (double buffer toggled via `$05AE ^= $10`).
  3. `$A1..$A3,$A5` (id in `$A1`, params `$A2,$A5`, `$A3`) and 4. `$A7..$A9,$AB`.
* After sending, `$9A=$FF`, `$A1/$A7` are cleared (slots are one-shot) and ports 0/2 are zeroed. So any code that wants a sound just stores an id into `$05A1` / `$05A7` etc. (SFX queue) and the frame mailbox forwards it.
* The `$2140-$2143` write callback did not fire in this Mesen build (APU I/O callbacks seem not to be delivered); use `exec` callbacks at the STA sites above if you need to log commands.
