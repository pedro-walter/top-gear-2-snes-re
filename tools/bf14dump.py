#!/usr/bin/env python3 -I
"""bf14dump.py ROM DISASM OUTDIR : decompress every statically-known 1F:BF14 stream (JSL with LDA #bank / LDX #addr immediates before it)
to OUTDIR/<bank>_<addr>.bin + a 4bpp tile sheet PNG."""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bf14 import decompress
from PIL import Image
rom = open(sys.argv[1], 'rb').read(); src = open(sys.argv[2]).read().split('\n'); out = sys.argv[3]; os.makedirs(out, exist_ok=True)
def sheet(d, path):
    n = len(d) // 32
    if n == 0: return
    cols = 16; im = Image.new('L', (cols * 8, ((n + cols - 1) // cols) * 8))
    for k in range(n):
        for y in range(8):
            pl = [d[k*32 + 2*y + (16 if p >= 2 else 0) + (p & 1)] for p in range(4)]
            for x in range(8):
                im.putpixel(((k % cols) * 8 + x, (k // cols) * 8 + y), sum(((pl[i] >> (7-x)) & 1) << i for i in range(4)) * 17)
    im.save(path)
seen = set()
for n, l in enumerate(src):
    if not re.match(r'\s+[0-9A-F]{6}\s+22 14 BF 9F', l): continue
    a = x = None
    for k in range(n - 1, max(0, n - 12), -1):
        m = re.match(r'\s+[0-9A-F]{6}\s+(A9|A2) (\w\w) (\w\w)\s', src[k])
        if not m: continue
        v = int(m.group(3) + m.group(2), 16)
        if m.group(1) == 'A9' and a is None: a = v
        if m.group(1) == 'A2' and x is None: x = v
    if a is None or x is None: print('dynamic', l.split()[0]); continue
    bank = a & 0xFF
    if (bank & 0x7F) > 0x1F or x < 0x8000: print('skip', hex(a), hex(x)); continue
    if (bank, x) in seen: continue
    seen.add((bank, x))
    try: d, u = decompress(rom, (bank & 0x7F) * 0x8000 + x - 0x8000)
    except Exception as e: print('FAIL %02X:%04X %s' % (bank, x, e)); continue
    nm = '%02X_%04X' % (bank & 0x7F, x); open('%s/%s.bin' % (out, nm), 'wb').write(d); sheet(d, '%s/%s.png' % (out, nm))
    print('%s: %d -> %d bytes (dest bank %02X)' % (nm, u, len(d), a >> 8))
