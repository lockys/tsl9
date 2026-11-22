"""APP, reference ROM, rasm2. Continuous synthetic RF trace; inner low-two-bit gate clear."""
from pathlib import Path
import re,runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
H=0x20002df2; S=0x2000ff60; IO=0x4002420c; T=0x40024200; B=0x40025000; X=0x40024100; M=0xffffffff
for lo,hi in [(0x641b0,0x64298),(0x63eda,0x63f02),(0x63f56,0x63f6a),(0x6645c,0x671aa),(0x662da,0x663a6),(H,H+54)]:
    g['window'](g['b'],0x40000 if lo!=H else 0x20000000-0x270,lo,hi)

def run(outer,inner,equal,wait):
    r={**{'s'+str(i):0x123400+i for i in range(12)},'sp':S,'ra':0x537b6,'zero':0}; start=r.copy();mem={};events=[];calls=[];pc=0x641b0;poll=0
    def put(p,n,v):mem.update({p+i:v>>(8*i)&255 for i in range(n)})
    def get(p,n):return sum(mem[p+i]<<(8*i) for i in range(n))
    for base in (B,T,X):
        for p in range(base,base+212,4):put(p,4,0)
    for p,v in [(0x20003504,0x40024300),(0x20003508,X),(0x2000353c,T),(0x20003590,B),(0x20003588,0x12345678 if equal else 0),(IO,outer)]:put(p,4,v)
    for p in (0x2000351b,0x20002fa6,0x20002fa7,0x20003594,0x20003595,0x20003584,0x2000358c):put(p,1,1)
    def val(x):return r[x] if x in r else int(x,0)
    def addr(x):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x).groups();return (int(d)+r[k])&M
    def signed(v):return (v^0x80000000)-0x80000000
    for _ in range(4000):
        if pc==start['ra']:break
        if pc==0x6632e:
            poll+=1
            if wait and poll==4:break
        at=pc;n,o,x=g['code'][pc];pc+=n;t=x[0]
        if o in ('lw','lbu','sw','sb'):
            p=addr(x[1]);w=4 if o.endswith('w') else 1
            if o.startswith('s'):put(p,w,r[t])
            elif at==0x63ee8 and p==IO:r[t]=inner # independent peripheral sample
            elif at==H+48 and p==T+100:r[t]=0 # helper timer expires
            elif at==0x6632e and p==T+100:r[t]=80 if wait else 0
            else:r[t]=get(p,w)
            if p==IO:events.append((at,o,r[t]))
        elif o in ('jal','jalr'):
            dest=val(x[-1]) if o=='jal' else addr(t)&~1;calls.append(dest);r['ra']=pc;pc=dest
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=val(t)
        elif o in ('beq','bne','beqz','bnez','bgez','bltz'):
            z=r[t];y=0 if o.endswith('z') else val(x[1]);take=z==y if o.startswith('beq') else z!=y if o.startswith('bne') else signed(z)>=0 if o=='bgez' else signed(z)<0
            if take:pc=val(x[-1]) if o in ('beq','bne') else val(x[-1])
        elif o not in ('nop','fence.i'):
            y=val(x[1]);z=val(x[2]) if len(x)>2 else 0
            if o=='li':v=y
            elif o in ('lui','auipc'):v=(y<<12)+(at if o=='auipc' else 0)
            elif o=='addi':v=y+z
            elif o in ('or','ori'):v=y|z
            elif o in ('and','andi'):v=y&z
            elif o=='sub':v=y-z
            elif o=='mul':v=y*z
            elif o=='div':a,b=map(signed,(y,z));v=-1 if not b else (abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
            elif o=='srli':v=y>>(z&31)
            elif o=='slli':v=y<<(z&31)
            else:raise ValueError((at,o))
            r[t]=v&M
    target=[0x63eda,0x6645c]+([] if equal else [H]*3)+[0x67198,0x662da]+([] if wait else [0x6636e])
    want=[(0x641ea,'lw',outer),(0x641ee,'sw',0),(0x63ee8,'lw',inner),(0x63eec,'sw',0),(0x63f5e,'sw',inner)]+([] if wait else [(0x64282,'sw',outer)])
    if calls!=target or events!=want or get(IO,4)!=(inner if wait else outer):raise ValueError('writeback trace')
    if wait and pc!=0x6632e or not wait and (pc!=start['ra'] or any(r[k]!=v for k,v in start.items())):raise ValueError('exit')

for pair in ((0x11223344,0xf00f),(0xffffffff,0),(0,0xffffffff)):
    for equal in (False,True):
        for wait in (False,True):run(*pair,equal,wait)
print('PASS: 6 continuous returns with original outer writeback; 6 bounded waits with only inner writeback')
