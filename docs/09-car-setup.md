# Player car setup from the shop state (`00:CD5E`, read from code + table dump)

The shop/save area `$1CD7..$1DF3` is copied to `7E:FE00..` (`1F:81DC`, so `$7EFE00+n` = `$1CD7+n`; `$7EFE06` = difficulty `$1CDD`). At race start `00:CD5E` turns the two player structs
(P1 `$7EFE28..`, P2 `$7EFE51..`, 0x29 apart, layout in `docs/06-password.md`) into the physics variables below. Shop categories (words at struct +04..+16, level 0..3 / 0..4):
k0 Engine, k1 Wet Tires, k2 Dry Tires, k3 Gearbox, k4 Nitro, k5 Gas Tank (4-valued, guess from the name list at `1F:AEA0`: Engine, Wet Tires, Dry Tires, Paint Shop, Gearbox, Nitro, Gas Tank, Side/Rear/Front Armor), k6-k8 the three armors (5 levels), k9 Paint (8 colours).

| shop value | P1 -> P2 var | table (bank 0 / `80:`) | result |
|---|---|---|---|
| k0 engine level | `$068C` -> `$06AE` | direct; `D036[level]` = 40,44,48,52,104,108,112,116 -> `$0698` (P2 `$06B?`) | engine power index |
| k3 gearbox | `$068A` -> `$06AC` | `D0D2[level*2]` = 5,6,6,7 -> `$06C0/$06C2` | **number of gears** (5,6,6,7) |
| k5 = **fuel economy** (verified, see below) | -> `$068E` | `D08E[level]` = 236,240,244,248 (`$0692=$6800`, `$0690=0`) | |
| (prices: 1F:AC6F, see 13-mod-index.md) k4 nitro | `$01A6` / `$06C4` | `D0C2[]` = 6,6,6,6 ; `D0CA[]` = 4096,2816,1280,0 | (meaning of the decreasing value unclear) |
| k6,k7,k8 armors | `$0697`,`$0695`,`$0696` | `D03E` = 24,16,12,8,4 (side/front?), `D043` = 32,28,16,12,8 | damage multipliers, lower = stronger |
| k1/k2 tyres | `$0694` / `$06B6` | `D0A2[ (track_class&7)*4 + level ]`: weather/surface class from `8A:8006+track*8 & 7`; classes 3,4 use the **wet** tyre level, the others the dry one (`D092`) | grip value (32,24,20,16 ... lower = better) |
| **control type** (`1D01`, 0..4; the CONTROL menu, TYPE 1-5) | `$067E,067A,067C,0686,0680,0682,0684` | 7 tables of 5 words at `D048..D084` (stride 10) | **joypad button masks** (see below), not car physics; bit15 of the word -> `$01AA` |
| toggle `1CFF` | `$019A` | 0 if non-zero else `$FFFF` | transmission (auto/manual) flag |
| track record | `$019E` | `64 / word(8A:8002+track*8)`, +1 | **number of laps** (Auckland: 64/13 = 4 -> 5 laps, matches the HUD) |

Player names are 12-char strings at `$7EFE1C` / `$7EFE45` copied to `$01E4` / `$01F0`. `$06EE/$06F0` (rank, finished count) are cleared here.
Open: connect `$067A..$0686` (car constants) and `$068C` to the physics routine `00:8A41` (`docs/03-physics.md` mentions `$D4/$D5/$88`); decode what `$0690..$06C4` mean.

**Verified** (`scripts/upg.lua`, poking the P1 words in the shop and sampling at frame 3300): level 0 -> 3 changes `$068C` 0->3, `$0698` 40->52, `$06C0` 5->7 (gears), `$068E` 236->248 (k5), `$06C4` 4096->0 (k4 nitro), `$0697` 24->8 (k6 armor). The mapping above holds.

## Where the variables are consumed (physics runs with **DP = `$0600`**, so `$8C` means `$068C`; found by grepping DP operands in `00:8A41..9FFF`)
| var | users | what the code does there |
|---|---|---|
| `$8C` engine level | `00:8F51` | `X = $8C*2` indexes the acceleration curve tables right after the "accelerating" flag (`$34` bit0) is set |
| `$8A` gearbox level | `00:8CAE, 8D04, 8D3C, 8D95, 99CD, 9B69, D5BC` | `X = $8A*2`, `ADC 80:BDF3,X` + `$30` (gear) -> index into `80:BDFB` = **gear ratio table** (multiplied by speed `$1D/$1E` through the PPU multiplier) |
| `$94` tyre grip | `00:9375, 9402` | multiplies the cornering/skid quantity (`MPYM` * 8 * `$94`) |
| `$8E` (k5, 236..248) | `00:98D9` | multiplies the speed `$1D` (hardware multiplier) - a speed/drag scale, so k5 is **not** a cosmetic item; its name ("Gas Tank"?) is unverified |
| `$7A,7C,7E,80,82,84,86` **button masks** | `8CD7, 8CEF, 8BCB, 8C19, 931E, 93A9, 8E09` (+ second uses) | `BIT $0028` tests of the joypad word: see the table below |
| `$0698` | `00:8B6B` | engine **sound** volume: `(31-lap_pos...) * $0698` -> `$059D` (sound mailbox), not engine power |
| `$0695/96/97` armor | `00:E9AA, EEF9, EFF9, F016` | damage/collision scaling in the AI/collision code |
| `$C4` (`$06C4`, nitro) | `00:8E36, 8E7A` | nitro quantity/duration |

Effect check (`scripts/upg2.lua`, hold X from the green flag, `$0610` speed_fine at frame 3400, i.e. ~400 frames after the start): engine level 0 -> 3 = 1174 -> **1666 (+42%)**; gearbox 0 -> 3 and k5 0 -> 3 show no difference in that window (they matter at higher speed / gear changes). Later samples are noisy (the car is not steered and hits walls).

## CORRECTION: the "per-car constants" are the controller layout
The word at player struct +02 (`$1D01`, `$7EFE2A`) is the **control type 0..4** chosen in the CONTROL screen of the mode menu (TYPE 1..5 over a pad picture labelled LEFT, RIGHT, DOWN GEAR, UP GEAR, ACCEL, BRAKE, NITRO), not a car model (there is no car choice: the car is always the same). `00:CF33..CFA4` loads seven **joypad masks** for it (P2 uses `$069C..$06A8` from `$7EFE53`):
| var (P1) | table | meaning | type1 | type2 | type3 | type4 | type5 |
|---|---|---|---|---|---|---|---|
| `$067E` | `80:D048` | ACCEL | X | X | R | B | Y |
| `$0680` | `80:D070` | BRAKE | B+Y | A | L | Y | X |
| `$0686` | `80:D066` | NITRO | A | B+Y | B+Y | A | L+R |
| `$067A` | `80:D052` | UP GEAR | R | R | X | Up | B |
| `$067C` | `80:D05C` | DOWN GEAR | L | L | A | Down | A |
| `$0682` | `80:D07A` | LEFT | Left | Left | Left | L | Left |
| `$0684` | `80:D084` | RIGHT | Right | Right | Right | R | Right |
Mask values are SNES joypad-word bits (`B=8000 Y=4000 Select=2000 Start=1000 Up=0800 Down=0400 Left=0200 Right=0100 A=0080 X=0040 L=0020 R=0010`). Check: `00:8F42` `LDA $7E; BIT $0028` gates acceleration (X accelerates in type 1), `00:8CD9/8CF1` (`TRB $0030`) are the gear-shift edges. Bit 15 of the stored word (digit >= 5 in a password) -> `$01AA`/`$01C4` (unknown flag). The password digit radix-10 field `p?_control` = `type + 5*flag`.

## k5 is the fuel gauge (verified 2026-11-01)
`$068E` (k5 = 236/240/244/248, i.e. signed -20/-16/-12/-8) is the multiplier in `00:98D9..9905`: each frame, `speed-ish value ($061B:$1D) x $8E` (signed `$211B/$211C` multiply) is added `dt` times to the 32-bit **fuel accumulator `$0690/$0692`** (clamped at 0). It starts at `$68000000` (set at `00:D5AA`, `$01AE = $0D00`) and `$01AE = $0692 >> 3` feeds the "E...F" bar under the car icon on the HUD (`01:BF90`, `01:C4EC`, and when `$01AE < $0300` the last segment `$18` is cleared).
* Drain is proportional to speed and to `-k5`: with k5 = 248 the gauge dropped 0x33 in 700 frames against 0x7F for 236 (ratio ~2.5 = 20/8, so a **higher k5 = slower drain**; level 3 is the best tank).
* Poking `$0692` to `$0300` empties the bar within ~400 frames. In a 1200-frame test the car kept driving at normal speed with an empty gauge (top speed ~$06C2), so I found **no penalty for running dry** (not exhaustively tested; AI cars have no gauge).
* Pokes must use `emu.write(addr, v, emu.memType.snesWorkRam)`; `R.ram/R.ramw` are read-only helpers.
