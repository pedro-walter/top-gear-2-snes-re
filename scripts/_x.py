import re,sys
sys.argv=['x']
exec(open('tools/portsyms.py').read().split("A, B = load")[0])
def mk(p):
    L=load(p); return L,[key(t) for _,t in L]
U=mk('disasm/tg2_usa.asm')
T={v:mk('disasm/tg2_%s.asm'%v) for v in('eur','jpn')}
names={0x00D84B:'ai_walker',0x00E541:'ai_handler_race',0x00D1D4:'ai_setup',0x08801C:'road_builder',0x1FD4B3:'password_validate',0x1FD74F:'password_checksum',0x008A41:'player_physics',0x1FCFB9:'password_end',0x1FD887:'mixed_radix_div',0x00CD09:'track_number',0x1F8F11:'car_next',0x1FABAA:'shop_buy' ,0x01E25B:'rng',0x00E417:'ai_handler_tbl'}
ia={a:i for i,(a,_) in enumerate(U[0])}
for a,n in names.items():
    row=[ '%06X'%a]
    i=ia.get(a)
    for v in('eur','jpn'):
        L,K=T[v]
        if i is None: row.append('?'); continue
        for N in (14,8,5):
            pat=K and U[1][i:i+N]
            m=[j for j in range(len(K)-N) if K[j:j+N]==pat]
            if len(m)==1: row.append('%06X'%L[m[0]][0]); break
        else: row.append('-')
    print(n,*row)
