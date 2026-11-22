"""APP, V1.31 carrier, rasm2. Optional RF initialization skipped; shared synthetic RAM.
Stop at the second request, not after it. Xwchc mapping and successful memory accesses assumed.
"""
from pathlib import Path
import re, runpy

g = runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for l,h in [(0x6dd16,0x6dd2e),(0x61b1c,0x61b5a),(0x55bde,0x55c32),(0x43c4e,0x43c7e),(0x4da70,0x4db18),(0x4edd2,0x4ee72)]:
    g['window'](g['b'],0x40000,l,h)


def trace(seed,cfg,used,capacity):
    target=0x20003350; heap=0x200048a4; end=heap+8+capacity
    mem={}; samples=[]; alloc=[]; fills=[]
    def put(p,w,z): mem.update({p+i:z>>(8*i)&255 for i in range(w)})
    def get(p,w): return sum(mem[p+i]<<(8*i) for i in range(w))
    for p,w,z in [(target,1,seed),(0x2000319f,1,1),(0x2000319d,1,used),(0x2000319e,1,29),(0x200031c4,4,0x20004800),(0x20003201,1,cfg),(0x20003190,4,heap),(0x2000318c,4,end),(heap,4,end),(heap+4,2,capacity),(heap+6,2,0),(0x200031a2,2,4000),(0x4002420c,4,17)]: put(p,w,z)
    pc=0x6dd16; r=dict(zero=0,sp=0x2000ffc0,ra=0x8eb8,s0=0x40000,s1=11,s2=12,s3=13,s4=14)
    def v(k): return r[k] if k in r else int(k,0)
    def addr(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups(); return (r[b]+int(d))&0xffffffff
    for _ in range(8000):
        if pc==0x4db3e or (pc==0x20000040 and r['ra']==0x4db18): break
        if pc==0x20000040: alloc.append((r['a0'],r['a1'],r['ra']))
        if pc==0x2000039c: fills.append((r['a0'],r['a2']))
        at=pc; n,op,x=g['code'][at]; pc+=n; t=x[0]
        if op in ('sb','sh','sw','lw','lhu','lbu'):
            p=addr(x[1]); w={'sb':1,'sh':2,'sw':4,'lw':4,'lhu':2,'lbu':1}[op]
            if op.startswith('s'):
                if p<=target<p+w: raise ValueError(('count overwritten',hex(at)))
                put(p,w,r[t])
            else:
                r[t]=get(p,w)
                if at==0x4daf6: samples.append((p,w,r[t]))
        elif op in ('jal','jalr','jr','ret','j'):
            dest=(addr(t) if '(' in t else v(x[-1])) if op!='ret' else r['ra']
            if op in ('jal','jalr'): r['ra']=pc
            pc=dest&~1
        elif op in ('bne','bnez','beqz','bleu','bltu','blt'):
            a=r[t]; b=0 if len(x)==2 else v(x[1]); take={'bne':a!=b,'bnez':a!=0,'beqz':a==0,'bleu':a<=b,'bltu':a<b,'blt':(a^0x80000000)<(b^0x80000000)}[op]
            if take: pc=v(x[-1])
        elif op!='fence.i':
            a=v(x[1]); b=v(x[2]) if len(x)>2 else 0
            if op in ('li','mv'): z=a
            elif op in ('auipc','lui'): z=(at if op=='auipc' else 0)+(a<<12)
            elif op in ('add','addi'): z=a+b
            elif op=='sub': z=a-b
            elif op=='andi': z=a&b
            elif op=='slli': z=a<<(b&31)
            elif op=='srli': z=a>>(b&31)
            elif op=='mul': z=a*b
            else: raise ValueError((hex(at),op))
            r[t]=z&0xffffffff
    else: raise ValueError('step bound')
    if samples!=[(target,1,seed)] or pc!=(0x20000040 if seed else 0x4db3e): raise ValueError('live count branch')
    if seed and (r['a0'],r['a1'])!=(16*seed,0x4c04): raise ValueError('outer request')
    if alloc!=([(300,0x9001,0x4ee10)] if cfg else []): raise ValueError('inner allocator')
    if fills!=([(heap+8,300),(0x20003358,48)] if cfg else [])+[(0x20003320,48)]: raise ValueError('fills')
    if get(0x20003314,1)!=(used if used<29 else 255): raise ValueError('registration')

for seed in (0,1,5,255):
    for cfg in (0,14):
        for used in (5,29):
            for capacity in (300,312): trace(seed,cfg,used,capacity)
print('PASS: 32 continuous skip-role traces; 8 zero exits, 24 requests; count sampled once without intervening store')
