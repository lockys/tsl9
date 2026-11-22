"""Args: APP, V1.31 reference, rasm2. Fork at first missing RF read; NOT continuous to the allocation call."""
from pathlib import Path
import runpy,sys
base=Path(__file__).with_name('check_v4160_inherited_role_prefix.py')
rows=[]
def ck(x):
    if not x:raise ValueError('inherited header or allocation mismatch')
def fork(m,code,sp):
    def get(p,w):return int.from_bytes(bytes(m[p+i] for i in range(w)),'little')
    def put(p,w,v):m.update({p+i:v>>(8*i)&255 for i in range(w)})
    r=dict(sp=sp,ra=0x4ee10,s0=123,zero=0,a0=300,a1=0x9001);pc=0x20000040;reads=[];headers=[]
    def val(s):return r[s] if s in r else int(s,0)
    for _ in range(140):
        if pc==0x4ee10:break
        at=pc;n,o,x=code[pc];pc+=n;t=x[0]
        if o in ('lw','lhu','sw','sh'):
            d,k=x[1][:-1].split('(');p=(r[k]+int(d))&0xffffffff;w=2 if o in ('sh','lhu') else 4
            if o.startswith('s'):put(p,w,r[t])
            else:
                r[t]=get(p,w)
                if at in (0x200000a8,0x2000010c,0x200000ca):reads.append((at,p,r[t]))
                if at==0x200000ae:headers.append((p-6,r[t]))
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=val(t)
        elif o in ('bltu','bleu','beqz','bnez','bne'):
            a=r[t];b=0 if len(x)==2 else val(x[1]);take={'bltu':a<b,'bleu':a<=b,'beqz':a==0,'bnez':a!=0,'bne':a!=b}[o]
            if take:pc=val(x[-1])
        elif o!='fence.i':
            a=val(x[1]);b=val(x[2]) if len(x)>2 else 0
            if o=='lui':z=a<<12
            elif o in ('addi','add','li'):z=a+b
            elif o=='sub':z=a-b
            elif o=='andi':z=a&b
            elif o=='slli':z=a<<b
            elif o=='srli':z=a>>b
            else:raise ValueError(o)
            r[t]=z&0xffffffff
    h=0x200048a4;p=h+8;end=0x2000b184
    ck(reads==[(0x200000a8,0x20003190,0x200045ac),(0x2000010c,0x200045ac,h),(0x200000ca,h,end)])
    ck(headers==[(0x200045ac,1),(h,0)] and pc==0x4ee10 and r['a0']==p and r['sp']==sp)
    ck(get(h,4)==h+308 and get(h+4,2)==300 and get(h+6,2)==0x9001 and get(h+308,4)==end)
    ck(0x20003351<0x2000418c<=p<p+300<=0x2000b18c)

prefix=runpy.run_path(str(base.resolve()));s=prefix['s'];code=s['code']
for entry,clock in [(0x2000ffc0,0x101),(0x2000ffd0,0x5555)]:
    for equal in (False,True):
        pc,r,m=s['base']['run'](code,s['a'],s['b'],bytes(range(6)),equal,entry,clock,outer=True)
        s['base']['calibrate'](code,pc,r,m)
        for control in (False,True):
            rr,mm=r.copy(),m.copy();s['mod']['follow'](code,s['b'],rr,mm,control);s['ns']['advance'](code,s['b'],rr,mm,control)
            ck(s['target'](code,s['b'],rr)==(0x401a0,0x6dd16) and prefix['follow'](rr,mm)==(0x660e8,0x40025048,4))
            fork(mm.copy(),code,rr['sp'])
print('PASS: 8 snapshot forks: 0x200045ac busy -> 0x200048a4 free -> split; P=0x200048ac, 300 bytes inside APP pool; intervening RF path not executed')
