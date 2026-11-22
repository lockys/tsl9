"""Offline APP 199e2 to 19a3a/19a08. Args: decoded APP, V1.31 carrier, rasm2.
Uses geometry checker for pinned image identities and candidate Xwchc instruction ledger.
Assumes mapped reference slots, successful accesses, synthetic peripheral samples and stack.
"""
from pathlib import Path
import re, runpy


def check(x):
    if not x: raise ValueError('preconfig trace mismatch')


def run(code,app,rom,delta,entry):
    m={}; F=entry-96; cfg=F+16; ctrl=0x4002420c; io=0x4002202c
    def put(p,n,v):
        for i in range(n): m[p+i]=v>>(8*i)&255
    def get(p,n): return sum(m[p+i]<<(8*i) for i in range(n))
    for i in range(96): put(F+i,1,0xa5)
    for off in (52,60,72): put(0x40000+off,4,int.from_bytes(rom[off:off+4],'little'))
    a=0x1ab1c; b=get(0x40034,4)
    check((b,get(0x4003c,4),get(0x40048,4))==(0x6e6a0,0x20000442,0x2000039c))
    for i in range(22):
        put(a+i,1,app[a+i-0x8000]); put(b+i,1,rom[b+i-0x40000]^int(i==delta))
    put(ctrl,4,0x13579bdf); put(0x20000008,4,0x12345678)
    samples=[0xaaaabbbb,0x11112222,0x44335566]; mm=[]; fill=[]; cmp=[]; args=[]; guards=[]
    r=dict(sp=entry,s0=0x12345,ra=0x8eac,gp=0x20004000,zero=0); pc=0x199e2
    for _ in range(1000):
        if pc in (0x19a08,0x19a3a): break
        if pc in (0x20000442,0x2000039c): args.append((pc,r['a0'],r['a1'],r['a2']))
        at=pc; n,op,x=code[pc]; pc+=n; t=x[0]
        def val(s): return r[s] if s in r else int(s,0)
        if op in ('lw','sw','lbu','sb'):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x[1]).groups(); p=(r[k]+int(d))&0xffffffff; w=4 if op.endswith('w') else 1
            if op[0]=='s':
                put(p,w,r[t]);
                if p==io: mm.append(r[t])
                if p==ctrl: guards.append(r[t])
                if at==0x200003c0: fill.append((p,r[t]))
            else:
                r[t]=samples[len(mm)] if p==io else get(p,w)
                if at in (0x20000474,0x20000478): cmp.append(p)
        elif op in ('addi','add','li','lui','auipc','and','or'):
            y=val(x[1]); r[t]=(y if op=='li' else y<<12 if op=='lui' else at+(y<<12) if op=='auipc' else y&val(x[2]) if op=='and' else y|val(x[2]) if op=='or' else y+val(x[2]))&0xffffffff
        elif op in ('beq','bne','beqz','bnez'):
            y=0 if op.endswith('z') else val(x[1]);
            if (r[t]==y)==op.startswith('beq'): pc=val(x[-1])
        elif op=='jalr': target=r[t]&~1; r['ra']=pc; pc=target
        elif op=='ret': pc=r['ra']&~1
        elif op=='j': pc=val(t)
        elif op!='fence.i': raise ValueError((at,op))
    success=delta is None; size=21 if success else delta+1
    check(cmp==[p+i for i in range(size) for p in (b,a)])
    check(args==[(0x20000442,b,a,21)]+([(0x2000039c,cfg,0,64)] if success else []))
    check(guards==[0,0x13579bdf]*(2 if success else 1))
    check(mm==([samples[0]&0x8fffffff,samples[1]|0x30000000,samples[2]|0x03000000] if success else []))
    check(fill==([(cfg+i,0) for i in range(64)] if success else []))
    check(get(cfg,64)==(0 if success else int.from_bytes(b'\xa5'*64,'little')))
    check((pc,r['sp'],r['s0'],get(F+88,4),get(F+92,4),get(r['gp']+384,4))==
          ((0x19a3a if success else 0x19a08),F,0x40000,0x12345,0x8eac,0x12345678))


if __name__=='__main__':
    base=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
    app,rom,win=base['a'],base['b'],base['window']; win(app,0x8000,0x199e2,0x19a3a)
    win(rom,0x20000000-0x270,0x20000442,0x2000048a)
    for entry in (0x2000ffc0,0x2000ffd0):
        for delta in (None,*range(21)): run(base['code'],app,rom,delta,entry)
    print('PASS: 2 reference matches -> 64 zero stores each; 42 single-byte mismatch controls -> no config stores')
