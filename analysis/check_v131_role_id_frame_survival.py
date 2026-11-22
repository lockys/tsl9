"""APP, V1.31 reference, rasm2. One synthetic state through all four callees.
Assumes Xwchc, mapped RAM fill routine, successful accesses, ordinary MMIO and no interference.
"""
from pathlib import Path
import re, runpy

g=runpy.run_path(str(Path(__file__).with_name('check_v4160_geometry_chain.py')))
for lo,hi in [(0x46570,0x465b4),(0x45220,0x45380),(0x48c56,0x48ce6),(0x47eac,0x47f2a),(0x6d682,0x6d700),(0x4d9ec,0x4da18)]:g['window'](g['b'],0x40000,lo,hi)
entries=(0x45220,0x48c56,0x47eac,0x6d682); resumes=(0x4657a,0x4657e,0x46582,0x46586); io=0x4002420c

def trace(s,task,sample):
    r=dict(zero=0,a0=task,sp=s,ra=0x6dd3e);m={};pc=0x46570;calls=[];returns=[];stores=[[] for _ in entries];active=None;slot=[];reads=[]
    def put(p,w,z):m.update({p+i:z>>(8*i)&255 for i in range(w)})
    def get(p,w):return sum(m[p+i]<<(8*i) for i in range(w))
    def v(k):return r[k] if k in r else int(k,0)
    def address(k):
        d,b=re.fullmatch(r'(-?\d+)\((\w+)\)',k).groups();return (r[b]+int(d))&0xffffffff
    put(io,4,sample)
    for _ in range(1000):
        if pc==0x6dd3e:break
        if pc in resumes:
            if active!=resumes.index(pc) or r['sp']!=s-32 or get(s-20,4)!=task:raise ValueError('callee return')
            returns.append(pc);active=None
        if pc in entries:active=entries.index(pc);calls.append(pc)
        at=pc;n,op,x=g['code'][at];pc+=n;t=x[0]
        if op in ('lw','sb','sh','sw'):
            p=address(x[1]);w={'lw':4,'sb':1,'sh':2,'sw':4}[op]
            if op=='lw':r[t]=get(p,w);reads.append((at,p,r[t]))
            else:
                put(p,w,r[t]);item=(at,p,w,get(p,w))
                if p<s-16 and p+w>s-20:slot.append(item)
                if active is not None:stores[active].append(item)
        elif op in ('jal','j','jr','ret'):
            dest=r['ra'] if op=='ret' else address(t) if op=='jr' else v(x[-1]);
            if op=='jal':r['ra']=pc
            pc=dest&~1
        elif op in ('bne','beqz','bnez','bltu'):
            a=v(t);b=v(x[1]) if len(x)==3 else 0
            if {'bne':a!=b,'beqz':a==0,'bnez':a!=0,'bltu':a<b}[op]:pc=v(x[-1])
        elif op!='fence.i':
            a=v(x[1]);b=v(x[2]) if len(x)>2 else 0
            if op in ('li','add','addi'):z=a+b
            elif op in ('lui','auipc'):z=(a<<12)+(at if op=='auipc' else 0)
            elif op=='mul':z=a*b
            elif op=='slli':z=a<<b
            elif op=='srli':z=a>>b
            else:raise ValueError((at,op))
            r[t]=z&0xffffffff
    if (tuple(calls),tuple(returns),slot)!=(entries,resumes,[(0x46574,s-20,4,task)]):raise ValueError('saved ID footprint')
    if reads!=[(0x200003a0,io,sample),(0x4659c,s-20,task),(0x465a6,s-4,0x6dd3e)]:raise ValueError(reads)
    if stores[-1][-8:]!=[(0x200003a4,io,4,0)]+[(0x200003c0,0x200035b0+i,1,0) for i in range(6)]+[(0x200003b8,io,4,sample)]:raise ValueError('fill')
    if (pc,r['a0'],r['sp'],get(0x200033ac,1),get(0x2000332e,1),get(0x2000332c,2))!=(0x6dd3e,0,s,task,task,5):raise ValueError('tail')
    return tuple(map(len,stores))

counts={trace(s,t,m) for s in (0x2000ff80,0x2000ffc0) for t in range(256) for m in (0,0x12345678)}
if len(counts)!=1:raise ValueError(counts)
print('PASS: 1024 continuous paths; callee store counts',counts.pop(),'; only caller save touches the ID slot')
