#!/usr/bin/env python3 -I
"""trackmap.py ROM [K] [REPS] : integrate curve profiles of every track, print closure error (end-start / length)."""
import struct, sys, math
rom = open(sys.argv[1], 'rb').read()
K = float(sys.argv[2]) if len(sys.argv) > 2 else 40000.0
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 4
def b(bank, a, n): o = (bank & 0x7f) * 0x8000 + a - 0x8000; return rom[o:o + n]
prof = [struct.unpack('<16h', b(9, 0x8000 + i * 32, 32)) for i in range(64)]
tt = b(10, 0x8000, 512)
def track(t):
    p, n = struct.unpack_from('<HH', tt, t * 8); h = x = y = 0.0; pts = []
    for i in range(n):
        c = b(10, p + 4 * i, 4)[3] & 0x3f
        for _ in range(REPS):
            for v in prof[c]:
                h += v / K * 2 * math.pi / 64 / 16 * 16; x += math.cos(h); y += math.sin(h); pts.append((x, y))
    return pts, h
if __name__ == '__main__':
    for t in range(64):
        pts, h = track(t); L = len(pts); d = math.hypot(*pts[-1])
        print(t, L, 'heading/2pi %.2f' % (h / 2 / math.pi), 'closure %.2f' % (d / L))
