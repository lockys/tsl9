"""Args: APP, V1.31 reference, rasm2. Three slices, not continuous boot.
The APP config copy and preservation up to each consumer are assumed; Xwchc reference.
"""
from pathlib import Path
import re, runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for image,base,lo,hi in [('a',0x8000,0x19a54,0x19a74),('b',0x40000,0x4edd2,0x4edf6),('b',0x40000,0x4efd8,0x4efe0)]:
    g['window'](g[image],base,lo,hi)

def straight(lo,hi,r,m):
    events=[]
    while lo<hi:
        size,op,x=g['code'][lo]; at=lo; lo+=size
        def v(k): return r[k] if k in r else int(k,0)
        if op in ('sb','sh','sw','lbu'):
            d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',x[1]).groups(); p=(r[b]+int(d))&0xffffffff
            if op=='lbu': r[x[0]]=m[p]; events.append((at,'r',p,m[p])); continue
            for i in range({'sb':1,'sh':2,'sw':4}[op]):
                z=v(x[0])>>(8*i)&255; m[p+i]=z; events.append((at,'w',p+i,z))
        else:
            a=v(x[1]); b=v(x[2]) if len(x)>2 else 0
            if op=='lui': z=a<<12
            elif op=='li': z=a
            elif op in ('add','addi'): z=a+b
            elif op=='andi': z=a&b
            elif op=='srli': z=a>>b
            else: raise ValueError((at,op))
            r[x[0]]=z&0xffffffff
    return events

sp=0x2000ff60; m={}
straight(0x19a54,0x19a74,{'sp':sp},m)
source=m[sp+16+21]
if (m[sp+36],source)!=(63,14): raise ValueError('APP little-endian config halfword')
for c in range(256):
    # Directly seed the copied config byte. Poison both destinations before init.
    m={0x20003201:c,0x200033b4:0xa5,0x200033b5:0xa5}; r=dict(sp=sp,s0=8,ra=1,s1=9)
    events=straight(0x4edd2,0x4edf6,r,m)
    k=(c&3)+(c>>2)
    fields=[e for e in events if e[2] in (0x20003201,0x200033b4,0x200033b5)]
    if fields!=[(0x4edd6,'r',0x20003201,c),(0x4edec,'w',0x200033b5,c&3),(0x4edf4,'w',0x200033b4,k)]: raise ValueError(fields)
    r={}; getter=straight(0x4efd8,0x4efe0,r,m)
    if getter!=[(0x4efdc,'r',0x200033b4,k)] or r['a0']!=k: raise ValueError('getter')
    if c==source and (k,12*k)!=(5,60): raise ValueError('APP-conditioned request')
print('PASS: APP cfg[21]=14; 256 writer/getter pairs; conditional third request = 5 x 12 = 60 bytes')
