#!/usr/bin/env python3 -I
"""gfxdump.py ROM DISASM_ASM OUTDIR : decompress every statically-known stream (callers of 01:DC53 / 01:DE85 that load
A/X as immediates) to OUTDIR/<bank>_<addr>.bin and render a 4bpp-grey tile sheet PNG next to it. Streams that fail are listed."""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tg2decomp import decompress, lorom
from PIL import Image
rom = open(sys.argv[1], 'rb').read(); src = open(sys.argv[2]).read().split('\n'); out = sys.argv[3]; os.makedirs(out, exist_ok=True)
def sheet(d, path, bpp=4):
    sz = 8 * bpp; n = len(d) // sz
    if n == 0: return
    cols = 16; rows = (n + cols - 1) // cols; im = Image.new('L', (cols * 8, rows * 8))
    for k in range(n):
        o = k * sz
        for y in range(8):
            pl = [d[o + 2 * y + (16 if p >= 2 else 0) + (p & 1)] for p in range(4)]
            for x in range(8):
                s = 7 - x; p = sum(((pl[i] >> s) & 1) << i for i in range(4))
                im.putpixel(((k % cols) * 8 + x, (k // cols) * 8 + y), p * 17)
    im.save(path)
seen = set()
for n, l in enumerate(src):
    m = re.match(r'\s+[0-9A-F]{6}\s+20 (53 DC|85 DE)', l)
    if not m: continue
    a = x = None
    for k in range(n - 1, max(0, n - 14), -1):
        mm = re.match(r'\s+[0-9A-F]{6}\s+(A9|A2) (\w\w)( (\w\w))?\s', src[k])
        if not mm: continue
        if mm.group(1) == 'A9' and a is None: a = int(mm.group(2), 16)
        if mm.group(1) == 'A2' and x is None and mm.group(4): x = int(mm.group(4) + mm.group(2), 16)
    if a is None or x is None or (a, x) in seen: continue
    seen.add((a, x)); v = 'a' if m.group(1) == '53 DC' else 'b'
    try: d, used = decompress(rom, lorom(a, x), v)
    except Exception as e: print('FAIL %02X:%04X %s' % (a & 0x7F, x, e)); continue
    nm = '%02X_%04X' % (a & 0x7F, x); open('%s/%s.bin' % (out, nm), 'wb').write(d); sheet(d, '%s/%s.png' % (out, nm))
    print('%s variant %s: %d -> %d bytes' % (nm, v, used, len(d)))
