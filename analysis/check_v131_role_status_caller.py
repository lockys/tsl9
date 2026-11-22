"""APP, V1.31 reference, rasm2. Caller slice from 6dd2e to next nested call.
Only a0 varies between paired executions; this does not discard prior RAM effects.
Conditional Xwchc interpretation and disjoint synthetic RAM/stack; no device IO.
"""
from pathlib import Path
import re, runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for lo,hi in [(0x6dd2a,0x6dd3e),(0x43c4e,0x43c7e),(0x46570,0x4657a)]:
    g['window'](g['b'],0x40000,lo,hi)
code=g['code']; pc0=0x6dd2a
if code[pc0][0]!=4 or code[pc0][1]!='jal' or code[pc0][2]!=['ra','0x4da70']:raise ValueError('caller edge')
N=0x2000319d; T=0x20004800; S=0x2000ff80; handler=0x465b4

def trace(status,n,cap):
    r=dict(a0=status,sp=S,ra=pc0+4); m={}; path=[]; writes=[]
    def put(p,w,v):m.update({p+i:(v>>(8*i))&255 for i in range(w)})
    def get(p,w):return sum(m[p+i]<<(8*i) for i in range(w))
    def addr(s):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return r[b]+int(d)
    put(N,1,n);put(N+1,1,cap);put(0x200031c4,4,T)
    pc=pc0+4
    for _ in range(40):
        if pc==0x45220:break
        at=pc;path.append(at);w,op,x=code[at];pc+=w;t=x[0]
        if op=='jal':r['ra']=pc;pc=int(x[-1],0)
        elif op=='j':pc=int(t,0)
        elif op=='ret':pc=r['ra']&~1
        elif op=='bleu':
            if r[t]<=r[x[1]]:pc=int(x[-1],0)
        elif op in ('lw','lbu'):r[t]=get(addr(x[1]),4 if op=='lw' else 1)
        elif op in ('sb','sw'):
            p=addr(x[1]);width=1 if op=='sb' else 4;put(p,width,r[t]);writes.append((at,p,width,get(p,width)))
        elif op in ('li','lui','mv','add','addi','slli'):
            a=r[x[1]] if x[1] in r else int(x[1],0); b=(r[x[2]] if x[2] in r else int(x[2],0)) if len(x)>2 else 0
            r[t]=(a<<12 if op=='lui' else a<<b if op=='slli' else a+b)&0xffffffff
        else:raise ValueError((at,op))
        if pc==0x43c4e and r['a0']!=handler:raise ValueError('handler')
    value=n if n<cap else 255
    expected=[(0x43c6a,N,1,n+1),(0x43c72,T+4*n,4,handler)] if n<cap else []
    expected += [(0x46572,S-4,4,0x6dd3e),(0x46574,S-20,4,value)]
    if pc!=0x45220 or writes!=expected or (r['a0'],r['ra'])!=(value,0x4657a):raise ValueError((pc,writes))
    return path,writes,r,m

for n in (0,5,19,254,255):
    for cap in (0,6,19,29,255):
        if trace(0,n,cap)!=trace(19,n,cap):raise ValueError((n,cap))
print('PASS: 25 paired caller traces; prior 0/19 overwritten; next ID or 255 saved at entry SP-20')
