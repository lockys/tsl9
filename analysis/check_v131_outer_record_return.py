"""Args: APP, V1.31 carrier, rasm2. Post-allocation caller and real reference fill.
Injected allocator return and live bytes, ordinary separated RAM, synthetic MMIO, Xwchc.
Stops before the next allocation, not a boot trace or an allocation-size proof.
"""
import re, runpy
from pathlib import Path

g = runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
g['window'](g['b'],0x40000,0x4db18,0x4db60)
C=0x20003350; P=0x20007000; IO=0x4002420c; SLOT=0x20003310; K=0x20002fa0

def trace(ok,count,neighbor,extra):
    r=dict(a0=P if ok else 0,s4=0x20003000,s3=K+3,s1=K+1,s0=K,zero=0)
    mem={}; stores=[]; loads=[]; pc=0x4db18
    def put(p,n,z): mem.update({p+i:(z>>(8*i))&255 for i in range(n)})
    def get(p,n): return sum(mem[p+i]<<(8*i) for i in range(n))
    for p,n,z in [(SLOT,4,0xaaaaaaaa),(C,1,count),(C+1,1,neighbor),(0x200033b4,1,extra),(K+1,1,0),(IO,4,17)]: put(p,n,z)
    def val(k): return r[k] if k in r else int(k,0)
    def addr(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups(); return (r[b]+int(d))&0xffffffff
    for _ in range(20000):
        if pc==0x20000040: break
        at=pc; n,op,x=g['code'][pc]; pc+=n; t=x[0]
        if op in ('sb','sw','lw','lbu'):
            p=addr(x[1]); w=4 if op in ('sw','lw') else 1
            if op.startswith('s'): stores.append((p,w,r[t])); put(p,w,r[t])
            else: loads.append((p,w)); r[t]=get(p,w)
        elif op in ('beqz','bnez','bne'):
            if (r[t]==0 if op=='beqz' else r[t]!=0 if op=='bnez' else r[t]!=r[x[1]]): pc=val(x[-1])
        elif op in ('jalr','j','ret'):
            dest=addr(t) if op=='jalr' else r['ra'] if op=='ret' else val(t)
            if op=='jalr': r['ra']=pc
            pc=dest&~1
        elif op!='fence.i':
            a=val(x[1]); b=val(x[2]) if len(x)>2 else 0
            if op=='li': z=a
            elif op in ('auipc','lui'): z=(a<<12)+(at if op=='auipc' else 0)
            elif op in ('add','addi'): z=a+b
            elif op=='slli': z=a<<b
            elif op=='andi': z=a&b
            else: raise ValueError((at,op))
            r[t]=z&0xffffffff
    else: raise ValueError('step bound')
    total=(extra+(neighbor if ok else 0))&255
    expected=[(SLOT,4,P if ok else 0)]
    if ok: expected += [(K+3,1,count),(K+1,1,neighbor),(IO,4,0)]+[(P+i,1,0) for i in range(16*count)]+[(IO,4,17)]
    if stores!=expected+[(K,1,total)] or loads!=([(C,1),(C+1,1),(IO,4)] if ok else [])+[(0x200033b4,1),(K+1,1)]: raise ValueError('access sequence')
    if (r['a0'],r['a1'],r['ra'])!=(16*total,0x4c05,0x4db60): raise ValueError('next request')

for ok in (False,True):
    for count in (0,1,5,255):
        for neighbor,extra in [(0,0),(3,7),(255,1),(255,255)]: trace(ok,count,neighbor,extra)
print('PASS: 16 null and 16 non-null returns; exact ordered accesses and next 0x4c05 request')
