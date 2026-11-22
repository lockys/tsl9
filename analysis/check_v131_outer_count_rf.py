"""Continuous optional RF init, first role to outer count branch (zero or five inner records). APP, V1.31, rasm2.
Synthetic separated RAM and register-backed MMIO, successful accesses and Xwchc.
"""
from pathlib import Path
import re, runpy

here=Path(__file__).parent
g=runpy.run_path(str(here/'check_v4160_geometry_chain.py'))
H=0x20002df2; C=0x20003350; T=0x40024200; M=0xffffffff
for lo,hi in [(0x6dd16,0x6dd1e),(0x61b1c,0x61b5a),(0x55bde,0x55c32),(0x43c4e,0x43c7e),(0x5362e,0x537d8),(0x55bd4,0x55bde),(0x55c48,0x55c52),(0x43e24,0x43e6a),(0x641b0,0x6434a),(0x66098,0x66242),(0x638ea,0x63944),(0x63e58,0x63fa0),(0x6645c,0x671aa),(0x662da,0x663a6),(0x57ac4,0x57ad8),(0x63704,0x63716),(0x5e758,0x5e76c),(H,H+54)]:
    g['window'](g['b'],0x40000 if lo!=H else 0x20000000-0x270,lo,hi)

for lo,hi in [(0x53868,0x5397c),(0x43e8e,0x43ed2),(0x433a8,0x43414),(0x43520,0x4354a),(0x43d62,0x43de4),(0x6df1a,0x6e2ac),(0x6dd1e,0x6dd2e),(0x4da70,0x4db18),(0x4edd2,0x4ee72)]:
    g['window'](g['b'],0x40000,lo,hi)
g['window'](g['a'],0x8000,0x191c6,0x19220)

def trace(seed,used,mask,wait,cfg):
    sp=0x2000ffc0; mem={}; pc=0x6dd16; polls=0; history=[]; watches=[]
    r={'s'+str(i):i for i in range(12)}; r.update(sp=sp,ra=0x8eb8,s0=0x40000,zero=0)
    def put(p,w,z): mem.update({p+i:z>>(8*i)&255 for i in range(w)})
    def get(p,w): return sum((g['b'][p+i-0x40000] if 0x40000<=p+i<0x40000+len(g['b']) else mem[p+i])<<(8*i) for i in range(w))
    for base in (0x40024100,T,0x40025000):
        for i in range(0,212,4): put(base+i,4,0)
    for p,w,z in [(C,1,seed),(0x2000319f,1,0),(0x2000319d,1,used),(0x2000319e,1,29),(0x200031c4,4,0x20004800),(0x200031ec,4,0x2000418c),(0x200031f0,2,0x7000),(0x200031fa,1,3),(0x200031fc,2,27),(0x2000323e,2,31),(0x20003200,1,63),(0x4002420c,4,17),(T,4,mask),(0x20003588,4,0),(0x2000351c,2,0)]: put(p,w,z)
    for p in (0x20002fa6,0x20002fa7,0x20003594,0x20003595,0x20003584,0x2000358c): put(p,1,1)
    for p,w,z in [(0x20003201,1,cfg),(0x20003204,6,0x123456789abc),(0x20002ec8,4,1),(0x200031b0,4,7),(0x200031b4,4,0),(0x20003210,4,0x43520),(0x20003230,4,0x43d62),(0x20003234,4,0x191c6),(0x2000323c,2,16000),(0x40002818,2,0),(0x4000281c,2,20)]: put(p,w,z)
    heap=0x200048a4; end=heap+320
    for p,w,z in [(0x20003190,4,heap),(0x2000318c,4,end),(heap,4,end),(heap+4,2,312),(heap+6,2,0),(0x200031a2,2,4000)]: put(p,w,z)
    sampled=[]; draws=[]; requests=[]
    def v(k): return r[k] if k in r else int(k,0)
    def addr(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups(); return (r[b]+int(d))&M
    def signed(x): return (x^0x80000000)-0x80000000
    for _ in range(10000):
        if pc==0x4db3e or (pc==0x20000040 and r['ra']==0x4db18): break
        if pc==0x20000040: requests.append((r['a0'],r['a1'],r['ra']))
        if pc==0x6632e:
            polls+=1
            if wait and polls==4: break
        if pc in (0x64298,0x641b0,0x63eda,0x6645c,0x537b6,0x53868,0x6dd1e,0x4dad2,0x4daf6): history.append(pc)
        at=pc;n,o,x=g['code'][pc];pc+=n;t=x[0]
        if o in ('lw','lh','lhu','lbu','sw','sh','sb'):
            p=addr(x[1]);w={'lw':4,'sw':4,'lbu':1,'sb':1,'lhu':2,'lh':2,'sh':2}[o]
            if o.startswith('s'):
                if p<=C<p+w: raise ValueError(('count store',hex(at)))
                put(p,w,r[t])
            elif at in (H+48,0x6632e) and p==T+100: r[t]=80 if wait and at==0x6632e else 0
            else:
                z=get(p,w); r[t]=((z^32768)-32768)&M if o=='lh' else z
            if at==0x4daf6: sampled.append((p,w,r[t]))
            if at==0x4340a: draws.append(r[t])
            if at in (0x641bc,0x641d0): watches.append((p,r[t]))
        elif o in ('jal','jalr','jr','j','ret'):
            dest=r['ra'] if o=='ret' else addr(t) if '(' in t else v(x[-1]);
            if o in ('jal','jalr'): r['ra']=pc
            pc=dest&~1
        elif o in ('beq','bne','beqz','bnez','bleu','bltu','blt','bltz','bgez'):
            a=r[t]; b=0 if len(x)==2 else v(x[1]); take={'beq':a==b,'bne':a!=b,'beqz':a==0,'bnez':a!=0,'bleu':a<=b,'bltu':a<b,'blt':signed(a)<signed(b),'bltz':signed(a)<0,'bgez':signed(a)>=0}[o]
            if take:pc=v(x[-1])
        elif o not in ('fence.i','nop'):
            a=v(x[1]); b=v(x[2]) if len(x)>2 else 0
            if o in ('li','mv'): z=a
            elif o in ('lui','auipc'): z=(at if o=='auipc' else 0)+(a<<12)
            elif o in ('add','addi'): z=a+b
            elif o=='sub':z=a-b
            elif o in ('and','andi'): z=a&b
            elif o in ('or','ori'): z=a|b
            elif o in ('slli','sll'):z=a<<(b&31)
            elif o in ('srli','srl'):z=a>>(b&31)
            elif o=='srai':z=signed(a)>>(b&31)
            elif o in ('sltiu','sltu'):z=int(a<b)
            elif o in ('mulhsu','mulhu'):z=((signed(a) if o=='mulhsu' else a)*b)>>32
            elif o=='divu':z=a//b if b else M
            elif o=='remu':z=a%b if b else a
            elif o=='mul':z=a*b
            elif o=='div':
                a,b=signed(a),signed(b);z=-1 if not b else (abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
            else:raise ValueError((hex(at),o))
            r[t]=z&M
    else:raise ValueError('step bound')
    if history!=[0x64298,0x641b0,0x63eda,0x6645c]+([] if wait else [0x537b6,0x53868,0x6dd1e,0x4dad2,0x4daf6]):raise ValueError(history)
    if pc!=(0x6632e if wait else 0x20000040 if seed else 0x4db3e) or watches!=[(0x2000351b,1)]*2 or get(C,1)!=seed:raise ValueError('RF boundary')
    if sampled!=([] if wait else [(C,1,seed)]): raise ValueError(('outer read',sampled))
    if not wait and seed and (r['a0'],r['a1'])!=(16*seed,0x4c04): raise ValueError('outer allocation request')
    expected=[]; z=1
    for _ in range(4): z=((z+9)*214013+2531011)&M; expected.append(z)
    if requests!=([(300,0x9001,0x4ee10)] if cfg and not wait else []): raise ValueError('inner allocation')
    if cfg and not wait:
        if get(0x20003354,4)!=heap+8 or bytes(mem[heap+8+i] for i in range(300))!=(bytes(2)+b'\xff\xff'+bytes(56))*5: raise ValueError('five records')
    if draws!=([] if wait else expected): raise ValueError(('clock draws',draws))
    if get(0x2000319f,1)!=(used if used<29 else 255):raise ValueError('registration result')

for seed in (0,1,5,255):
    for used in (5,29):
        for mask in (0,3):
            for wait in (False,True):
                for cfg in (0,14): trace(seed,used,mask,wait,cfg)
print('PASS: 32 RF returns sample entry count (8 skips, 24 requests); 32 bounded waits never reach sample; 16 five-record allocations verified')
