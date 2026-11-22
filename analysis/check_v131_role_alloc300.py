"""Trace the 300-byte role allocation (args: reference carrier, rasm2).
Synthetic valid header chains, Xwchc RAM mapping, ordinary MMIO, null failure hook.
"""
from pathlib import Path
import re
import runpy

code = runpy.run_path(str(Path(__file__).with_name('check_v4160_alloc_fill_geometry.py')))['code']


def check(cap, skip):
    h, s, g, f = 0x200048a4, 0x2000ff70, 0x200031a2, 0x4002420c
    end, new = h+8+cap, h+308
    mem, writes = {}, []
    def put(p,w,v):
        for i in range(w): mem[p+i] = v>>(8*i)&255
    def get(p,w): return sum(mem[p+i]<<(8*i) for i in range(w))
    prior = h-32
    for p,w,v in [(0x20003190,4,prior if skip else h),(0x2000318c,4,end),(prior,4,h),(prior+4,2,24),(prior+6,2,1),(h,4,end),(h+4,2,cap),(h+6,2,0),(g,2,4000),(f,4,17),(0x20003220,4,0),(0x20003550,4,0x6789abcd)]: put(p,w,v)
    r = dict(zero=0,sp=s,s0=29,ra=0x4ee10,a0=300,a1=0x9001)
    pc = 0x20000040
    def val(k): return r[k] if k in r else int(k,0)
    for _ in range(120):
        if pc==0x4ee10: break
        size,op,x = code[pc]; pc+=size; t=x[0]
        if op in ('lw','sw','lhu','sh'):
            d,b = re.fullmatch(r'(-?\d+)\((\w+)\)',x[1]).groups(); p=(r[b]+int(d))&0xffffffff
            w=2 if op in ('lhu','sh') else 4
            if op.startswith('l'): r[t]=get(p,w)
            else: put(p,w,r[t]); writes.append((p,w,get(p,w)))
        elif op in ('lui','li','addi','add','sub','andi','slli','srli'):
            a=val(x[1]); b=val(x[2]) if len(x)>2 else 0
            if op=='lui': z=a<<12
            elif op=='sub': z=a-b
            elif op=='andi': z=a&b
            elif op=='slli': z=a<<b
            elif op=='srli': z=a>>b
            else: z=a+b
            r[t]=z&0xffffffff
        elif op=='ret': pc=r['ra']&~1
        elif op=='j': pc=val(t)
        elif op in ('bltu','bleu','bne','bnez','beqz'):
            a=r[t]; b=0 if op.endswith('z') else val(x[1]); take=a<b if op=='bltu' else a<=b if op=='bleu' else a==b if op=='beqz' else a!=b
            if take: pc=val(x[-1])
        elif op!='fence.i': raise ValueError(op)
    expected=[(s-8,4,29),(s-4,4,0x4ee10),(f,4,0)]
    if cap>308:
        expected += [(new+4,2,cap-308),(new,4,end),(new+6,2,0),(h,4,new),(h+4,2,300),(g,2,3992)]
    if cap>=300: expected += [(h+6,2,0x9001),(g,2,3692 if cap>308 else 3700)]
    expected += [(f,4,17)]
    if writes!=expected or pc!=0x4ee10 or (r['sp'],r['s0'],r['a0'])!=(s,29,h+8 if cap>=300 else 0): raise ValueError((cap,skip,writes))
    if any(p<0x20003554 and p+w>0x20003550 for p,w,_ in writes): raise ValueError('RF callback overlap')


for cap in (296,300,304,308,312,1024):
    for skip in (False,True): check(cap,skip)
print('PASS: 12 allocator returns; 2 null, 6 unsplit, 4 split; ordered stack/MMIO/heap writes checked')
