"""APP, V1.31 carrier, rasm2. Xwchc reference path; four calls are opaque
normal returns preserving SP and RAM, except for the explicit reload control.
This checks consumers of the ID, not whether the callees preserve its stack slot.
"""
from pathlib import Path
import re, runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for lo,hi in [(0x46570,0x465b4),(0x4d9ec,0x4da18)]:g['window'](g['b'],0x40000,lo,hi)
S=0x2000ff80; M=0xffffffff

def trace(task,change=None):
    m={}; r={'a0':task,'ra':0x6dd3e,'sp':S,'zero':0}; pc=0x46570; calls=[]; writes=[]; loads=[]
    def put(p,w,z):m.update({p+i:(z>>(8*i))&255 for i in range(w)})
    def get(p,w):return sum(m[p+i]<<(8*i) for i in range(w))
    def v(k):return r[k] if k in r else int(k,0)
    def addr(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[b]+int(d))&M
    for _ in range(80):
        if pc==0x6dd3e:break
        if pc in (0x45220,0x48c56,0x47eac,0x6d682):
            calls.append(pc);r['a0']=0xdead0000+len(calls)
            if pc==0x6d682 and change is not None:put(S-20,4,change)
            pc=r['ra'];continue
        at=pc;n,op,x=g['code'][pc];pc+=n;t=x[0]
        if op in ('sw','sh','sb'):
            p=addr(x[1]);w={'sw':4,'sh':2,'sb':1}[op];put(p,w,r[t]);writes.append((at,p,w,get(p,w)))
        elif op=='lw':
            p=addr(x[1]);r[t]=get(p,4);loads.append((at,p,r[t]))
        elif op in ('jal','j','ret'):
            dest=r['ra'] if op=='ret' else v(x[-1]);
            if op=='jal':r['ra']=pc
            pc=dest&~1
        elif op=='bltu':
            if r[t]<v(x[1]):pc=v(x[-1])
        else:
            a=v(x[1]);b=v(x[2]) if len(x)>2 else 0
            if op in ('add','addi','li'):z=a+b
            elif op=='mul':z=a*b
            elif op=='lui':z=a<<12
            elif op=='slli':z=a<<b
            elif op=='srli':z=a>>b
            else:raise ValueError((at,op))
            r[t]=z&M
    live=task if change is None else change
    expected=[(0x46572,S-4,4,0x6dd3e),(0x46574,S-20,4,task),(0x46592,0x2000324a,2,0xff00),(0x46594,0x2000324c,1,0),(0x465a4,0x200033ae,1,255),(0x465a8,0x200033ac,1,live&255),(0x4da0c,0x2000332e,1,live&255),(0x4da0e,0x2000332c,2,5)]
    if calls!=[0x45220,0x48c56,0x47eac,0x6d682] or loads!=[(0x4659c,S-20,live),(0x465a6,S-4,0x6dd3e)]:raise ValueError('calls/reloads')
    if writes!=expected or (pc,r['sp'],r['a0'])!=(0x6dd3e,S,0):raise ValueError((writes,pc))

for task in range(256):trace(task)
trace(255,0x12345678)
print('PASS: 256 IDs and 1 changed-stack control; two ID-byte stores, selector 5, return 0')
