"""Args: APP, V1.31, rasm2. Inherited sparse states; optional zero-hook control is explicit."""
from pathlib import Path
import runpy
s=runpy.run_path(str(Path(__file__).with_name('check_v131_slot0_zero_count_next.py')))
g=s['g']; ck=s['ck']; g['window'](g['b'],0x40000,0x4db60,0x4dbf2)
M=0xffffffff; SLOT=0x200034e0; HOOK=0x20003220

def run(reg,mem,zero_hook):
    r=reg.copy();m=mem.copy();size=r['a0'];pc=0x20000040;stores=[];returned=False
    ck(size in (0,80) and (r['a1'],r['ra'])==(0x4c05,0x4db60))
    if zero_hook:
        ck(all(HOOK+i not in m for i in range(4)));m.update({HOOK+i:0 for i in range(4)})
    for _ in range(200):
        if pc==0x4db84:break
        if pc==0x4db60:ck(r['a0']==0);returned=True
        at=pc;n,o,x=g['code'][pc];pc+=n;t=x[0]
        if o in ('lw','lhu','sb','sw'):
            d,k=x[1][:-1].split('(');p=(r[k]+int(d))&M;w={'lw':4,'lhu':2,'sb':1,'sw':4}[o]
            if o in ('sb','sw'):
                ck(not(p<SLOT+4 and SLOT<p+w));stores.append((at,p,w,r[t]));m.update({p+i:(r[t]>>(i*8))&255 for i in range(w)})
            elif at==0x20000094 and not zero_hook:
                ck(size==80 and p==HOOK and all(p+i not in m for i in range(w)));pc=at;break
            else:r[t]=int.from_bytes(bytes(m[p+i] for i in range(w)),'little')
        elif o in ('beqz','bnez','bne','bltu'):
            a=r[t];b=0 if len(x)==2 else r[x[1]]
            if (a==b if o=='beqz' else a<b if o=='bltu' else a!=b):pc=int(x[-1],0)
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=int(t,0)
        elif o=='lui':r[t]=(int(x[1],0)<<12)&M
        elif o=='li':r[t]=int(x[1],0)&M
        elif o in ('addi','slli','srli','andi'):
            a=r[x[1]];b=int(x[2],0);r[t]=(a+b if o=='addi' else a<<b if o=='slli' else a>>b if o=='srli' else a&b)&M
        elif o!='fence.i':raise ValueError((hex(at),o))
    else:raise ValueError('step bound')
    ck(bytes(m[SLOT+i] for i in range(4))==bytes(4)); ck([p for at,p,w,z in stores[:3]]==[reg['sp']-8,reg['sp']-4,0x4002420c])
    if not size or zero_hook:
        ck(returned and pc==0x4db84 and stores[3:]==[(0x2000005e,0x4002420c,4,reg_io(mem)),(0x4db60,reg['s2'],4,0),(0x4dbe8,0x20002fa0,1,0),(0x4dbec,0x20002fa1,1,0)])
    else:ck(not returned and pc==0x20000094 and len(stores)==3)
    return pc

def reg_io(m):return int.from_bytes(bytes(m[0x4002420c+i] for i in range(4)),'little')
ends=[run(r,m,False) for _,r,m in s['states']];ck(ends.count(0x4db84)==4 and ends.count(0x20000094)==4)
ck([run(r,m,True) for _,r,m in s['states'] if r['a0']==80]==[0x4db84]*4)
print('PASS: 4 zero-size returns; 4 size-80 stops at unknown hook word; 4 explicit zero-hook controls return; no modeled store overlaps callback')
