#!/usr/bin/env python3 -I
"""portsyms.py USA.asm TARGET.asm symbols_usa.txt > symbols_target.txt
Ports routine names/docs to another ROM version by matching the first N instructions (branch targets and 16-bit absolute
operands masked, like asmdiff.py).  Only unique matches are emitted; the rest are listed on stderr."""
import re, sys
N = 14
def load(p):
    out = []
    for l in open(p):
        m = re.match(r'  ([0-9A-F]{6})  ((?:[0-9A-F]{2} )+)\s*(\S[^;]*?)\s*(;.*)?$', l.rstrip('\n'))
        if m: out.append((int(m.group(1), 16), m.group(3)))
    return out
def key(t):
    mn = t.split()[0]
    if mn in ('JSR','JMP','JSL','JML','BRA','BRL','BEQ','BNE','BCC','BCS','BMI','BPL','BVC','BVS'): return mn
    return re.sub(r'(?<![#])\$[0-9A-F]{4}\b', '$X', re.sub(r'\$[0-9A-F]{6}\b', '$L', t))
A, B = load(sys.argv[1]), load(sys.argv[2])
ka = [key(t) for _, t in A]; kb = [key(t) for _, t in B]
ia = {a: i for i, (a, _) in enumerate(A)}
idx = {}
for j in range(len(kb) - N): idx.setdefault(tuple(kb[j:j+N]), []).append(j)
out = []; fail = 0
for l in open(sys.argv[3]):
    m = re.match(r'@([0-9A-F]{6}) (\S+)', l)
    if m:
        a = int(m.group(1), 16); cur = None
        i = ia.get(a)
        c = idx.get(tuple(ka[i:i+N])) if i is not None else None
        if c and len(c) == 1: out.append('@%06X %s' % (B[c[0]][0], m.group(2)))
        else:
            out.append('# UNMATCHED %06X %s (%s)' % (a, m.group(2), 'ambiguous' if c else 'no match')); fail += 1
    else: out.append(l.rstrip('\n'))
print('\n'.join(out)); print('unmatched', fail, file=sys.stderr)
