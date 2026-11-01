#!/usr/bin/env python3 -I
"""password.py decode PASSWORD | encode country=N ...   Top Gear 2 (USA) password codec (validator 1F:D4B3).
22 chars from a 32-char alphabet -> 5-bit v_i = ((idx_i - idx_{i-1}) ^ KEY[i]) & 31 -> N = sum v_i*32^i
-> mixed-radix digits (RADIX order below, via 1F:D887, least significant first). First digit = checksum = (sum of 30 stored words) mod 109."""
import sys
ALPHA = "BCDFGHJLMNPQRTVWY#?()<>12345 6789".replace(' ', '')  # screen order; ROM order (below) is what counts
ROMALPHA = bytes.fromhex('42 43 44 46 47 48 4a 4c 4d 4e 50 51 52 54 56 57 59 31 32 33 34 35 36 37 38 39 23 3f 28 29 3c 3e'.replace(' ', '')).decode('latin1')
KEY = bytes.fromhex('0d051a141a0e1707160d0c1606130d1b1d1b1d1f1200')
# (radix, name) in decode order; name -> destination word
FIELDS = [(0x6D, 'checksum'), (2, 'f17D1_music'), (0x41, 'country4'), (3, 'difficulty'), (0x500, 'p2_money'), (10, 'p2_car'),
          (2, 'p2_manual'), (8, 'p2_x8'), (5, 'p2_up8'), (5, 'p2_up7'), (5, 'p2_up6'), (4, 'p2_up5'), (4, 'p2_nitro'), (4, 'p2_gearbox'),
          (4, 'p2_dry'), (4, 'p2_wet'), (4, 'p2_engine'),
          (0x500, 'p1_money'), (10, 'p1_car'), (2, 'p1_manual'), (8, 'p1_x8'), (5, 'p1_up8'), (5, 'p1_up7'), (5, 'p1_up6'),
          (4, 'p1_up5'), (4, 'p1_nitro'), (4, 'p1_gearbox'), (4, 'p1_dry'), (4, 'p1_wet'), (4, 'p1_engine')]
def stored(name, v):   # value as stored in the word table that the checksum sums
    if name == 'country4': return v >> 2
    if name.endswith('car?') : return ((v - 5) | 0x8000) if v >= 5 else v
    return v
def decode(pw):
    assert len(pw) == 22
    prev = 0; n = 0
    for i, ch in enumerate(pw):
        idx = ROMALPHA.index(ch); v = ((idx - prev) ^ KEY[i]) & 31; prev = idx; n |= v << (5 * i)
    out = []
    for r, nm in FIELDS: out.append((nm, n % r)); n //= r
    chk = (sum(stored(nm, v) for nm, v in out[1:]) & 0xFFFF) % 109
    return out, chk == out[0][1], n
def encode(vals):
    """vals: dict name->raw digit (default 0). Returns the password."""
    d = [vals.get(nm, 0) for r, nm in FIELDS[1:]]
    chk = (sum(stored(nm, v) for (r, nm), v in zip(FIELDS[1:], d)) & 0xFFFF) % 109
    ds = [chk] + d; n = 0
    for (r, nm), v in reversed(list(zip(FIELDS, ds))): n = n * r + v
    pw = ''; prev = 0
    for i in range(22):
        v = (n >> (5 * i)) & 31; idx = ((v ^ KEY[i]) + prev) & 31; pw += ROMALPHA[idx]; prev = idx
    return pw
if __name__ == '__main__':
    if sys.argv[1] == 'decode':
        o, ok, rest = decode(sys.argv[2]); print('valid' if ok else 'BAD checksum', 'leftover', rest); [print(' ', *x) for x in o]
    else:
        kv = {k: int(v) for k, v in (a.split('=') for a in sys.argv[2:])}; pw = encode(kv); print(pw); print(decode(pw)[1])
