#!/usr/bin/env python3 -I
"""Dump the track table (USA: bank 0A:8000, 8 bytes/track, indexed by WRAM $0108 = 4*country+sub).
entry: +0 ptr (bank 0A), +2 count N, +4 ?, +6 flags.  segment list = N+1 records of 4 bytes (last repeats first), rec[3] = length.
usage: trackdump.py ROM [track ...]"""
import sys; sys.path.insert(0,__import__('os').path.dirname(__file__))
from tg2decomp import lorom
r=open(sys.argv[1],'rb').read(); o=lorom(0x0A,0x8000)
n=64   # 16 countries x 4 tracks; table is 0x200 bytes (0A:8000-81FF)
sel=[int(x) for x in sys.argv[2:]] or range(n)
for t in sel:
    e=r[o+t*8:o+t*8+8]; p=int.from_bytes(e[:2],'little'); cnt=e[2]; q=lorom(0x0A,p)
    segs=[r[q+i*4:q+i*4+4] for i in range(cnt+1)]
    print(f"track {t:2d} (country {t//4} sub {t%4}) ptr 0A:{p:04X} segs {cnt} total_len {sum(s[3] for s in segs[:cnt])} hdr {e.hex(' ')}")
    if len(sel)<=8:
        for s in segs: print('   ',s.hex(' '))
