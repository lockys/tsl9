"""Late binding only: APP, V1.31 reference, rasm2. Synthetic stack/IO; no device."""
from pathlib import Path
import re,runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
g['window'](g['a'],0x8000,0x17644,0x1765c)
g['window'](g['b'],0x40000,0x64bae,0x64bf6)

def trace(flags,aux,pc=0x17644):
    sp=0x2000ff30; dst=0x20003540; io=0x4002420c; mask=0xffffffff
    src=bytes((i*13+7)&255 for i in range(32));m={};log=[];calls=[]
    def put(p,n,v):m.update({p+i:(v>>(8*i))&255 for i in range(n)})
    def get(p,n):return int.from_bytes(bytes(m[p+i] for i in range(n)),'little')
    for i,v in enumerate(src):put(sp+i,1,v);put(dst+i,1,0xa5)
    put(sp,1,flags);put(sp+4,4,aux);put(sp+16,4,0);put(io,4,0x12340201)
    put(0x401c4,4,int.from_bytes(g['b'][0x1c4:0x1c8],'little'))
    r=dict(sp=sp,s0=0x40000,s1=1,s2=2,ra=3,zero=0,a0=sp);late=pc==0x17644
    def v(k):return r[k] if k in r else int(k,0)
    def adr(s):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (v(d)+v(k))&mask
    for _ in range(1000):
        if pc in (0x64ce8,0x64c84,0x64bf6):break
        at=pc;n,o,x=g['code'][pc];pc+=n;t=x[0]
        if o in ('sw','sb','lw','lbu'):
            p=adr(x[1]);w=4 if o.endswith('w') else 1
            if o.startswith('s'):put(p,w,v(t))
            else:r[t]=get(p,w)
            if dst<=p<dst+32 or at==0x20000358:log.append((at,p,get(p,w)))
        elif o=='jalr':
            target=(adr(t) if '(' in t else v(t))&~1;r['ra']=pc;pc=target;calls.append(pc)
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=v(t)
        elif o in ('bne','bnez','beqz'):
            neq=v(t)!=(v(x[1]) if o=='bne' else 0)
            if neq!=(o=='beqz'):pc=v(x[-1])
        elif o!='fence.i':
            a=v(x[1]);b=v(x[2]) if len(x)>2 else 0
            if o in ('li','mv'):z=a
            elif o in ('addi','add'):z=a+b
            elif o=='andi':z=a&b
            elif o in ('lui','auipc'):z=(a<<12)+(at if o=='auipc' else 0)
            else:raise ValueError((at,o))
            r[t]=z&mask
    passed=late and (not flags&64 or aux!=0)
    want=[(0x200003c0,dst+i,0) for i in range(32)] if passed else []
    if passed:
        for i in range(32):want.extend([(0x20000358,sp+i,get(sp+i,1)),(0x20000362,dst+i,get(sp+i,1))])
    if log!=want or pc!=(0x64bf6 if passed else 0x64c84 if late else 0x64ce8):raise ValueError('copy order/stop')
    if calls!=([0x64bae] if late else [])+([0x2000039c,0x20000332] if passed else []):raise ValueError('callee')
    if get(dst+16,4)!=(0x174ee if passed else 0xa5a5a5a5):raise ValueError('callback word')

for f in (0,64,255):
    for a in (0,1):trace(f,a);trace(f,a,0x64bae)
print('PASS: 4 ordered 32-byte fills/copies; 2 auxiliary and 6 null-callback guard exits with no destination write')
