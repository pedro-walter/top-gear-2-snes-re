#!/usr/bin/env python3 -I
"""Map a PC histogram (scripts/pchist.lua) onto the subroutines of a generated listing.
usage: prof.py out/<tag>_pchist.txt disasm/tg2_usa.asm [N]   -> top-N subs by executed instructions"""
import sys, re, bisect, collections
hist = collections.Counter()
for l in open(sys.argv[1]):
    a, n = l.split(); a = int(a, 16)
    b = a >> 16
    if b >= 0x80: a &= 0x7FFFFF          # FastROM mirrors -> canonical bank
    hist[a] += int(n)
subs = {}
for l in open(sys.argv[2]):
    m = re.match(r'(sub_[0-9A-F]{6}):', l)
    if m: subs[int(m.group(1)[4:], 16)] = m.group(1)
keys = sorted(subs)
tot = sum(hist.values()); per = collections.Counter()
for a, n in hist.items():
    i = bisect.bisect_right(keys, a) - 1
    per[subs[keys[i]] if i >= 0 else '?'] += n
top = int(sys.argv[3]) if len(sys.argv) > 3 else 25
for s, n in per.most_common(top): print(f'{s}  {n:10d}  {100*n/tot:5.1f}%')
