"""Args: APP, V1.31 carrier, rasm2. Conditional Xwchc/copied RAM; synthetic MMIO."""
from pathlib import Path
import runpy,re

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for lo,hi,base in [(0x6645c,0x67198,0x40000),(0x20002df2,0x20002e28,0x20000000-0x270)]:g['window'](g['b'],base,lo,hi)
code=g['code'];M=0xffffffff;B=0x40025000;T=0x40024200;S=0x2000ff40;ID=0x200035f5;H=0x20002df2

def need(ok):
    if not ok:raise ValueError('RF calibration trace mismatch')

def trace(equal,mode,initial,sample=0xabc104):
    r={'sp':S,'ra':0x6424a,'zero':0,**{'s'+str(i):0xabc100+i for i in range(12)}}; r['s4']=sample; orig=r.copy(); mem={}; ev=[];calls=[]; polls=0; pc=0x6645c
    def put(p,w,z):mem.update({p+i:(z>>(8*i))&255 for i in range(w)})
    def get(p,w):return sum(mem[p+i]<<(8*i) for i in range(w))
    def adr(s):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (r[k]+int(d))&M
    def sign(y):return (y^0x80000000)-0x80000000
    for p in range(B,B+212,4):put(p,4,p^0x55555555)
    put(0x20003590,4,B);put(0x2000353c,4,T);put(0x20003588,4,0x12345678 if equal else 0);put(ID,1,initial)
    for p in [0x20002fa6,0x20002fa7,0x20003594,0x20003595,0x20003584,0x2000358c]:put(p,1,9)
    for _ in range(2000):
        if pc==0x6424a:break
        if pc==H:calls.append(r['ra']);polls=0
        if pc==H+24:
            polls+=1
            if mode=='busy' and polls==4:break
        at=pc;w,o,x=code[pc];pc+=w;t=x[0]
        if o in ('sw','sb','lw','lbu'):
            p=adr(x[1]);n=4 if o in ('sw','lw') else 1
            if o in ('sw','sb'):put(p,n,r[t]);ev.append((at,p,n,r[t]))
            elif H<=at<0x20002e28 and p==B+144:r[t]=(3<<25) if mode=='bits' else 0
            elif H<=at<0x20002e28 and p==T+100:r[t]=0 if mode=='zero' else 6000
            else:r[t]=get(p,n)
        elif o in ('j','jalr','ret'):
            if o=='jalr':dest=adr(t)&~1;r['ra']=pc;pc=dest
            elif o=='ret':pc=r['ra']&~1
            else:pc=int(t,0)
        elif o in ('beq','bgez','bltz','bnez'):
            z=r[t];take=(z==r[x[1]]) if o=='beq' else (sign(z)>=0 if o=='bgez' else sign(z)<0 if o=='bltz' else z!=0)
            if take:pc=int(x[-1],0)
        else:
            v=lambda s:r[s] if s in r else int(s,0)
            y=v(x[1]);z=v(x[2]) if len(x)>2 else 0
            if o=='li':q=y
            elif o in ('lui','auipc'):q=(y<<12)+(at if o=='auipc' else 0)
            elif o=='addi':q=y+z
            elif o in ('or','ori'):q=y|z
            elif o in ('and','andi'):q=y&z
            elif o=='slli':q=y<<(z&31)
            elif o=='srli':q=y>>(z&31)
            elif o=='sub':q=y-z
            elif o=='mul':q=y*z
            elif o=='div':a,b=sign(y),sign(z);q=-1 if b==0 else (abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
            else:raise ValueError((at,o))
            if t!='zero':r[t]=q&M
    busy=not equal and mode=='busy';need(pc==(H+24 if busy else 0x6424a));need(calls==([] if equal else [0x66500] if busy else [0x66500,0x66542,0x6658e]))
    ram=[(p,n) for _,p,n,_ in ev if not (T+100==p and n==4 or B<=p and p+n<=B+212 or S-80<=p and p+n<=S)];need(ram==([(0x20003588,4)] if equal else [] if busy else [(p,1) for p in (0x20002fa6,0x20002fa7,0x20003595,0x2000358c,0x20003594,0x20003584)]))
    need(all(not p<=ID<p+n for _,p,n,_ in ev) and get(ID,1)==initial);need([v for at,p,n,v in ev if at==H+14]==[6000]*len(calls))
    # Inspect every actual store interval, including those using non-SP bases.
    slot=S-24
    need([(at,p,n,v) for at,p,n,v in ev if p<slot+4 and slot<p+n]==[(0x66470,slot,4,sample)])
    need(get(slot,4)==sample)
    need([(p,n,v) for at,p,n,v in ev if H<=at<0x20002e28]==[(T+100,4,6000)]*len(calls))
    if not busy:need(all(r[k]==v for k,v in orig.items()))

for initial in (0,11,255):
    for equal in (False,True):
        for mode in ('zero','bits','busy'):trace(equal,mode,initial)
print('PASS: 15 complete RF calibration traces and 3 bounded waits; shared ID untouched')
for sample in (0,0xf00f,0x11223344,0xffffffff):
    for equal in (False,True):
        for mode in ('zero','bits','busy'):trace(equal,mode,11,sample)
print('PASS: 20 returns and 4 bounded waits; sole overlapping store is the s4 spill, including nested-call writes')
