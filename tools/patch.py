#!/usr/bin/env python3 -I
"""patch.py ROM PATCHFILE OUT.sfc [OUT.ips] : apply a text patch to a ROM and optionally write an IPS of only our bytes.
Patch file lines (comments with #):
  BB:AAAA  xx xx xx ...        bytes at LoROM bank:addr (bank 00-1F; $80+ mirrors folded)
  word BB:AAAA  v1 v2 ...      16-bit little-endian words (decimal or 0x..)
  @0xFILEOFF  xx xx ...        bytes at a file offset
Each patched range is printed with the old bytes, so a patch is self-documenting."""
import sys, re
def off(b, a): return (b & 0x7F) * 0x8000 + (a - 0x8000)
def parse(txt):
    for l in txt.split('\n'):
        l = l.split('#')[0].strip()
        if not l: continue
        m = re.match(r'word\s+([0-9A-Fa-f]{2}):([0-9A-Fa-f]{4})\s+(.*)', l)
        if m:
            vs = [int(x, 0) for x in m.group(3).split()]
            yield off(int(m.group(1), 16), int(m.group(2), 16)), b''.join(v.to_bytes(2, 'little') for v in vs); continue
        m = re.match(r'([0-9A-Fa-f]{2}):([0-9A-Fa-f]{4})\s+(.*)', l)
        if m: yield off(int(m.group(1), 16), int(m.group(2), 16)), bytes(int(x, 16) for x in m.group(3).split()); continue
        m = re.match(r'@(0x[0-9A-Fa-f]+)\s+(.*)', l)
        if m: yield int(m.group(1), 16), bytes(int(x, 16) for x in m.group(2).split()); continue
        raise SystemExit('bad patch line: ' + l)
def ips(orig, new):
    out = bytearray(b'PATCH'); i = 0; n = len(new)
    while i < n:
        if i < len(orig) and orig[i] == new[i]: i += 1; continue
        last = i; j = i + 1
        while j < n and j - i < 0xFFFF and j - last <= 6:
            if j >= len(orig) or orig[j] != new[j]: last = j
            j += 1
        start = i if i != 0x454F46 else i - 1
        out += start.to_bytes(3, 'big') + (last + 1 - start).to_bytes(2, 'big') + bytes(new[start:last + 1]); i = last + 1
    return bytes(out) + b'EOF'
if __name__ == '__main__':
    rom = bytearray(open(sys.argv[1], 'rb').read()); orig = bytes(rom)
    for o, b in parse(open(sys.argv[2]).read()):
        print('%06X: %s -> %s' % (o, rom[o:o + len(b)].hex(' '), b.hex(' '))); rom[o:o + len(b)] = b
    open(sys.argv[3], 'wb').write(rom)
    if len(sys.argv) > 4: open(sys.argv[4], 'wb').write(ips(orig, bytes(rom)))
