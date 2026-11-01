#!/usr/bin/env python3 -I
"""declogdump.py ROM declog.txt OUTDIR : decompress every call logged by scripts/declog.lua (BF14 = bf14.py, DC53/DE85 = tg2decomp variants a/b)
to OUTDIR/<kind>_<bank>_<addr>.bin; prints bank:addr, kind, caller, dest, compressed->output size."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bf14, tg2decomp
from PIL import Image
def sheet(d, path, bpp=4):
    sz = 8 * bpp; n = len(d) // sz
    if n == 0: return
    cols = 16; im = Image.new('L', (cols * 8, ((n + cols - 1) // cols) * 8))
    for k in range(n):
        for y in range(8):
            pl = [d[k*sz + 2*y + (16 if p >= 2 else 0) + (p & 1)] for p in range(4)]
            for x in range(8):
                im.putpixel(((k % cols) * 8 + x, (k // cols) * 8 + y), sum(((pl[i] >> (7-x)) & 1) << i for i in range(4)) * 17)
    im.save(path)
rom = open(sys.argv[1], 'rb').read(); out = sys.argv[3]; os.makedirs(out, exist_ok=True)
seen = set()
for l in open(sys.argv[2]):
    p = l.split()
    if len(p) < 6: continue
    kind = p[1]; a = int(p[2], 16); x = int(p[3], 16); y = int(p[4], 16); caller = p[5]
    bank = a & 0x7F; dest = 0x7F if (a >> 8) & 1 or kind == 'BF14' and (a >> 8) == 0x7F else 0x7E
    if (kind, bank, x) in seen: continue
    seen.add((kind, bank, x))
    off = (bank & 0x7F) * 0x8000 + (x - 0x8000)
    try:
        if kind == 'BF14': d, used = bf14.decompress(rom, off)
        else: d, used = tg2decomp.decompress(rom, off, 'a' if kind == 'DC53' else 'b')
    except Exception as e:
        print('%02X:%04X %s caller %s FAIL %s' % (bank, x, kind, caller, e)); continue
    open('%s/%s_%02X_%04X.bin' % (out, kind, bank, x), 'wb').write(d)
    if len(d) >= 256: sheet(d, '%s/%s_%02X_%04X.png' % (out, kind, bank, x))
    print('%02X:%04X %-5s caller %s A=%04X Y=%04X  %d -> %d' % (bank, x, kind, caller, a, y, used, len(d)))
