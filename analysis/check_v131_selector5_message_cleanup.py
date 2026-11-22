"""Zero-status cleanup, V1.31 candidate. Args: APP, reference, rasm2.
Use disassembled caller instructions, synthetic disjoint RAM and normal helper returns.
No allocator effects or actual ownership inferred.
"""
from pathlib import Path
import re, runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for l,h in [(0x4e1ae,0x4e1c2),(0x4e224,0x4e226),(0x4e22c,0x4e23a),(0x4e1c8,0x4e1d2),(0x4e27c,0x4e286)]:
    g['window'](g['b'],0x40000,l,h)

def ck(x):
    if not x: raise ValueError('message cleanup')

def case(base,ident,ptr,result):
    sp=0x2000ff80; end=0x44444; regs=dict(a0=base,s0=11,s1=12,sp=sp,ra=end); mem={}; calls=[]; reads=[]
    def put(p,n,v):mem.update({p+i:v>>(8*i)&255 for i in range(n)})
    def get(p,n):return sum(mem[p+i]<<(8*i) for i in range(n))
    put(base+2,2,ident);put(base+8,4,ptr);pc=0x4e1ae
    for _ in range(64):
        if pc==end:break
        if pc==0x4ded0:
            ck((regs['s1'],regs['s0'])==(base,ident));pc=0x4e224;regs['a0']=0;continue # intervening decode and dispatch not run
        if pc in (0x20000110,0x4d962):
            calls.append((pc,regs['a0'],regs['a1']));regs['a0']=0x11111111 if pc==0x20000110 else result;pc=regs['ra'];continue
        at=pc;n,o,x=g['code'][pc];pc+=n;t=x[0]
        def addr(arg):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',arg).groups();return (regs[k]+int(d))&0xffffffff
        if o in ('sw','lw','lhu'):
            p=addr(x[1]);w=2 if o=='lhu' else 4
            if o=='sw':put(p,w,regs[t])
            else:regs[t]=get(p,w);reads.append((at,p))
        elif o=='addi':regs[t]=(regs[x[1]]+int(x[2]))&0xffffffff
        elif o=='mv':regs[t]=regs[x[1]]
        elif o=='li':regs[t]=int(x[1],0)
        elif o=='auipc':regs[t]=(at+(int(x[1],0)<<12))&0xffffffff
        elif o=='beqz':pc=int(x[-1],0) if not regs[t] else pc
        elif o=='jalr':regs['ra'],pc=pc,addr(t)&~1
        elif o=='jal':regs['ra'],pc=pc,int(x[-1],0)
        elif o=='j':pc=int(t,0)
        elif o=='ret':pc=regs['ra']&~1
        else:raise ValueError((hex(at),o))
    ck([c[:2] for c in calls]==([(0x20000110,ptr)] if ptr else [])+[(0x4d962,ident)])
    ck(calls[-1][2]==1 and (pc,regs['a0'],regs['sp'],regs['s0'],regs['s1'])==(end,result,sp,11,12))
    ck((0x4e22c,base+8) in reads and get(base+8,4)==ptr)

for b in (0x20005700,0x20006100):
    for i in (0,255,0x1234,65535):
        for p in (0,0x20004600,0x20004908):
            for r in (0,3,0x55667788):case(b,i,p,r)
print('PASS: 72 cleanup traces; 24 null skips, 48 pointer handoffs; final helper result forwarded')
