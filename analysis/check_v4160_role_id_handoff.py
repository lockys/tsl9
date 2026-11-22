"""APP V131 rasm2. Two roles share one RAM. Six consumer calls, prefix and
first role's post-registration helpers are opaque normal returns. Flag at 319f
is nonzero, so the second role does not take its optional initializer here.
"""
from pathlib import Path
import re,runpy
g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
w=g['window'];b=g['b'];w(g['a'],32768,0x8eb8,0x8ebe)
for lo,hi in [(0x6dd16,0x6dd86),(0x6d572,0x6d682),(0x43c4e,0x43c7e),(0x6dd86,0x6dda4),(0x5a004,0x5a026),(0x60856,0x6089a),(0x58ef2,0x58f14)]:w(b,0x40000,lo,hi)
ID=0x200035f5;N=0x2000319d;T=0x20004800;M=0xffffffff
OPAQUE={0x61b1c,0x4da70,0x46570,0x4a7d6,0x50412,0x6c300,0x4d172,0x4600e,0x2000039c,0x440c2,0x20000332}
def ck(ok,msg):
    if not ok:raise ValueError(msg)
def trace(n,cap,cfg):
    m={};r=dict(sp=0x2000ffc0,s0=0x40000,s1=11,s2=12,ra=0x8eb8,zero=0);pc=0x6dd16;ids=[];handlers=[];status=[];writes=[];sample=[]
    def put(p,k,v):m.update({p+i:v>>(8*i)&255 for i in range(k)})
    def get(p,k):return sum(m[p+i]<<(8*i) for i in range(k))
    def v(s):return r[s] if s in r else int(s,0)
    def addr(s):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (r[k]+int(d))&M
    for p,k,z in [(N,1,n),(N+1,1,cap),(0x200031c4,4,T),(ID,1,255),(0x20003201,1,cfg),(0x2000319f,1,1)]:put(p,k,z)
    for _ in range(700):
        if pc in (0x6dda4,0x6de04):break
        if pc in OPAQUE:r['a0']=0;pc=r['ra'];continue
        if pc==0x43c4e:handlers.append(r['a0'])
        if pc==0x8eb8:status.append(r['a0'])
        at=pc;k,o,x=g['code'][pc];pc+=k;t=x[0]
        if o in ('lw','lbu','sw','sb'):
            p=addr(x[1]);nbyte=4 if o in ('sw','lw') else 1
            if o.startswith('s'):
                put(p,nbyte,r[t]);writes.append((at,p,nbyte,get(p,nbyte)))
                if p==ID:ids.append((at,r[t]&255))
            else:
                r[t]=int.from_bytes(b[p-0x40000:p-0x40000+nbyte],'little') if 0x40000<=p<0x40000+len(b) else get(p,nbyte)
                if at==0x6dd92:sample.append((p,r[t]))
        elif o in ('jal','jalr'):
            dest=addr(t) if '(' in t else v(x[-1]);r['ra']=pc;pc=dest&~1
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=v(t)
        elif o.startswith('b'):
            z=0 if len(x)==2 else v(x[1]);y=r[t]
            if {'bleu':y<=z,'bnez':y!=0,'bne':y!=z,'beq':y==z}[o]:pc=v(x[-1])
        else:
            y=v(x[1]);z=v(x[2]) if len(x)>2 else 0
            if o in ('mv','li'):q=y
            elif o in ('auipc','lui'):q=(at if o=='auipc' else 0)+(y<<12)
            elif o in ('add','addi'):q=y+z
            elif o=='andi':q=y&z
            elif o=='slli':q=y<<z
            else:raise ValueError((at,o))
            r[t]=q&M
    hs=[0x4dbf2,0x465b4,0x4a808,0x502b4,0x6cc4c,0x4d1b0]+([0x6d26c] if cfg&3 else [])
    slots=min(len(hs),max(0,cap-n));result=n+6 if cfg&3 and n+6<cap else 255
    ck(handlers==hs and get(N,1)==n+slots,'count or handler')
    ck([(p,z) for at,p,k,z in writes if at==0x43c72]==[(T+4*(n+i),h) for i,h in enumerate(hs[:slots])],'task table')
    ck(ids==([(0x6d5b6,result)] if cfg&3 else []) and sample==[(ID,result)],'ID store/load')
    ck(status==[24 if result==255 else 0] and pc==(0x6dda4 if result==255 else 0x6de04),'status or branch')
    return result
for n,cap,cfg in [(5,29,1),(6,29,1),(5,11,1),(5,29,0),(11,11,1),(248,255,3)]:print(n,cap,cfg,'=>',trace(n,cap,cfg))
print('PASS: six shared-RAM registration-to-read paths, including shifted count, gate closed and full table')
