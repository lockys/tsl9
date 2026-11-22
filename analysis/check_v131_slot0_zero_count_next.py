"""Continue the eight 4db3e exits of the RF trace to the next allocator entry.
Args: decoded APP, V1.31 carrier, rasm2. No unknown bytes default to zero.
"""
import runpy, sys
from pathlib import Path
src=Path(__file__).with_name('check_v131_outer_count_rf.py').resolve()
states=[]
def ck(x):
    if not x: raise ValueError('zero-count continuation mismatch')
def save(f,event,arg):
    if event=='return' and f.f_code.co_name=='trace' and f.f_code.co_filename==str(src):
        d=f.f_locals
        if d['pc']==0x4db3e:states.append((d['cfg'],dict(d['r']),dict(d['mem'])))
p=sys.getprofile()
try:
    sys.setprofile(save); ctx=runpy.run_path(str(src))
finally:sys.setprofile(p)
g=ctx['g'];g['window'](g['b'],0x40000,0x4db3e,0x4db60)
slot=0x200034e0
ck(len(states)==8)
summary=[]
for cfg,r,m in states:
    before=bytes(m[slot+i] for i in range(4)); pc=0x4db3e; reads=[];writes=[]
    while pc!=0x20000040:
        at=pc;n,o,x=g['code'][pc];pc+=n;t=x[0]
        if o in ('lbu','sb','jalr'):
            off,base=x[-1][:-1].split('(');addr=(r[base]+int(off))&0xffffffff
            if o=='lbu':reads.append((addr,m[addr]));r[t]=m[addr]
            elif o=='sb':writes.append((addr,r[t]&255));m[addr]=r[t]&255
            else:r['ra']=pc;pc=addr&~1
        elif o in ('lui','auipc'):r[t]=((int(x[1],0)<<12)+(at if o=='auipc' else 0))&0xffffffff
        elif o in ('addi','add','andi','slli'):
            a=r[x[1]];b=r[x[2]] if x[2] in r else int(x[2],0)
            r[t]=(a+b if o in ('add','addi') else a&b if o=='andi' else a<<b)&0xffffffff
        else:raise ValueError((hex(at),o))
    total=((cfg&3)+(cfg>>2)+reads[1][1])&255
    ck(before==bytes(4)==bytes(m[slot+i] for i in range(4)))
    ck(len(reads)==2 and reads[0]==(0x200033b4,(cfg&3)+(cfg>>2)))
    ck(reads[1]==(0x20002fa1,0) and writes==[(0x20002fa0,total)])
    ck((r['a0'],r['a1'],r['ra'])==(16*total,0x4c05,0x4db60));summary.append((reads[1],writes[0],16*total))
ck(sorted(v[2] for v in summary)==[0]*4+[80]*4)
print('PASS: 8 inherited zero-count continuations, one store each, callback word untouched; (second read, store, request bytes):',sorted(set(summary)))
