"""Post-copy 53890 to return. Inject only 433a8's word result, not its effects. Args: APP V131 rasm2."""
from pathlib import Path
import re,runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for lo,hi in [(0x53890,0x5397c),(0x43e8e,0x43ed2)]:g['window'](g['b'],0x40000,lo,hi)
M=0xffffffff;O=0x200033b8;ID=0x200035f5;S=0x2000ff20

def ck(ok):
    if not ok:raise ValueError('pair filter mismatch')

def trace(draws,source,initial,stops):
    pc=0x53890;i=0;mem={};stores=[];vis=[];r=dict(sp=S,s0=O,s1=0x4000,zero=0);ret=0x123456
    def put(p,n,v):mem.update({p+j:v>>(8*j)&255 for j in range(n)})
    def get(p,n):return sum(mem[p+j]<<(8*j) for j in range(n))
    def va(s):return r[s] if s in r else int(s,0)
    def adr(s):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (int(d)+r[k])&M
    put(S+28,4,ret);put(ID,1,initial);put(O+232,6,source)
    for j in (12,16,20,24):put(S+j,4,j)
    for _ in range(800):
        if pc==ret:break
        if pc==0x433a8:
            if i==len(draws):break
            r['a0']=draws[i];i+=1;pc=r['ra'];continue
        if pc in (0x53966,0x538e2):vis.append(pc)
        at=pc;w,o,x=g['code'][pc];pc+=w;t=x[0]
        if o in ('sw','sh','sb','lh','lw'):
            p=adr(x[1]);n={'sb':1,'sh':2,'sw':4,'lw':4,'lh':2}[o]
            if o.startswith('s'):stores.append((p,n));put(p,n,r[t])
            else:
                v=get(p,n);r[t]=((v^32768)-32768)&M if o=='lh' else v
        elif o=='jal':ck(t=='ra');r[t]=pc;pc=va(x[1])
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=va(t)
        elif o in ('beq','bne','beqz'):
            if (r[t]==(0 if o=='beqz' else r[x[1]]))!=(o=='bne'):pc=va(x[-1])
        else:
            y=va(x[1]);z=va(x[2]) if len(x)>2 else 0
            if o in ('li','mv'):v=y
            elif o=='lui':v=y<<12
            elif o in ('add','addi'):v=y+z
            elif o=='sub':v=y-z
            elif o in ('or','ori'):v=y|z
            elif o in ('and','andi'):v=y&z
            elif o=='slli':v=y<<z
            elif o=='srli':v=y>>z
            elif o=='srai':v=((y^0x80000000)-0x80000000)>>z
            elif o in ('mulhu','mulhsu'):v=(((y^0x80000000)-0x80000000 if o=='mulhsu' else y)*z)>>32
            else:raise ValueError((at,o))
            r[t]=v&M
    ck(i==len(draws) and pc==stops and get(ID,1)==initial)
    ck(all(S-32<=p and p+n<=S or O+244<=p and p+n<=O+256 for p,n in stores))
    return vis,mem

# Both products are monotone for these nonnegative first operands.
ck((16383*M)>>32==16382 and (M*M)>>32==M-1)
for initial in (0,11,255):
    # First pair zero, retry. Second-stage zero, then match copied source, then differ.
    vis,m=trace([0,0,M,M,0,0,M,M,0,2],(16382<<32)|(M-1),initial,0x123456)
    ck(vis==[0x53966,0x538e2,0x538e2,0x538e2]);ck(bytes(m[O+k] for k in range(244,256))==bytes.fromhex('fefffffffeff010000000000'))
    ck(trace([0,0]*4,0,initial,0x433a8)[0]==[0x53966]*4)
print('PASS: 3 returns + 3 bounded retry traces; 14/32-bit maxima 16382/4294967294; post-copy stores exclude shared ID with draw effects omitted')
