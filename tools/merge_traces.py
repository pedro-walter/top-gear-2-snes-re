#!/usr/bin/env python3 -I
"""Union of exec-coverage traces ("BBAAAA m x"), dropping junk from crashed fuzz runs:
banks outside ROM/WRAM, and seeds whose opcode is BRK/COP/WDM/STP.
usage: merge_traces.py ROM OUT.txt IN.txt..."""
import sys
rom = open(sys.argv[1], 'rb').read()
seen = {}
for p in sys.argv[3:]:
    for l in open(p):
        t = l.split()
        if len(t) < 3: continue
        a = int(t[0], 16); b, o = a >> 16, a & 0xFFFF
        if b in (0x7E, 0x7F) or ((b & 0x7F) < 0x40 and o < 0x2000):
            pass                                   # WRAM / mirrors: kept (stubs); the disassembler judges them
        elif (b & 0x7F) <= 0x1F and o >= 0x8000:
            if rom[((b & 0x1F) << 15) | (o & 0x7FFF)] in (0x00, 0x02, 0x42, 0xDB): continue
        else:
            continue
        seen[(a, t[1], t[2])] = 1
with open(sys.argv[2], 'w') as f:
    for a, m, x in sorted(seen): f.write(f'{a:06X} {m} {x}\n')
print(len(seen), 'seeds')
