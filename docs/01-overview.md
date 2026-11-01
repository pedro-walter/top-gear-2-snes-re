# 01 - Overview (phase 2 start)

Addresses are USA LoROM `bank:offset` (banks 00-1F = file offset `bank*0x8000 + (offset-0x8000)`). EUR/JPN differ by small shifts;
use `tools/asmdiff.py` / `romcmp.py` to map. **(?)** = inferred, not yet verified in the emulator.

## Where the code is (12% of the ROM; the rest is graphics/music/data)
| bank | content |
|---|---|
| 00 | `8000-8A37` 32x32 byte lookup table (scaling/multiplication, rows grow with column x row); engine code from `8A38`; many tables after code (`F093..`) |
| 01 | boot (`8003`), frame sequence (`8145`..), decompressors (`DC53`, `DE85`), NMI (`E2F2`), thunks (`AC79`, `B31A`), `F7FD` setup |
| 08 | race code: `88BCA`, `8CB74` road render (36% of race CPU) |
| 0B | race code: `8000` HDMA table builder, `8578`/`A6EA` per-scanline loops, `D7E7` |
| 0E | ~1.2 KB code mixed with colour data |
| 1F | **front-end**: title, menus, car shop, options. Own environment: DBR `$9F`, DP `$0100`, S `$1FFF`; busy-waits on `$4211/$4212` instead of using NMI |
| 03-06, 18-1E | high entropy: compressed graphics (?) |
| 07 | sound program/music (?) |
| 0C-0F | BGR555 palette words (?) (byte pattern only; 0E also has code) |
| 09,0A,10,11,16,17 | tables / tilemaps / track data (?) |

## Boot and modes (verified)
* RESET `00:8A38` -> `JML 01:8003` -> `01:8008`: forced blank, 2 vblanks, DP=0, S=`$07FF`, `JSR 01F7FD`, `JML 1F:8000` (front-end).
* Bank profile (`scripts/bankprof.lua`, 100-frame windows): frames 0-1650 run only in bank 1F (menus, ~1.4M instr/100 frames = busy-wait);
  a race (frames ~1700+) runs in banks 00, 01, 08, 0B, 0E.  Bank 1F never runs while racing.
* Native vectors point into WRAM stubs (`JML $81xxxx`, see CLAUDE.md). NMI (`01:E2F2`) sets DP=0, DBR=`$82`, copies `$0122`->`$22`,
  steps the screen fade (`$58/$5B`, `$5D/$60`, limit `$0F00`) and increments the frame counters `$1A/$1C`.
* Warm-start magic: `$0700=$1234`, `$0702=$5678` are written at boot (`01:8068`).

## Race frame (verified by profile)
Per frame: `008A41` (road scroll maths) -> `00D726` (walk the car/object records) -> `088BCA` -> `08CB74` (road render) -> `0B8000` (HDMA tables).
CPU profile of a race frame (`tools/prof.py`, 300 frames at speed): 08CB74 36%, 0B8578 14%, 00F042 11% (16x8 signed multiply helper using the PPU
multiplier `$211B/$211C` -> `$2134-36`), 0BA6EA 11%, 00D726 4.5%.  The renderer is pseudo-3D (per-scanline tables + HDMA), not Mode 7 proper;
the Mode 7 multiplier registers are only used as a fast multiplier, and `$4204-$4214` as divider.
Double buffering: the sign of `$0124` selects the table buffer (`7E:AD7E`-ish vs `7E:AE7E`-ish).

## Data structures found
* **Car/object records**: 0x40 bytes each at `7E:C400` + n*0x40 (20 slots), walked by 20 unrolled blocks at `00:D84B-D9DA`, each does `JSR ($E417,X)` (per-record handler table `00:E417`).
* **Speed**: `$01A4` (byte) ~ HUD mph (+/-5 offset), `$0610` (word) a finer value (about 18-21 x HUD value). Found by linear correlation of WRAM dumps against HUD readings
  at 7 moments (r=0.9997 / 0.9993); verify with a watchpoint before relying on it.
* **Decompressor** `01:DC53` (and variant `01:DE85`): A low=src bank, A high bit0=dest bank bit (7E/7F), X=src offset, Y=dest offset, output through `$2180`; command byte top-3-bits -> 7 handlers.
  Port it to Python to extract graphics (next step).

## Tooling added in this step
* `scripts/fuzz.lua` + `tools/fuzz.sh VER menu|race SEEDS...`: random-input explorer that records exec traces (menu fuzz from boot; race fuzz after the race preset holding X).
  Beware: runs are slow with tracing (~4x), `TG_TIMEOUT` is raised in the script; some menu-fuzz runs crash the game (executing zeros at `4F:xxxx`).
* `make merge VER=` -> `tools/merge_traces.py` (union of traces, drops junk from crashed runs); `make disasm` now reads `out/merged_<ver>.txt`.
* `tools/disasm.py`: heuristic jump-table resolver for `JMP/JSR (abs,X)` (reads in-bank code pointers until a word is not plausible code) - raised code from 8.4% to 12%.
* `scripts/bankprof.lua` (per-window bank usage), `scripts/pchist.lua` + `tools/prof.py` (PC histogram -> hottest subroutines).
* Fixed `tools/run.py --watch` (it was turning the spec into an absolute path, so watchpoints never fired).
* Annotations per version: `disasm/annot_<ver>/{symbols,ram,regions,comments,hwregs}.txt` (USA filled, EUR/JPN only hwregs for now).

## Open questions / next steps
1. Reach more code: a full race to the finish (results screen, podium), pit/car-shop paths, 2P, password, other tracks; fuzzing barely moved coverage (bank 1F menu + bank 08/0B race paths dominate).
2. Port the decompressor, then dump the compressed banks to find tiles/tilemaps/music; identify the track data format (`09/0A/10/11`?).
3. Understand car physics: where steering/acceleration is computed (look for writers of `$01A4/$0610`), AI cars, collisions.
4. Locate the SPC700 upload (`1F:F23A` compares `#$BBAA`).

## Doc index (phase 2)
`02-compression.md` decompressors - `03-physics.md` player physics - `04-tracks.md` unlock poke, track table, road builder, segment records, difficulty `$0120` -
`05-ai-cars.md` AI car records/update/setup - `06-password.md` password codec (`tools/password.py`).
* `docs/07-versions.md` - USA/EUR/JPN address map and password compatibility
* `docs/08-sound.md` - SPC700 upload, song table (first look)
* `docs/09-car-setup.md` - shop state -> physics variables (00:CD5E)
