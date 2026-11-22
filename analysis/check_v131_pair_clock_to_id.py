"""CLI: APP V131 rasm2. Begin after the six-byte copy, with synthetic saved caller frames.
Nominal registered clock chain, stable synthetic RTC, ordinary memory and no interference.
"""
from pathlib import Path
import re,runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
a,b,code,win=(g[k] for k in ('a','b','code','window'))
for lo,hi in [(0x53890,0x5397c),(0x43e8e,0x43ed2),(0x433a8,0x43414),(0x43520,0x4354a),(0x43d62,0x43de4),(0x6df1a,0x6e2ac),(0x60874,0x6089a),(0x58ef2,0x58f14),(0x5a00c,0x5a026),(0x6dd8e,0x6dd96)]:win(b,0x40000,lo,hi)
win(a,0x8000,0x191c6,0x19220)
M=0xffffffff;S=0x2000ff20;O=0x200033b8;ID=0x200035f5;IO=0x4002420c;RNG=0x20002ec8;ACC=0x200031b0;LAST=ACC+4
def ck(ok,msg):
    if not ok:raise ValueError(msg)
def signed(x):return (x^0x80000000)-0x80000000

def trace(shared,control):
    pc=0x53890;r=dict(sp=S,s0=O,s1=0x4000,zero=0,s2=2,s3=3,s4=4,s5=5);m={};writes=[];calls=[];draws=[]
    def put(p,n,v):m.update({p+i:v>>(i*8)&255 for i in range(n)})
    def get(p,n):return sum((b[p+i-0x40000] if 0x40000<=p+i<0x40000+len(b) else m[p+i])<<(8*i) for i in range(n))
    for p,n,z in [(ID,1,shared),(S+28,4,0x60874),(S+44,4,0x5a00c),(S+60,4,0x6dd8e),(O+232,6,0),(IO,4,17),(RNG,4,1),(ACC,4,7),(LAST,4,0),(0x20003210,4,0x43520),(0x20003230,4,0x43d62),(0x20003234,4,0x191c6),(0x2000323c,2,16000),(0x40002818,2,0),(0x4000281c,2,20)]:put(p,n,z)
    for j in (12,16,20,24):put(S+j,4,j)
    def v(k):return r[k] if k in r else int(k,0)
    def addr(k):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[k]+int(d))&M
    for _ in range(8000):
        if pc==0x6dd96:break
        at=pc;w,o,x=code[pc];pc+=w;t=x[0]
        if at==0x6dd92 and control:put(ID,1,shared^0x80)
        if o in ('sw','sb','sh','lw','lbu','lh','lhu'):
            p=addr(x[1]);n={'sw':4,'lw':4,'sb':1,'lbu':1,'lh':2,'sh':2,'lhu':2}[o]
            if o.startswith('s'):put(p,n,r[t]);writes.append((at,p,n,get(p,n)))
            else:
                z=get(p,n);r[t]=((z^32768)-32768)&M if o=='lh' else z
                if at==0x6dd92:ck((p,n)==(ID,1),'fresh ID source')
                if at==0x4340a:draws.append(z)
        elif o in ('jal','jalr'):
            dest=v(x[-1]);r['ra']=pc;pc=dest&~1;calls.append(pc)
        elif o in ('j','ret'):pc=(r['ra'] if o=='ret' else v(t))&~1
        elif o.startswith('b'):
            y=r[t];z=0 if len(x)==2 else v(x[1]);take={'beq':y==z,'beqz':y==0,'bne':y!=z,'bnez':y!=0,'bltu':y<z,'bleu':y<=z,'bltz':signed(y)<0,'bgez':signed(y)>=0}[o]
            if take:pc=v(x[-1])
        elif o!='fence.i':
            y=v(x[1]);z=v(x[2]) if len(x)>2 else 0
            if o in ('mv','li'):q=y
            elif o in ('auipc','lui'):q=(at if o=='auipc' else 0)+(y<<12)
            elif o in ('add','addi'):q=y+z
            elif o=='sub':q=y-z
            elif o=='mul':q=y*z
            elif o in ('mulhsu','mulhu'):q=((signed(y) if o=='mulhsu' else y)*z)>>32
            elif o in ('or','ori'):q=y|z
            elif o in ('and','andi'):q=y&z
            elif o in ('slli','sll'):q=y<<(z&31)
            elif o in ('srli','srl'):q=y>>(z&31)
            elif o=='srai':q=signed(y)>>(z&31)
            elif o=='divu':q=y//z if z else M
            elif o=='remu':q=y%z if z else y
            elif o=='sltu':q=int(y<z)
            else:raise ValueError((at,o))
            r[t]=q&M
    expected=[];state=1
    for _ in range(4):state=((state+9)*214013+2531011)&M;expected.append(state)
    ck(draws==expected and pc==0x6dd96 and r['a5']==(shared^(128 if control else 0)),'draws or ID')
    ck(all(calls.count(f)==4 for f in (0x433a8,0x43520,0x43d62,0x191c6,0x6df1a)),'clock chain')
    ck([(p,z) for _,p,n,z in writes if p in (ACC,LAST,IO)]==[(IO,0),(LAST,2),(ACC,9),(IO,17)]+[(IO,0),(ACC,9),(IO,17)]*3,'clock stores')
    ck(all(not p<=ID<p+n for _,p,n,_ in writes),'firmware store covers ID')
for shared in (0,11,255):
    for control in (False,True):trace(shared,control)
print('PASS: 3 nominal + 3 changed-ID controls; four complete clock-backed draws per path; fresh 6dd92 sample')
