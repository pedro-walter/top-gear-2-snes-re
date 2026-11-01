#!/usr/bin/env python3 -I
"""spc700.py BIN LOADADDR [ENTRY...] : recursive SPC700 disassembler (flow-following from entries, plus linear fallback)."""
import sys
# opcode table: (mnemonic, operand format). operands: d=dp, D=dp+x.. etc encoded in template
T = {}
def a(op, fmt, n): T[op] = (fmt, n)
# n = total length. fmt uses {b1} {b2} {rel} {abs} {dp1} {dp2}
for hi, nm in enumerate(['OR','AND','EOR','CMP','ADC','SBC']):
    b = hi*0x20
    a(b+0x08, nm+' A,#{b1}', 2); a(b+0x06, nm+' A,(X)', 1); a(b+0x04, nm+' A,{dp1}', 2); a(b+0x14, nm+' A,{dp1}+X', 2)
    a(b+0x05, nm+' A,!{abs}', 3); a(b+0x15, nm+' A,!{abs}+X', 3); a(b+0x16, nm+' A,!{abs}+Y', 3)
    a(b+0x07, nm+' A,[{dp1}+X]', 2); a(b+0x17, nm+' A,[{dp1}]+Y', 2)
    a(b+0x09, nm+' {dp2},{dp1}', 3); a(b+0x18, nm+' {dp2},#{b1}', 3); a(b+0x19, nm+' (X),(Y)', 1)
a(0xC8,'CMP X,#{b1}',2); a(0x3E,'CMP X,{dp1}',2); a(0x1E,'CMP X,!{abs}',3)
a(0xAD,'CMP Y,#{b1}',2); a(0x7E,'CMP Y,{dp1}',2); a(0x5E,'CMP Y,!{abs}',3)
a(0xE8,'MOV A,#{b1}',2); a(0xE6,'MOV A,(X)',1); a(0xBF,'MOV A,(X)+',1); a(0xE4,'MOV A,{dp1}',2); a(0xF4,'MOV A,{dp1}+X',2)
a(0xE5,'MOV A,!{abs}',3); a(0xF5,'MOV A,!{abs}+X',3); a(0xF6,'MOV A,!{abs}+Y',3); a(0xE7,'MOV A,[{dp1}+X]',2); a(0xF7,'MOV A,[{dp1}]+Y',2)
a(0xCD,'MOV X,#{b1}',2); a(0xF8,'MOV X,{dp1}',2); a(0xF9,'MOV X,{dp1}+Y',2); a(0xE9,'MOV X,!{abs}',3)
a(0x8D,'MOV Y,#{b1}',2); a(0xEB,'MOV Y,{dp1}',2); a(0xFB,'MOV Y,{dp1}+X',2); a(0xEC,'MOV Y,!{abs}',3)
a(0xC6,'MOV (X),A',1); a(0xAF,'MOV (X)+,A',1); a(0xC4,'MOV {dp1},A',2); a(0xD4,'MOV {dp1}+X,A',2); a(0xC5,'MOV !{abs},A',3)
a(0xD5,'MOV !{abs}+X,A',3); a(0xD6,'MOV !{abs}+Y,A',3); a(0xC7,'MOV [{dp1}+X],A',2); a(0xD7,'MOV [{dp1}]+Y,A',2)
a(0xD8,'MOV {dp1},X',2); a(0xD9,'MOV {dp1}+Y,X',2); a(0xC9,'MOV !{abs},X',3)
a(0xCB,'MOV {dp1},Y',2); a(0xDB,'MOV {dp1}+X,Y',2); a(0xCC,'MOV !{abs},Y',3)
a(0x7D,'MOV A,X',1); a(0xDD,'MOV A,Y',1); a(0x5D,'MOV X,A',1); a(0xFD,'MOV Y,A',1); a(0x9D,'MOV X,SP',1); a(0xBD,'MOV SP,X',1)
a(0xFA,'MOV {dp2},{dp1}',3); a(0x8F,'MOV {dp2},#{b1}',3)
a(0xBC,'INC A',1); a(0x3D,'INC X',1); a(0xFC,'INC Y',1); a(0xAB,'INC {dp1}',2); a(0xBB,'INC {dp1}+X',2); a(0xAC,'INC !{abs}',3)
a(0x9C,'DEC A',1); a(0x1D,'DEC X',1); a(0xDC,'DEC Y',1); a(0x8B,'DEC {dp1}',2); a(0x9B,'DEC {dp1}+X',2); a(0x8C,'DEC !{abs}',3)
a(0x1C,'ASL A',1); a(0x0B,'ASL {dp1}',2); a(0x1B,'ASL {dp1}+X',2); a(0x0C,'ASL !{abs}',3)
a(0x5C,'LSR A',1); a(0x4B,'LSR {dp1}',2); a(0x5B,'LSR {dp1}+X',2); a(0x4C,'LSR !{abs}',3)
a(0x3C,'ROL A',1); a(0x2B,'ROL {dp1}',2); a(0x3B,'ROL {dp1}+X',2); a(0x2C,'ROL !{abs}',3)
a(0x7C,'ROR A',1); a(0x6B,'ROR {dp1}',2); a(0x7B,'ROR {dp1}+X',2); a(0x6C,'ROR !{abs}',3)
a(0x9F,'XCN A',1); a(0xBA,'MOVW YA,{dp1}',2); a(0xDA,'MOVW {dp1},YA',2); a(0x3A,'INCW {dp1}',2); a(0x1A,'DECW {dp1}',2)
a(0x7A,'ADDW YA,{dp1}',2); a(0x9A,'SUBW YA,{dp1}',2); a(0x5A,'CMPW YA,{dp1}',2)
a(0xCF,'MUL YA',1); a(0x9E,'DIV YA,X',1); a(0xDF,'DAA A',1); a(0xBE,'DAS A',1)
a(0x2D,'PUSH A',1); a(0x4D,'PUSH X',1); a(0x6D,'PUSH Y',1); a(0x0D,'PUSH PSW',1)
a(0xAE,'POP A',1); a(0xCE,'POP X',1); a(0xEE,'POP Y',1); a(0x8E,'POP PSW',1)
a(0x60,'CLRC',1); a(0x80,'SETC',1); a(0xED,'NOTC',1); a(0xE0,'CLRV',1); a(0x20,'CLRP',1); a(0x40,'SETP',1); a(0xA0,'EI',1); a(0xC0,'DI',1)
a(0x00,'NOP',1); a(0xEF,'SLEEP',1); a(0xFF,'STOP',1)
a(0x2F,'BRA {rel}',2); a(0xF0,'BEQ {rel}',2); a(0xD0,'BNE {rel}',2); a(0xB0,'BCS {rel}',2); a(0x90,'BCC {rel}',2)
a(0x70,'BVS {rel}',2); a(0x50,'BVC {rel}',2); a(0x30,'BMI {rel}',2); a(0x10,'BPL {rel}',2)
a(0x2E,'CBNE {dp1},{rel2}',3); a(0xDE,'CBNE {dp1}+X,{rel2}',3); a(0x6E,'DBNZ {dp1},{rel2}',3); a(0xFE,'DBNZ Y,{rel}',2)
a(0x5F,'JMP !{abs}',3); a(0x1F,'JMP [!{abs}+X]',3); a(0x3F,'CALL !{abs}',3); a(0x4F,'PCALL ${up}',2); a(0x6F,'RET',1); a(0x7F,'RETI',1); a(0x0F,'BRK',1)
a(0x2A,'OR1 C,/{mb}',3); a(0x0A,'OR1 C,{mb}',3); a(0x6A,'AND1 C,/{mb}',3); a(0x4A,'AND1 C,{mb}',3); a(0x8A,'EOR1 C,{mb}',3)
a(0xEA,'NOT1 {mb}',3); a(0xAA,'MOV1 C,{mb}',3); a(0xCA,'MOV1 {mb},C',3)
a(0x0E,'TSET1 !{abs}',3); a(0x4E,'TCLR1 !{abs}',3)
for i in range(16): a(0x01+i*16, 'TCALL %d' % i, 1)
for i in range(8):
    a(0x02+i*0x20, 'SET1 {dp1}.%d' % i, 2); a(0x12+i*0x20, 'CLR1 {dp1}.%d' % i, 2)
    a(0x03+i*0x20, 'BBS {dp1}.%d,{rel2}' % i, 3); a(0x13+i*0x20, 'BBC {dp1}.%d,{rel2}' % i, 3)
def dis(d, base, pc):
    op = d[pc-base]; fmt, n = T.get(op, ('.db $%02X' % op, 1))
    g = lambda k: d[pc-base+k] if pc-base+k < len(d) else 0
    r = lambda k: (g(k) ^ 0x80) - 0x80
    s = fmt.format(b1='$%02X'%g(1), b2='$%02X'%g(2), dp1='$%02X'%g(1), dp2='$%02X'%g(2), abs='$%04X'%(g(1)|g(2)<<8),
                   rel='$%04X'%((pc+2+r(1))&0xFFFF), rel2='$%04X'%((pc+3+r(2))&0xFFFF), up='%04X'%(0xFF00|g(1)),
                   mb='$%04X.%d'%((g(1)|g(2)<<8)&0x1FFF, (g(1)|g(2)<<8)>>13))
    return s, n, op
if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read(); base = int(sys.argv[2], 16); ents = [int(x, 16) for x in sys.argv[3:]] or [base]
    seen = {}; q = list(ents); labels = set(ents)
    while q:
        pc = q.pop()
        while base <= pc < base+len(d) and pc not in seen:
            s, n, op = dis(d, base, pc); seen[pc] = (s, n)
            import re
            m = re.search(r'\$([0-9A-F]{4})$', s)
            if m and (s.split()[0] in ('JMP','CALL') or s.split()[0].startswith('B') or s.split()[0] in ('CBNE','DBNZ')) and '[' not in s:
                t = int(m.group(1), 16); labels.add(t); q.append(t)
            if op in (0x6F, 0x7F, 0x5F, 0x2F, 0x1F, 0xFF): break
            pc += n
    pc = base; out = []
    while pc < base+len(d):
        if pc in seen:
            s, n = seen[pc]; out.append('%s%04X  %s' % ('L' if pc in labels else ' ', pc, s)); pc += n
        else:
            j = pc
            while j < base+len(d) and j not in seen: j += 1
            for k in range(pc, j, 16): out.append(' %04X  .db %s' % (k, ' '.join('%02X' % x for x in d[k-base:min(k+16, j)-base])))
            pc = j
    print('\n'.join(out))
