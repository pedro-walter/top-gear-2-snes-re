# Password system (USA; 1F:D4B3 validator, entry screen around 1F:C838..D0A0)
Screen "ENTER PASSWORD": 22 characters, 32-char alphabet `B C D F G H J L M N P Q R T V W Y # ? ( ) < > 1 2 3 4 5 6 7 8 9` (+ del / end).
Text buffer = draw-list entries of 6 bytes at `$17D3 + 6k` = `80 posL posH 82 CHAR 83` (CHAR = ASCII at `$17D7+6k`). The cursor blink rewrites the current slot.
Pressing "end" -> `1F:CFB9` copies the 22 chars to `$1780..`, calls `sub_1FD4B3` (carry set = invalid -> "INVALID PASSWORD").
## Algorithm (implemented and verified in `tools/password.py`)
1. idx_i = index of char i in ROM alphabet `9F:D7D9` (the ASCII bytes `42 43 44 46 47 48 4A 4C 4D 4E 50 51 52 54 56 57 59 31..39 23 3F 28 29 3C 3E`).
2. 5-bit v_i = ((idx_i - idx_{i-1}) XOR KEY[i]) & 31, KEY = `9F:D7F9` (22 bytes `0D 05 1A 14 1A 0E 17 07 16 0D 0C 16 06 13 0D 1B 1D 1B 1D 1F 12 00`), idx_{-1}=0.
3. N = sum v_i * 32^i (110 bits).
4. Mixed-radix digits, least significant first (division routine `1F:D887`), radices `0x6D, 2, 0x41, 3, 0x500, 10, 2, 8, 5,5,5, 4,4,4,4,4,4, 0x500, 10, 2, 8, 5,5,5, 4,4,4,4,4,4` (30 digits).
5. Digit 0 = checksum = (sum of the 29 other stored words, 16-bit) mod 109. Stored value of the 0x41 digit is `digit>>2`; of each radix-10 digit `d>=5 ? (d-5)|0x8000 : d`.
6. On success the words are copied to the game variables: `$1CE3` (highest unlocked country, from digit `0x41`>>2; with `$01E3` bit15 set (a "password for a new game vs. continue" flag) the check is `>= $1CE1`), `$1CDB` (digit 1, 2 values),
   `$1CDD` (digit 3: 0..2 = **difficulty**, same as the Options screen AMATEUR/PROFESSIONAL/CHAMPIONSHIP, becomes `$0120` via `7E:FE06`), then per-player (two blocks of 14 digits) the radix-0x500 value (1280: money/points, $1D42 / $1D40...),
   radix-10 (car/slot with bit15 flag), 2, 8, 5, 5, 5 and six 4-valued digits (**car-shop upgrade levels** 0..3 or 0..4). Names `a_*/b_*` in password.py are positional guesses.
## Player block layout = car shop state (verified in the shop, `scripts/shoplog.lua`)
Each player has a 0x29-byte struct in WRAM: **P1 at `$1CFF`, P2 at `$1D28`** (`$A3` = player offset 0 / `$29` in the shop code).
| off | P1 addr | meaning | password digit radix |
|---|---|---|---|
| +00 | 1CFF | toggle set by left/right in the shop (Auto/Manual, guess) | 2 |
| +02 | 1D01 | selected car 0..4, bit15 = confirmed (`1F:8F11`) | 10 (d>=5 -> (d-5)\|8000) |
| +04..+14 | 1D03,05,...,13 | one word per shop category, 0 = not bought, `$8000\|level` = bought. Order: **Engine, Wet Tires, Dry Tires, Gearbox, Nitro**, then three more (Side/Rear/Front Armor; Paint) | 4,4,4,4,4,4,5,5,5 (k0..k8) |
| +16 | 1D15 | unknown (radix 8, maybe paint colour; only the password code touches it) | 8 |
| +18 | 1D17 | copy of k1 (a quirk of the password code) | (shares digit with k1) |
| +1A | 1D19 | **money in $1000 units** (max 1279); purchases subtract the price table entry `9F:0000+9F:AC5B[cat]*..+level*2` | 0x500 |
Verified by buying with money poked into `$1D19`: Engine level 3 costs 80 (-> $80000), Wet 3, Dry 4, Gearbox 50, Nitro 30 (matches the on-screen prices).
In the password, block 1 (first) feeds the **P2** struct (`$1D28..$1D42`), block 2 feeds **P1** (`$1CFF..$1D19`). `tools/password.py` names are now `p1_*`/`p2_*`
(`*_engine, *_wet, *_dry, *_gearbox, *_nitro, *_up5..up8, *_x8, *_manual, *_car, *_money`).
Default (new game) shop state is two 9-word zero tables at `9F:8413` (P1) and `9F:843C` (P2), installed by `1F:DA09`; `1F:DA3C` saves a copy to `$1D45...`.
Caveat: when `$01E3` bit15 is set (the normal flow from the title screen) a *valid* password sets `$1D19 = $1CE1*10` (and `$1D42` too when `$1CDB != 0`) right after loading (`1F:CFF4`),
so the money in the password is overridden in that flow (we saw 30 for `$1CE1`=3); the upgrade words are kept (verified: engine=3, nitro=2 survive).
Race winnings are added to `$1D19`/`$1D42` from `$1D71`/`$1D73` at `1F:81F8`.

## Test
`tools/password.py encode country4=36 difficulty=1 a_money?=100` -> `64PB<RFPBT9W5M5YTMHG66`; injecting it at `1F:CFB9` (`scripts/pwtest.lua`, `TG_PW=...`) gives `$1CE3=9, $1CDD=1` (all 10 countries unlocked, difficulty 1).
(Typing it by hand: cursor starts on "end"; the injection avoids navigating the grid.)

EUR/JPN: the same 22-byte KEY table exists in both (file offsets 0xFD9F1 EUR, 0xFDC68 JPN vs 0xFD7F9 USA), so the algorithm is shared; addresses differ, passwords are probably interchangeable (untested).
