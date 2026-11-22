"""V1.31 role record init. Args: v4.1.60 APP, V1.31 carrier, rasm2.
Xwchc, modeled MMIO, stable count and separated objects. Null stops after first fill.
"""
from pathlib import Path
import re
import runpy

g = runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
g['window'](g['b'], 0x40000, 0x4ee10, 0x4ee68)
g['window'](g['b'], 0x40000, 0x4dad2, 0x4db18)


def trace(payload, count, outer=None, task=5):
    base, ptr, fixed, sp, io = 0x200033ac, 0x20003354, 0x20003358, 0x2000ff70, 0x4002420c
    mem, writes = {}, []
    def put(p,w,v):
        for i in range(w): mem[p+i] = (v>>(8*i))&255
    def get(p,w): return sum(mem[p+i]<<(8*i) for i in range(w))
    for p,w,v in [(base+8,1,count),(sp+8,4,0x20003000),(sp+12,4,0x4dad2),(sp+4,4,0x20003000),(sp+28,4,task),(io,4,17)]: put(p,w,v)
    if payload: mem.update(dict.fromkeys(range(payload,payload+60*count),0xa5))
    mem.update(dict.fromkeys(range(fixed,fixed+48),0xa5))
    if outer is not None: put(0x20003350,1,outer)
    r = dict(zero=0,sp=sp,s0=base,s1=0x20003000,s2=0x20003000,a0=payload)
    def val(k): return r[k] if k in r else int(k,0)
    def addr(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups(); return (r[b]+int(d))&0xffffffff
    pc=0x4ee10; stop=0x4dad2 if payload else 0x4ee28
    if outer is not None: stop=0x20000040 if outer else 0x4db3e
    samples=[]
    for _ in range(10000):
        if pc==stop: break
        here=pc; n,op,x=g['code'][pc]; pc+=n; t=x[0]
        if op in ('lw','lbu','sw','sh','sb'):
            p=addr(x[1]); w={'lw':4,'lbu':1,'sw':4,'sh':2,'sb':1}[op]
            if op.startswith('l'):
                r[t]=get(p,w)
                if here in (0x4dad2,0x4daf6): samples.append((here,p,w,r[t],len(writes)))
            else: put(p,w,r[t]); writes.append((p,w,get(p,w)))
        elif op in ('li','lui','auipc','addi','add','mul','slli'):
            a=val(x[1]); b=val(x[2]) if len(x)>2 else 0
            if op in ('auipc','lui'): z=(here if op=='auipc' else 0)+(a<<12)
            elif op=='mul': z=a*b
            elif op=='slli': z=a<<b
            else: z=a+b
            r[t]=z&0xffffffff
        elif op=='jalr': r['ra'],pc=pc,addr(t)&~1
        elif op=='jr': pc=addr(t)&~1
        elif op=='ret': pc=r['ra']&~1
        elif op=='j': pc=val(t)
        elif op in ('beqz','bnez','bne','blt'):
            a=r[t]; b=0 if op.endswith('z') else val(x[1]); take=(a==b if op=='beqz' else (a^0x80000000)<(b^0x80000000) if op=='blt' else a!=b)
            if take: pc=val(x[-1])
        elif op!='fence.i': raise ValueError((here,op))
    expected=[(ptr,4,payload),(io,4,0)]
    if payload: expected += [(payload+i,1,0) for i in range(60*count)]
    expected += [(io,4,17)]
    if payload:
        for i in range(count):
            p=payload+60*i; expected += [(p+2,2,65535),(p+4,1,0),(p+44,4,0)]
        expected += [(io,4,0)]+[(fixed+i,1,0) for i in range(48)]+[(io,4,17)]
        record=bytes(2)+b'\xff\xff'+bytes(56)
        if bytes(mem[payload+i] for i in range(60*count))!=record*count: raise ValueError('record layout')
    if outer is not None:
        before=len(expected)
        expected += [(0x20003314,1,task&255),(io,4,0)]+[(0x20003320+i,1,0) for i in range(48)]+[(io,4,17)]
        if samples!=[(0x4dad2,sp+28,4,task,before),(0x4daf6,0x20003350,1,outer,len(expected))]: raise ValueError('outer reads')
        if outer and (r['a0'],r['a1'],r['ra'])!=(16*outer,0x4c04,0x4db18): raise ValueError('outer request')
    if pc!=stop or writes!=expected: raise ValueError(('write trace',hex(pc),count))


for p in (0x200048ac,0x20004aac):
    for k in (1,5,8): trace(p,k)
trace(0,5)
for outer in (0,1,5,255):
    for task in (5,255): trace(0x200048ac,5,outer,task)
print('PASS: 8 continuous 300-byte paths through outer count sample; 2 skips, 6 allocator requests')
print('PASS: 6 successful record initializers through return; 1 null case through first fill only')
