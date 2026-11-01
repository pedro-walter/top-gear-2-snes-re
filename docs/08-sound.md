# Sound: SPC700 upload (first look; code read, not yet verified with an APU trace)

* Front-end entry calls `1F:F04E` (`called from 1F:8051`): zeroes the sound-state bytes `$D0-$DA,$CF,$D6` (DP=$0100), decompresses the **SPC driver** with `1F:BF14` from `9A:8000` to **WRAM `7F:0000`**, then
  `1F:F230` uploads it through the standard **SPC700 IPL protocol** (waits `$BBAA` on `$2140`, then blocks `[length][dest][bytes...]` via ports 0-2 with the echo handshake; pointer in `[$C5]` = `7F:0000`) and finishes by waiting for the driver to answer `$77` on `$2141`.
* `1F:F0A3` (called from `1F:8139`, `1F:8323`, `1F:C440`) loads a **song**: `$C1` = song id; `9B:8000 + 2*id` is a pointer into bank 1B (`0x8008, 0x8072, 0x80E2, 0x814C` = 4 songs/sound sets).
  Header (offsets inside the entry): three 4-byte descriptors (word source + bank) for **three decompressed pieces** (each `1F:BF14` -> `7F:0000` -> `1F:F180` + `1F:F28F` upload; the `1F:F28F` path is the *driver's own* protocol: byte `$AB` on port 3, answered `$CD`, then `[word]` commands with port-3 toggling),
  a word at `+0x0C` (`$C9`, SPC destination address, e.g. `$4040`) and from `+0x0E` a list of 6-byte records **(start word, end word, bank word)** = raw sample/sequence blocks in banks 1A/1B (e.g. `9A:DBDB-E1C3`, `9A:B538-BCF4`...) uploaded with `1F:F423` until a zero start word.
* `1F:BF14` is a front-end copy of the **variant B compressor** (same format as `01:DE85`, see `docs/11-assets.md`; was first believed to be a third compressor) (a jump table at `1F:BF2F` indexed by the control byte `&0xFE`, per-range handlers `C02F, C075, C0AB, C0DD, C165, C1E2, C20D`), different from the graphics compressors A/B; it is used 27 times (all the front-end/shop graphics too). **Decoded and verified** (`tools/bf14.py`, byte-exact against the WRAM image at `7F:0000` after the driver decompression, 3244 bytes; see the format in its docstring). Note: `E0-FF` copies `b2+5` bytes (the word-copy loops add 4).
* `tools/bf14dump.py ROM disasm OUT` decompresses all statically-known streams (16 found; 9 more call sites load their args dynamically). Examples: `1A:8000` = SPC driver (SPC700 code starting `mov $f4,#0; mov x,#$cf; mov sp,x` ...), `1E:D129` (20928 B) = **car-shop icon/tile sheet** (clean 4bpp tiles), `1C:98C9` = car/shop background tiles, `1D:8000`.. = more shop/menu tiles, `1E:82E9` (39136 B -> `7E`) = not 4bpp tiles (probably tilemap/other data).
* Open: disassemble the SPC driver, find the music/sfx command interface used in-race (writes to `$2140-$2143` during a race).

## In-race sound mailbox (`01:DA29..DAD4`, called once per frame, DP switched to `$0500`; read from code)
* Wait until the SPC answers `$77` on `$2141` (driver idle), then send up to four 4-byte commands, each as ports 1,2,3 first and port 0 last (port 0 = command id | `$80` request bit; the SPC clears bit7 when it consumed it):
  1. `$0598/$0599/$059A` (`$98/$99/$9A`) - first command; `$0598` is **engine pitch/volume** (`ADC $00FC`, clamped at `$FF`), port 0 = `((STAT78>>3)&2) | $AE | $80` (the PAL/NTSC bit goes to the driver).
  2. two sets `$9B..$9D` / `$9E..$A0` chosen by bit 4 of `$AE` (double buffer toggled via `$05AE ^= $10`).
  3. `$A1..$A3,$A5` (id in `$A1`, params `$A2,$A5`, `$A3`) and 4. `$A7..$A9,$AB`.
* After sending, `$9A=$FF`, `$A1/$A7` are cleared (slots are one-shot) and ports 0/2 are zeroed. So any code that wants a sound just stores an id into `$05A1` / `$05A7` etc. (SFX queue) and the frame mailbox forwards it.
* The `$2140-$2143` write callback did not fire in this Mesen build (APU I/O callbacks seem not to be delivered); use `exec` callbacks at the STA sites above if you need to log commands.
* Sample of a 1000-frame acceleration run (`scripts/sfxlog.lua`): slot 0 port-0 byte alternates `84/94` (bit 4 = the double-buffer toggle), slot 2 is mostly `00`/`06` (id 6 ~ 630 times: a repeated effect, probably the engine loop retrigger) and ids `0x10..0x19` appear 10-100 times each (likely engine pitch/gear steps, more at higher numbers), `0x0E`, `0x07` rarely. Names unverified.

## SPC700 driver (disassembled with `tools/spc700.py`)
The decompressed driver (`out/spc_driver.bin`, 3244 B) is IPL-format blocks `[len][dest][bytes]`: **3216 bytes at SPC `$0810`** (code; entry `$0810`) and 16 bytes at `$1500`, terminated by `len=0, dest=$0810` (the IPL jump). Disassemble: `python3 -I tools/spc700.py out/spc_blk810.bin 810 810` (blocks split by a few lines of Python; see git history of this doc). Operand order of `MOV dp,#imm` is `imm dp` in the byte stream.
* `0810` init: clear DP/page 1-3, DSP setup (`$F2/$F3` index/data), `CALL 0B58`, then main loop `088E`: `CALL 094E` (read mailbox), `CALL 0899` (apply DSP writes), `CALL 10AA` (sequencer tick), repeat. Timer-0-style 8 voice allocator: `$44` = voice mask, `$2D+X` = per-voice priority, `0F1D` picks the lowest-priority voice.
* **Mailbox, SPC side (`094E`)** - four 4-byte commands per frame, handshake on port 0 bit 7 (CPU sets, SPC answers `$77` on port 1 and clears):
  1. port0 -> `$54` flags, port1 -> `$57` (engine value, written to DSP `$1C`/`$0C`... master/volume regs), port2 -> `$52`, port3 -> `$56`. Flag bits in `$54`: bit0 = **enter the upload protocol** (`09BD`: key-off, wait `$AB` on port 3, answer `$CD`, receive `[word len...]` blocks; this is the `1F:F28F` path), bit1 = selects the opcode patched into `$0804` (`$92` vs `$AF`: the PAL/NTSC timing tweak), bit4 = selects which of two parameter sets (`$0542/$0546`) goes to the DSP (the CPU's double buffer), bit5 = write `$63` into a per-voice table `$35+X`.
  2. port0 -> `$61`, ports 1-3 -> `$60,$62,$63`.
  3. port0 `&$7F` -> `$58` (SFX id A), ports -> `$59,$5F,$5A`; if `$58 != 0` the driver calls `0ED8` with A = id to start the effect on a voice.
  4. same for `$5C` (SFX id B, params `$5D,$5F,$5E`).
* `0ED8` (start effect/sequence): allocate a voice (`0F1D`), reset the voice's tracks (`$0280/$0288/$0290+X`), then `0F53`: **ids `>= $40` are rejected**; the id indexes the 4-byte records at `$0400+id*4` / `$0501+id*4` (sequence pointers and flags, loaded with the song set, so the table content depends on the song/sound set in bank 1B).
* So the CPU-side ids in `$05A1/$05A7` (docs above) are SFX ids 0..63 whose meaning comes from the song set's data, not from the driver.
Open: the sequence byte-code at `10AA` and the id -> sound naming (needs dumping the `$0400/$0500` tables after the set upload; Mesen can read APU RAM via `emu.memType.snesSpcRam`? untested).

## SFX trigger sites in the race code (static scan of `STA $05A1/$05A7`, DP-independent)
The CPU writes a **16-bit word** to `$05A1` (low byte = SFX id, high byte `$FF` = "loop/keep" modifier? or `$80` = the second variant) and a word to `$05A3` (parameter: `4`/`$10` for player 1, `8`/`$20` for player 2: the code at `00:A2xx..B3xx` is a copy of `00:8Bxx..9Axx` for P2), then the mailbox forwards them. Id `$0001` written to `$05A1` is the "stop this effect" command.
| site (P1 / P2 copy) | word | param | context |
|---|---|---|---|
| `00:8DD2` / `00:A636` | `$FF20` / `$FF21` | 4 / 8 | a button edge in `$0030` bit `$2000` sets `$34` bit `$0800`; the matching release at `8DFC`/`A660` writes `$0001` |
| `00:8E24` / `00:A688` | `$FF14` | `$10` / `$20` | start of a looping effect (state `$01A6`, `$8000`) |
| `00:8E54` / `00:A6B8` | `$FF13` | `$10` / `$20` | **nitro** activation (`$C4` -> `$BC`, `$2C = $0230` timer, `$01A6 |= $8000`); stop at `8EA4` / `A708` |
| `00:9A92` / `00:B2F4` | `$8017` | 4 / 8 | `$0001` written at `9AA9` / `B30B` (collision/skid loop, stopped when it ends) |
| `00:D76F`, `D7CB` | `$FF1A`, `$FF19` | 1 | in the car-list walker `00:D726` (other-car effects: passing / engine of an AI car near the player) |
| `00:A29B`, `00:BAFD` | register value | `$3F` | one-shot with the id taken from a register/table (`$3F` = max-volume param) |
Engine pitch/volume goes through `$0598/$059D` (`00:8B79`, `00:9B0D`), not through the effect slots. Names of the ids are still unknown (the driver does not name them either; they index the song set's table at SPC `$0400+id*4`).

## Reading SPC RAM from Mesen
`emu.read(addr, emu.memType.spcRam)` (64 KB) and `emu.memType.spcDspRegisters` work in the headless runner (`scripts/spcdump.lua`, env `TG_SPC=frames`, writes `out/<tag>_<f>.spcram/.dsp`); `spcMemory` and `spcDebug` also exist. With it: the SFX table of the race song set is at SPC `$0400+id*4` and `$0500+id*4`; it has **34 real entries (ids 0..33 = `$21`)**, the rest repeat a filler (`14 30 cf 1f / 06 06 07 00`), which agrees with the highest id the CPU sends (`$21`, `00:A636`). Example entries (4 + 4 bytes): id 1 `14 01 bf ba / 80 c6 07 24`, id 19 `ff e2 ff e1 / 80 0d 12 ff` (field meaning not decoded: probably sample number, ADSR, pitch and priority).
