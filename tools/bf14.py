#!/usr/bin/env python3 -I
"""bf14.py : the third TG2 compressor (routine 1F:BF14, "variant C"), a byte-oriented LZ with delta/run commands.
decompress(rom, file_offset) -> (data, bytes_consumed).   CLI: bf14.py ROM BANK ADDR OUT
Command byte c (dispatch table 1F:BF2F, index c>>1):
  00        end
  01-3F     literal copy of c bytes
  40-4F     arithmetic continuation of the last two bytes (delta = b[-1]-b[-2]), (c&15)+3 bytes, mod 256
  50-5F     same with 16-bit words: (c&15)+2 words
  60-6F     run of the last byte, (c&15)+3 bytes
  70-7F     run of the last 16-bit word, (c&15)+2 words
  80-BF     3-byte copy from distance (c&63)+3
  C0-DF     2-byte code: dist = ((c&3)<<8 | b1)+3, len = ((c>>2)&7)+4
  E0-FF     3-byte code: dist = ((c&31)<<8 | b1)+3, len = b2+5"""
import sys
def decompress(rom, p, limit=1 << 20):
    o = bytearray(); s = p
    while True:
        c = rom[p]; p += 1
        if c == 0: break
        if c < 0x40: o += rom[p:p + c]; p += c
        elif c < 0x50:
            d = (o[-1] - o[-2]) & 255; v = o[-1]
            for _ in range((c & 15) + 3): v = (v + d) & 255; o.append(v)
        elif c < 0x60:
            w1 = o[-2] | o[-1] << 8; w2 = o[-4] | o[-3] << 8; d = (w1 - w2) & 0xFFFF; v = w1
            for _ in range((c & 15) + 2): v = (v + d) & 0xFFFF; o += bytes((v & 255, v >> 8))
        elif c < 0x70: o += bytes([o[-1]]) * ((c & 15) + 3)
        elif c < 0x80: o += bytes(o[-2:]) * ((c & 15) + 2)
        elif c < 0xC0:
            d = (c & 63) + 3
            for _ in range(3): o.append(o[-d])
        elif c < 0xE0:
            d = ((c & 3) << 8 | rom[p]) + 3; n = ((c >> 2) & 7) + 4; p += 1
            for _ in range(n): o.append(o[-d])
        else:
            d = ((c & 31) << 8 | rom[p]) + 3; n = rom[p + 1] + 5; p += 2
            for _ in range(n): o.append(o[-d])
        if len(o) > limit: raise ValueError('output too large')
    return bytes(o), p - s
if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read(); b = int(sys.argv[2], 16); a = int(sys.argv[3], 16)
    d, u = decompress(rom, (b & 0x7F) * 0x8000 + (a - 0x8000)); open(sys.argv[4], 'wb').write(d); print(len(d), 'bytes from', u)
