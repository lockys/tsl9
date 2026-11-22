"""After the optional initializer skip: args APP, V1.31 carrier, rasm2. Synthetic RAM, conditional Xwchc."""
from pathlib import Path
import re
import runpy

g = runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for lo, hi in [(0x6dd1e,0x6dd2e),(0x43c4e,0x43c7e),(0x4da70,0x4dad2),(0x4edd2,0x4ee10)]:
    g['window'](g['b'],0x40000,lo,hi)


def trace(c, n):
    sp, table, slot = 0x2000ffb0, 0x20004800, 0x20003550
    mem, writes = {}, []
    def put(p,w,v):
        for i in range(w): mem[p+i] = v>>(8*i)&255
    def get(p,w): return sum(mem[p+i]<<(8*i) for i in range(w))
    for p,w,v in [(slot,4,0x76543210),(0x2000319d,1,n),(0x2000319e,1,29),(0x200031c4,4,table),(0x20003201,1,c)]: put(p,w,v)
    r = dict(zero=0,sp=sp,ra=0x8eb8,**{'s'+str(i):i for i in range(5)})
    def val(x): return r[x] if x in r else int(x,0)
    def addr(x):
        d,b = re.fullmatch(r'(-?\d+)\((\w+)\)',x).groups()
        return (int(d)+r[b])&0xffffffff
    pc = 0x6dd1e
    for _ in range(120):
        if pc in (0x4ee68,0x20000040): break
        at = pc; size,op,x = g['code'][pc]; pc += size; t = x[0]
        if op in ('sb','sw','sh','lbu','lw'):
            w = {'sb':1,'sw':4,'sh':2,'lbu':1,'lw':4}[op]; p = addr(x[1])
            if op.startswith('s'): put(p,w,r[t]); writes.append((p,w,r[t]&((1<<(8*w))-1)))
            else: r[t] = get(p,w)
        elif op == 'jal': r['ra'],pc = pc,val(x[-1])
        elif op == 'jalr': r['ra'],pc = pc,addr(t)&~1
        elif op == 'ret': pc = r['ra']&~1
        elif op == 'j': pc = val(t)
        elif op == 'bleu':
            if r[t]<=val(x[1]): pc = val(x[-1])
        elif op == 'beqz':
            if not r[t]: pc = val(x[-1])
        else:
            a = val(x[1]); b = val(x[2]) if len(x)>2 else 0
            if op in ('mv','li'): z=a
            elif op in ('lui','auipc'): z=(a<<12)+(at if op=='auipc' else 0)
            elif op in ('add','addi'): z=a+b
            elif op=='slli': z=a<<b
            elif op=='srli': z=a>>b
            elif op=='andi': z=a&b
            elif op=='mul': z=a*b
            else: raise ValueError((at,op))
            r[t]=z&0xffffffff
    k = (c&3)+(c>>2)
    if pc!=(0x20000040 if k else 0x4ee68) or (k and (r['a0'],r['a1'])!=(60*k,0x9001)): raise ValueError('allocator boundary')
    if get(sp-36,4)!=(n if n<29 else 255) or get(0x2000319d,1)!=n+int(n<29): raise ValueError('saved registration result')
    if n<29 and get(table+4*n,4)!=0x4dbf2: raise ValueError('handler')
    if get(0x200033b5,1)!=(c&3) or get(0x200033b4,1)!=k: raise ValueError('split fields')
    if len(writes)!=21+2*int(n<29) or any(p<slot+4 and slot<p+w for p,w,_ in writes): raise ValueError('write footprint')
    if get(slot,4)!=0x76543210: raise ValueError('callback word')


for c in range(256):
    for n in (5,29): trace(c,n)
print('PASS: 512 skip-prefix traces; 510 allocator entries, 2 zero-count branches; no store overlaps RF callback slot')
