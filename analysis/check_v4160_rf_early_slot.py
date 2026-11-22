"""Conditional startup zero versus later RF prefix: separate intervals, not a boot trace.
Args: decoded APP, V1.31 carrier, rasm2. Requires the reference startup HEX.
"""
import re, runpy
from pathlib import Path

here=Path(__file__).resolve().parent
slot=0x20003550

def need(ok,label):
    if not ok: raise ValueError(label)

startup=runpy.run_path(str(here.parent/'scripts/check-rf-3538-init.py'))
v=startup['verify'](startup['HEX'].read_bytes()); lo,hi=v['zero_range']
words=range(lo,hi,4)
need(len(words)==456 and words.index(slot)==406,'startup word index')
need(all(b<=slot or a>=slot+4 for a,b in v['copy_ranges']),'copy range')
need(v['missing_source']==[0x6eb2c,0x6eb30],'source gap before zero loop')

g=runpy.run_path(str(here/'check_v4160_geometry_chain.py'))
g['window'](g['b'],0x40000,0x64298,0x642fe)

def prefix(entry,prior,source):
    regs=dict(sp=entry,ra=0x537b6,zero=0); mem={}; writes=[]
    def put(p,n,z):
        for i in range(n):mem[p+i]=(z>>(8*i))&255
    def get(p,n):return int.from_bytes(bytes(mem[p+i] for i in range(n)),'little')
    put(slot,4,prior);put(0x200031ec,4,source);pc=0x64298
    while pc<0x642fc:
        n,op,args=g['code'][pc];pc+=n;d=args[0]
        if op in ('sb','sw','lw'):
            off,reg=re.fullmatch(r'(-?\d+)\((\w+)\)',args[1]).groups();p=(regs[reg]+int(off))&0xffffffff
            if op=='lw':regs[d]=get(p,4)
            else:
                w=1 if op=='sb' else 4;put(p,w,regs[d]);writes.append((p,w,get(p,w)))
        elif op=='li':regs[d]=int(args[1],0)
        elif op=='lui':regs[d]=int(args[1],0)<<12
        elif op=='addi':regs[d]=(regs[args[1]]+int(args[2],0))&0xffffffff
        else:raise ValueError(op)
    need(g['code'][pc][1:]==('jal',['0x6430e']),'stop before helper')
    need(writes==[(0x20003510,1,0),(0x2000350c,4,0),(0x20003504,4,0x40024300),(0x2000353c,4,0x40024200),(0x20003590,4,0x40025000),(0x20003508,4,0x40024100),(entry-4,4,0x537b6),(0x2000351b,1,1),(0x20003538,4,source),(0x20003534,4,(source+272)&0xffffffff)],'ordered writes')
    need(all(p+w<=slot or p>=slot+4 for p,w,_ in writes) and get(slot,4)==prior,'slot changed')

for sp in (0x2000ff60,0x2000ff90):
    for prior in (0,0x174ee,0x5ac3bd7e):
        for source in (0x2000418c,0xffffff00):prefix(sp,prior,source)
print('PASS: conditional zero store #407/456; 12 RF prefixes, 10 ordered stores each, callback word preserved')
