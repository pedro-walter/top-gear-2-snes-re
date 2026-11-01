# Player car setup from the shop state (`00:CD5E`, read from code + table dump)

The shop/save area `$1CD7..$1DF3` is copied to `7E:FE00..` (`1F:81DC`, so `$7EFE00+n` = `$1CD7+n`; `$7EFE06` = difficulty `$1CDD`). At race start `00:CD5E` turns the two player structs
(P1 `$7EFE28..`, P2 `$7EFE51..`, 0x29 apart, layout in `docs/06-password.md`) into the physics variables below. Shop categories (words at struct +04..+16, level 0..3 / 0..4):
k0 Engine, k1 Wet Tires, k2 Dry Tires, k3 Gearbox, k4 Nitro, k5 Gas Tank (4-valued, guess from the name list at `1F:AEA0`: Engine, Wet Tires, Dry Tires, Paint Shop, Gearbox, Nitro, Gas Tank, Side/Rear/Front Armor), k6-k8 the three armors (5 levels), k9 Paint (8 colours).

| shop value | P1 -> P2 var | table (bank 0 / `80:`) | result |
|---|---|---|---|
| k0 engine level | `$068C` -> `$06AE` | direct; `D036[level]` = 40,44,48,52,104,108,112,116 -> `$0698` (P2 `$06B?`) | engine power index |
| k3 gearbox | `$068A` -> `$06AC` | `D0D2[level*2]` = 5,6,6,7 -> `$06C0/$06C2` | **number of gears** (5,6,6,7) |
| k5 (gas tank?) | -> `$068E` | `D08E[level]` = 236,240,244,248 (`$0692=$6800`, `$0690=0`) | |
| k4 nitro | `$01A6` / `$06C4` | `D0C2[]` = 6,6,6,6 ; `D0CA[]` = 4096,2816,1280,0 | (meaning of the decreasing value unclear) |
| k6,k7,k8 armors | `$0697`,`$0695`,`$0696` | `D03E` = 24,16,12,8,4 (side/front?), `D043` = 32,28,16,12,8 | damage multipliers, lower = stronger |
| k1/k2 tyres | `$0694` / `$06B6` | `D0A2[ (track_class&7)*4 + level ]`: weather/surface class from `8A:8006+track*8 & 7`; classes 3,4 use the **wet** tyre level, the others the dry one (`D092`) | grip value (32,24,20,16 ... lower = better) |
| car (`1D01`, 0..4) | `$067E,067A,067C,0686,0680,0682,0684` | 7 tables of 5 words at `D048..D084` (stride 10) | per-car physics constants (`$067A` = 16,16,64,2048,32768 ...); bit15 of the car word -> `$01AA` |
| toggle `1CFF` | `$019A` | 0 if non-zero else `$FFFF` | transmission (auto/manual) flag |
| track record | `$019E` | `64 / word(8A:8002+track*8)`, +1 | **number of laps** (Auckland: 64/13 = 4 -> 5 laps, matches the HUD) |

Player names are 12-char strings at `$7EFE1C` / `$7EFE45` copied to `$01E4` / `$01F0`. `$06EE/$06F0` (rank, finished count) are cleared here.
Open: connect `$067A..$0686` (car constants) and `$068C` to the physics routine `00:8A41` (`docs/03-physics.md` mentions `$D4/$D5/$88`); decode what `$0690..$06C4` mean.
