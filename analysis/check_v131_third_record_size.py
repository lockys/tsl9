"""Args: APP, V1.31 reference, rasm2. Trace the 0x4c06 request to fill-call boundary.
Allocator result injected; separate ordinary RAM and stable count. No device execution.
"""
from pathlib import Path
import re, runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for lo,hi in [(0x4db84,0x4dbc2),(0x4efd8,0x4efe2)]:
    g['window'](g['b'],0x40000,lo,hi)
COUNT=0x200033b4; SLOT=0x20003318; P=0x20007000

def trace(n,ptr):
    pc=0x4db84; r={'zero':0}; events=[]; ram={COUNT:n}
    def val(x): return r[x] if x in r else int(x,0)
    def addr(x):
        off,base=re.fullmatch(r'(-?\d+)\((\w+)\)',x).groups(); return (val(base)+int(off))&0xffffffff
    for _ in range(80):
        if pc==0x20000040:
            events.append(('allocate',r['a0'],r['a1'],r['ra'])); r['a0']=ptr; pc=r['ra']; continue
        if pc==0x2000039c:
            events.append(('fill-call',r['a0'],r['a1'],r['a2'],r['ra'])); break
        if pc==0x4dbc2: break
        at=pc; w,op,x=g['code'][pc]; pc+=w; t=x[0]
        if op=='lbu':
            p=addr(x[1]); r[t]=ram[p]; events.append(('read',at,p,r[t]))
        elif op=='sw':
            p=addr(x[1]); ram.update({p+j:(r[t]>>(8*j))&255 for j in range(4)}); events.append(('store',at,p,r[t]))
        elif op in ('jal','jalr','ret'):
            dest=r['ra'] if op=='ret' else addr(t) if op=='jalr' else val(x[-1]);
            if op!='ret': r['ra']=pc
            pc=dest&~1
        elif op=='beqz':
            if not r[t]: pc=val(x[-1])
        else:
            a=val(x[1]); b=val(x[2]) if len(x)>2 else 0
            if op in ('li','mv'): z=a
            elif op=='mul': z=a*b
            elif op=='addi': z=a+b
            elif op in ('lui','auipc'): z=(a<<12)+(at if op=='auipc' else 0)
            elif op=='slli': z=a<<b
            elif op=='srli': z=a>>b
            else: raise ValueError((at,op))
            r[t]=z&0xffffffff
    else: raise ValueError('step limit')
    read=('read',0x4efdc,COUNT,n)
    want=[read,('allocate',12*n,0x4c06,0x4dba0),('store',0x4dba4,SLOT,ptr)]
    if ptr: want += [read,('fill-call',ptr,0,12*n,0x4dbc2)]
    if events!=want or pc!=(0x2000039c if ptr else 0x4dbc2): raise ValueError((n,ptr,events))

for count in range(256):
    for result in (0,P): trace(count,result)
print('PASS: 256 counts x 2 returns; request 0..3060 bytes; success reloads count before fill, null skips fill')
