#!/usr/bin/env python3 -I
"""Top Gear 2 (SNES) decompressors, ported from 01:DC53 (variant A) and 01:DE85 (variant B).
decompress(rom, off, variant) -> (output bytes, input bytes consumed). off = file offset of the stream."""
def decompress(rom, i, variant='a'):
    o = bytearray(); s = i
    def cp(src, n):
        if src < 0: raise ValueError('backref before start')
        for k in range(n): o.append(o[src + k])      # byte-wise: overlap allowed
    while True:
        c = rom[i]; i += 1
        if c == 0: break
        if variant == 'a':
            t = c >> 5; n = c & 0x1F
            if t == 0: o += rom[i:i+n]; i += n
            elif t == 1:
                n = ((n << 8) | rom[i]) + 0x20; i += 1; o += rom[i:i+n]; i += n
            elif t == 2: o += bytes([rom[i]]) * (n + 3); i += 1
            elif t == 3:
                n = ((n << 8) | rom[i]) + 0x24; i += 1; o += bytes([rom[i]]) * n; i += 1
            elif t == 4: cp(len(o) - n - 2, 2)
            elif t == 5: cp(len(o) - n - 3, 3)
            else:
                d = ((c & 3) << 8) | rom[i]; i += 1; k = ((c >> 2) & 0xF) + 3
                cp(len(o) - d - k - 1, k + 1)
        else:
            if c < 0x40: n = c & 0x3F; o += rom[i:i+n]; i += n
            elif c < 0x50:
                n = (c & 15) + 3; b1 = o[-1]; d = (b1 - o[-2]) & 255
                for _ in range(n): b1 = (b1 + d) & 255; o.append(b1)
            elif c < 0x60:
                n = (c & 15) + 2; w1 = o[-2] | o[-1] << 8; w0 = o[-4] | o[-3] << 8; d = (w1 - w0) & 0xFFFF
                for _ in range(n): w1 = (w1 + d) & 0xFFFF; o += bytes([w1 & 255, w1 >> 8])
            elif c < 0x70: o += bytes([o[-1]]) * ((c & 15) + 3)
            elif c < 0x80: o += bytes([o[-2], o[-1]]) * ((c & 15) + 2)
            elif c < 0xC0: cp(len(o) - (c & 0x3F) - 3, 3)
            elif c < 0xE0:
                d = ((c & 3) << 8) | rom[i]; i += 1; cp(len(o) - d - 3, ((c >> 2) & 7) + 4)
            else:
                d = ((c & 0x1F) << 8) | rom[i]; b = rom[i+1]; i += 2; cp(len(o) - d - 3, b + 5)
    return bytes(o), i - s

def lorom(bank, addr): return (bank & 0x7F) * 0x8000 + (addr - 0x8000)
