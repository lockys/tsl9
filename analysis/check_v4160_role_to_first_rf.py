"""First role entry to optional RF init or skip. APP, V1.31, rasm2. Synthetic stack/table/IO; Xwchc."""
from pathlib import Path
import re,runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for l,h in [(0x6dd16,0x6dd1e),(0x61b1c,0x61b5a),(0x55bde,0x55c32),(0x43c4e,0x43c7e),(0x5362e,0x537b6),(0x537cc,0x537d8),(0x55bd4,0x55bde),(0x55c48,0x55c52),(0x43e24,0x43e6a)]:g['window'](g['b'],0x40000,l,h)

def trace(flag,count,prior):
    m={};sp=0x2000ffc0;slot=0x20003550;obj=0x200033b8;table=0x20004800
    def put(p,w,v):m.update({p+i:v>>(8*i)&255 for i in range(w)})
    def get(p,w):return int.from_bytes(bytes(m[p+i] for i in range(w)),'little')
    for p,w,v in [(slot,4,prior),(0x2000319f,1,flag),(0x2000319d,1,count),(0x2000319e,1,29),(0x200031c4,4,table),(0x200031ec,4,0x2000418c),(0x200031f0,2,0x7000),(0x200031fa,1,3),(0x200031fc,2,27),(0x2000323e,2,31),(0x4002420c,4,17)]:put(p,w,v)
    pc=0x6dd16;r=dict(sp=sp,ra=0x8eb8,s0=0x40000,s1=11,s2=12,ra_unused=0,zero=0);stores=[];calls=[]
    def val(s):return r[s] if s in r else int(s,0)
    def addr(s):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (val(d)+r[k])&0xffffffff
    for _ in range(4000):
        if pc in (0x64298,0x6dd1e):break
        at=pc;n,o,x=g['code'][pc];pc+=n;t=x[0]
        if o in ('lw','sw','lbu','sb','lhu','sh'):
            p=addr(x[1]);w={'sw':4,'lw':4,'sb':1,'lbu':1,'sh':2,'lhu':2}[o]
            if o[0]=='s':put(p,w,r[t]);stores.append((at,p,w,get(p,w)))
            else:r[t]=get(p,w)
        elif o in ('jal','jalr'):
            target=val(x[-1]) if o=='jal' else addr(t)&~1;r['ra']=pc;pc=target;calls.append(pc)
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=val(t)
        elif o in ('bleu','bne','beqz','bnez'):
            a=r[t];b=0 if o.endswith('z') else val(x[1]);take=a<=b if o=='bleu' else a==b if o=='beqz' else a!=b
            if take:pc=val(x[-1])
        elif o!='fence.i':
            a=val(x[1]);b=val(x[2]) if len(x)>2 else 0
            if o in ('mv','li'):z=a
            elif o in ('lui','auipc'):z=(a<<12)+(at if o=='auipc' else 0)
            elif o in ('add','addi'):z=a+b
            elif o=='slli':z=a<<b
            elif o=='or':z=a|b
            elif o=='andi':z=a&b
            elif o=='srli':z=a>>b
            elif o=='sltiu':z=int(a<b)
            else:raise ValueError((at,o))
            r[t]=z&0xffffffff
    expected=[0x61b1c,0x55bde]+([] if flag else [0x43c4e,0x5362e,0x2000039c,0x55bd4,0x55c48,0x43e24,0x64298])
    if pc!=(0x6dd1e if flag else 0x64298) or calls!=expected:raise ValueError(('path',hex(pc),calls))
    fill=[(p,w,z) for at,p,w,z in stores if at==0x200003c0]
    if fill!=([] if flag else [(obj+i,1,0) for i in range(296)]):raise ValueError('bulk fill')
    if get(slot,4)!=prior or any(p<slot+4 and p+w>slot for _,p,w,_ in stores):raise ValueError('callback overlap')
    return len(stores)

for f in (0,1,255):
    for n in (5,29):
        for s in (0,0x174ee,0x5ac3bd7e):trace(f,n,s)
print('PASS: 6 paths to RF entry, 12 optional-init skips; 296-byte fill ends at 0x200034e0 exclusive; no modeled store touches callback word')
