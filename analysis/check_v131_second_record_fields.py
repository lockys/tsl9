"""Args: APP, V1.31 reference, rasm2. Conditional Xwchc; injected 0x4c05 return.
Stable count, disjoint synthetic RAM and MMIO. Stop at the next helper call.
"""
from pathlib import Path
import re, runpy

g = runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for lo,hi in [(0x4db60,0x4db88),(0x4dbdc,0x4dbf2)]:
    g['window'](g['b'],0x40000,lo,hi)
P=0x20007000; SLOT=0x20002f98; COUNT=0x20002fa0; IO=0x4002420c

def trace(n,ptr):
    mem={}; writes=[]; reads=[]
    def put(p,w,z): mem.update({p+i:(z>>(8*i))&255 for i in range(w)})
    def get(p,w): return sum(mem[p+i]<<(8*i) for i in range(w))
    r=dict(a0=ptr,s2=SLOT,s0=COUNT,s1=COUNT+1,zero=0); pc=0x4db60
    put(COUNT,1,n); put(COUNT+1,1,37); put(IO,4,17)
    for i in range(-1,16*n+1): put(P+i,1,0xa5)
    def val(x): return r[x] if x in r else int(x,0)
    def addr(x):
        off,reg=re.fullmatch(r'(-?\d+)\((\w+)\)',x).groups(); return (r[reg]+int(off))&0xffffffff
    for _ in range(25000):
        if pc==0x4efd8: break
        at=pc; w,op,x=g['code'][at]; pc+=w; t=x[0]
        if op in ('sb','sw','lbu','lw'):
            p=addr(x[1]); size=1 if op in ('sb','lbu') else 4
            if op in ('sb','sw'):
                z=r[t]&((1<<(size*8))-1); writes.append((p,size,z)); put(p,size,z)
            else: reads.append((p,size)); r[t]=get(p,size)
        elif op in ('bne','beqz','bnez'):
            take=(r[t]!=val(x[1]) if op=='bne' else r[t]==0 if op=='beqz' else r[t]!=0)
            if take: pc=val(x[-1])
        elif op in ('jal','jalr','j','ret'):
            dest=r['ra'] if op=='ret' else addr(t) if op=='jalr' else val(x[-1]);
            if op in ('jal','jalr'): r['ra']=pc
            pc=dest&~1
        elif op!='fence.i':
            a=val(x[1]); b=val(x[2]) if len(x)>2 else 0
            if op in ('lui','auipc'): z=(a<<12)+(at if op=='auipc' else 0)
            elif op=='li': z=a
            elif op in ('addi','add'): z=a+b
            elif op=='slli': z=a<<b
            elif op=='andi': z=a&b
            else: raise ValueError((at,op))
            r[t]=z&0xffffffff
    else: raise ValueError('step bound')
    expected=[(SLOT,4,ptr)]
    if ptr:
        expected += [(IO,4,0)]+[(P+i,1,0) for i in range(n*16)]+[(IO,4,17)]
        expected += [(P+16*i+9,1,255) for i in range(n)]
    else: expected += [(COUNT,1,0),(COUNT+1,1,0)]
    if writes!=expected or reads!=([(COUNT,1),(IO,4),(SLOT,4),(COUNT,1)] if ptr else []): raise ValueError('access order')
    rec=bytes(9)+b'\xff'+bytes(6) if ptr else bytes([0xa5])*16
    if bytes(mem[P+i] for i in range(-1,n*16+1))!=b'\xa5'+rec*n+b'\xa5' or r['ra']!=0x4db88: raise ValueError('layout or next call')

for n in (0,1,2,5,127,254,255):
    for ptr in (0,P): trace(n,ptr)
print('PASS: 7 null + 7 non-null returns, counts 0..255 sampled; 16-byte layout, ordered stores, guard bytes and next call')
