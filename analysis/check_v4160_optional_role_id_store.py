"""CLI: python SCRIPT APP V131 rasm2. Conditional reference/Xwchc, synthetic RAM,
separate task table and stack, successful accesses. Stop immediately after 53668.
"""
from pathlib import Path
import re,runpy

def check(ok,label):
    if not ok:raise ValueError(label)

def trace(code,n,cap):
    table=0x20004800;flag=0x2000319f;shared=0x200035f5;io=0x4002420c;sp=0x2000ff90
    pc=0x60864;r=dict(zero=0,sp=sp,s0=12,s1=13,s2=14);m={};writes=[];calls=[]
    def put(p,w,z):m.update({p+i:z>>(8*i)&255 for i in range(w)})
    def get(p,w):return sum(m[p+i]<<(8*i) for i in range(w))
    def val(k):return r[k] if k in r else int(k,0)
    def adr(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[b]+int(d))&0xffffffff
    put(flag,1,0);put(shared,1,11);put(0x2000319d,1,n);put(0x2000319e,1,cap);put(0x200031c4,4,table);put(io,4,17)
    for _ in range(5000):
        if pc==0x5366c:break
        at=pc;k,o,x=code[pc];pc+=k;t=x[0]
        if o in ('sw','sb','lw','lbu'):
            p=adr(x[1]);w=4 if o in ('sw','lw') else 1
            if o.startswith('s'):put(p,w,r[t]);writes.append((at,p,w,get(p,w)))
            else:r[t]=get(p,w)
        elif o in ('jal','jalr'):
            dest=val(x[-1]) if o=='jal' else adr(t);r['ra']=pc;pc=dest&~1;calls.append((pc,r['a0']))
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=val(t)
        elif o in ('bleu','beqz','bnez','bne'):
            z=0 if len(x)==2 else val(x[1]);y=r[t]
            if y<=z if o=='bleu' else y==z if o=='beqz' else y!=z:pc=val(x[-1])
        elif o!='fence.i':
            y=val(x[1]);z=val(x[2]) if len(x)>2 else 0
            if o in ('mv','li'):q=y
            elif o=='lui':q=y<<12
            elif o=='auipc':q=at+(y<<12)
            elif o in ('addi','add'):q=y+z
            elif o=='slli':q=y<<z
            else:raise ValueError((at,o))
            r[t]=q&0xffffffff
    result=n if n<cap else 255;buf=0x200033b8
    check(calls==[(0x43c4e,0x5352c),(0x5362e,result),(0x2000039c,buf),(0x55bd4,0),(0x55c48,0)],'handoffs')
    check([(p,w,z) for at,p,w,z in writes if at in (0x43c6a,0x43c72)]==([(0x2000319d,1,n+1),(table+4*n,4,0x5352c)] if n<cap else []),'registration stores')
    check([(p,w,z) for at,p,w,z in writes if at==0x200003c0]==[(buf+i,1,0) for i in range(296)],'fill')
    check([(p,w,z) for at,p,w,z in writes if at in (0x5364a,0x55bd8,0x55c4c,0x53668)]==[(0x200034e4,4,0),(0x200034e0,4,0),(0x200034e8,4,0),(flag,1,result)],'initialization stores')
    check(pc==0x5366c and get(shared,1)==11 and all(not p<=shared<p+w for _,p,w,_ in writes),'shared byte')

if __name__=='__main__':
    g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')));win=g['window'];b=g['b']
    for lo,hi in [(0x60864,0x60874),(0x43c4e,0x43c7e),(0x5362e,0x5366c),(0x55bd4,0x55bde),(0x55c48,0x55c52)]:win(b,0x40000,lo,hi)
    for n,cap in [(0,29),(11,29),(28,29),(29,29),(255,29),(254,255)]:trace(g['code'],n,cap)
    print('PASS: 6 optional registration traces, including ID 0 and rejection 255; 296 fill bytes each; shared ID untouched through 53668')
