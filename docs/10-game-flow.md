# Game flow: championship, results, prizes (front-end, bank 1F)

How to reach it headlessly: `scripts/champ.lua` (force `$019E`=1 lap and an identity standings list at `7E:FE9E` while `00:8A41` runs) + `tools/champ.sh VER FRAMES TAG` (holds X, taps A/Start; writes an exec trace `out/f_<ver>_<tag>_trace.txt` for `make merge`). Caution: **never poke `7E:FE00-FFFF` outside a race**: it is the mirror of the save/shop area (`$1CD7+n`) and crashes the front-end.

## State variables (DP/bank: `$1Cxx` are low WRAM, seen from bank 1F as `9F:1Cxx`; **watch `9F1D19`-style addresses for front-end writes**, `00xxxx` and `7Exxxx` watches miss them)
| var | meaning |
|---|---|
| `$1CE1` | current **country** (0..15; reaching 16 = game completed -> `1F:E52E`) |
| `$1CE5` | race index inside the country (0..3; `+1`, bit2 set = country done -> `$1CE5=0`, `$1CE1++`) |
| `$1CE3` | highest country reached (`1F:C9CD` compares the cursor to it; also what `scripts/unlock.lua` pokes) |
| `$1CDB` | 2P flag (second player block used) |
| `$1D45..$1D6F` | snapshot of the P1/P2 shop state taken at the start of a country (`1F:DA3C`; restored by `1F:DA69` when the player fails to qualify / continues) |
| `$1D75..` | 20 words: car ids in **finishing order** (copied from the race list `7E:FE9E`; times in `7E:FEC6`) |
| `$1D9D` | P1 finish time (non-zero = a race just ended); `$1DF1` non-zero = skip results (go to title) |
| `$1DED/$1DEF` | far return vector of the front-end (`1F:809B`); the race exits with `JML [$0076]` (loaded from `7E:FF16`) at `01:839A` |

## After a race
1. `00:DE9B` (per car) counts laps; when `+0x22-1 == $019E` the car finishes: its id is appended to `7E:FE9E[$06EE]`, time `= $001A - $0602` to `7E:FEC6`; at the end `00:DF1D` fills unfinished cars at their current rank (only ranks >= 10 are written, so cars ranked < 10 that have not finished leave holes = id 0).
2. `01:8388`: `JML [$0076]` -> `1F:809B` (front-end re-entry). `1F:81D4` reloads the persistent state from the `7E:FE00` mirror into `$1CD7+` and adds `$1D71/$1D73` (prize carried into this block) to the P1/P2 money.
3. `1F:EB7C` = **results screen**: searches `$1D75` for car id 0 (P1) and id 1 (P2) -> ranks `$2D`/`$2F`; `rank < 10` qualifies ("YOU HAVE QUALIFIED!", PLAYER 1 `nth`, points, prize), otherwise "YOU FAILED TO QUALIFY" and back to the title. The search keeps the **last** match, so unfilled holes (id 0) in the list make P1 look 20th.
4. `1F:ECD6..ED48`: on qualify P1 gets **prize money = `9F:EF46[rank]` x $1000** and points `9F:E35D[rank]`: both tables are `10, 6, 4, 3, 2, 1, 0...` (so 1st = $10000 and 10 points, 6th = $1000 and 1 point; ranks 7-10 qualify but earn nothing). Points accumulate in `$1DC5[car*2]` (the championship table) and the screens that follow are RACE RESULTS (top 10 names + times + points) and CHAMPIONSHIP TABLE (20 drivers, e.g. Ritchie, Ash, Mick, Tony, Greggs, Pat, Paul, Mark, George).
5. `1F:ED48`: `$1CE5++`; after the 4th race (bit2) -> next country (`$1CE1++`, `1F:DA3C` snapshot, `$1CE3 = max`). When `$1CE1` reaches `$10` the game is complete (`1F:E52E`).
6. Then the **car shop** for the next race (screen shows the country/track card: "AUSTRALASIA / Ayers Rock, Length 11 miles, Laps 5, Weather, Time"), then the race. Race 3 (Australasia 3rd track) is a night race with 4 laps.
Open: what `$1DF1` is, the standings screen drawing code, and the 2P variants (`$1CDB != 0`).

## Text
Front-end text is plain ASCII (NUL-terminated) with small control codes (e.g. `0x82` ... `0x83` wrap a heading such as `RACE RESULTS`; position/colour bytes in front of strings). Clusters (USA): `18:8001` (ENTER PASSWORD...), `18:9365-9518` credits (programming, art, music names), `1F:DA97-DBDA` (23 menu/shop strings), `1F:EF6F-F00D` race-results screen (heading, the **20 driver names** via a pointer table at `1F:EF8F..`, names start at `1F:EFA7`; the prize/points tables `1F:EF46`/`1F:E35D` sit right before), `1F:A359-A5FF` (shop/mode texts), `1F:CBE5-CC33`. Driver order = car id order used in `$1D75` (id 0 = Player 1, 1 = Player 2 / first AI...).
