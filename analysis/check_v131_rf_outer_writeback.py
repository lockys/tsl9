"""APP, reference ROM, rasm2. Continuous synthetic RF trace; synthetic status, optional returning callback and timer."""
from pathlib import Path
import re,runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
H=0x20002df2; S=0x2000ff60; IO=0x4002420c; T=0x40024200; B=0x40025000; X=0x40024100; M=0xffffffff
for lo,hi in [(0x641b0,0x64298),(0x63e58,0x63fa0),(0x6645c,0x671aa),(0x662da,0x663a6),(H,H+54)]:
    g['window'](g['b'],0x40000 if lo!=H else 0x20000000-0x270,lo,hi)

def run(outer,inner,equal,wait,mask=0,state=1,after=None):
    r={**{'s'+str(i):0x123400+i for i in range(12)},'sp':S,'ra':0x537b6,'zero':0}; start=r.copy();mem={};events=[];calls=[];pc=0x641b0;poll=0
    def put(p,n,v):mem.update({p+i:v>>(8*i)&255 for i in range(n)})
    def get(p,n):return sum(mem[p+i]<<(8*i) for i in range(n))
    for base in (B,T,X):
        for p in range(base,base+212,4):put(p,4,0)
    for p,v in [(0x20003504,0x40024300),(0x20003508,X),(0x2000353c,T),(0x20003590,B),(0x20003588,0x12345678 if equal else 0),(IO,outer)]:put(p,4,v)
    for p in (0x2000351b,0x20002fa6,0x20002fa7,0x20003594,0x20003595,0x20003584,0x2000358c):put(p,1,1)
    record=0x20003514; stub=0x10000000
    put(T,4,mask);put(record+7,1,state);put(record+8,2,0);put(0x20003550,4,stub);put(0x2000350c,4,0)
    copies=[]
    def val(x):return r[x] if x in r else int(x,0)
    def addr(x):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x).groups();return (int(d)+r[k])&M
    def signed(v):return (v^0x80000000)-0x80000000
    for _ in range(4000):
        if pc==start['ra']:break
        if pc==stub: # synthetic normal return, not an identified implementation
            if tuple(r[k] for k in ('a0','a1','a2','ra'))!=(17,0,0,0x63f28):raise ValueError('callback arguments')
            if after is not None:put(record+7,1,after)
            pc=r['ra'];continue
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
            if at in (0x63f98,0x63f9c,0x63ed4):copies.append((at,p,r[t]&255))
        elif o in ('jal','jalr'):
            dest=val(x[-1]) if o=='jal' else (addr(t) if '(' in t else r[t])&~1;calls.append(dest);r['ra']=pc;pc=dest
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=val(t)
        elif o in ('beq','bne','beqz','bnez','bgez','bltz'):
            z=r[t];y=0 if o.endswith('z') else val(x[1]);take=z==y if o.startswith('beq') else z!=y if o.startswith('bne') else signed(z)>=0 if o=='bgez' else signed(z)<0
            if take:pc=val(x[-1])
        elif o not in ('nop','fence.i'):
            y=val(x[1]);z=val(x[2]) if len(x)>2 else 0
            if o in ('li','mv'):v=y
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
    active=bool(mask&3);callback=active and state==3
    live=after if callback and after is not None else state
    expected=([(0x63f98,record+8,live),(0x63f9c,record+9,1)] if active and live in (6,7,8) else [])+([(0x63ed4,record+7,0)] if active else [])
    if copies!=expected:raise ValueError(('state writes',copies,expected))
    target=[0x63eda]+([stub] if callback else [])+([0x63e58] if active else [])+[0x6645c]+([] if equal else [H]*3)+[0x67198,0x662da]+([] if wait else [0x6636e])
    want=[(0x641ea,'lw',outer),(0x641ee,'sw',0),(0x63ee8,'lw',inner),(0x63eec,'sw',0),(0x63f5e,'sw',inner)]+([] if wait else [(0x64282,'sw',outer)])
    if calls!=target or events!=want or get(IO,4)!=(inner if wait else outer):raise ValueError('writeback trace')
    if wait and pc!=0x6632e or not wait and (pc!=start['ra'] or any(r[k]!=v for k,v in start.items())):raise ValueError('exit')

for pair in ((0x11223344,0xf00f),(0xffffffff,0),(0,0xffffffff)):
    for equal in (False,True):
        for wait in (False,True):run(*pair,equal,wait)
for mask in (1,2,3):
    for state,after in ((1,None),(3,None),(3,8),(6,None),(7,None),(8,None)):
        for equal in (False,True):
            for wait in (False,True):run(0x11223344,0xf00f,equal,wait,mask,state,after)
print('PASS: 12 baseline and 72 nonzero-mask traces; callback arguments, state writes and ordered sample writebacks checked')
