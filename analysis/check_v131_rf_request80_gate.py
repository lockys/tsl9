"""Inherited zero-outer-count prefix + controlled two-byte inputs. Args: APP, V1.31, rasm2."""
from pathlib import Path
import runpy

ctx=runpy.run_path(str(Path(__file__).with_name('check_v131_slot0_zero_count_next.py')))
g=ctx['g']; code=g['code']; ck=ctx['ck']
# Check the no-wait suffix of the RF function, separately from the later outer gates.
for lo,hi in ((0x64252,0x64298),(0x6636e,0x663a6)):
    ops=[(p,code[p][1]) for p in sorted(code) if lo<=p<hi]
    ck(all(o in ('lw','lui','addi','ori','andi','or','and','sw','sb','ret','jal') for p,o in ops))
    ck([(p,o) for p,o in ops if o in ('ret','jal')]==([(lo,'jal'),(hi-2,'ret')] if lo==0x64252 else [(hi-2,'ret')]))
ck(code[0x64252][2][-1]=='0x6636e')
# Use inherited s0/s1 from the prior runner (these registers survive its final straight-line block).
_,regs,_=ctx['states'][0]; sizes={}; hits=[]
for a in range(256):
    for b in range(256):
        mem={0x200033b4:a,0x20002fa1:b}; r=regs.copy(); pc=0x4db3e
        while pc!=0x20000040:
            at=pc;n,o,x=code[pc];pc+=n;t=x[0]
            if o in ('lbu','sb','jalr'):
                d,k=x[-1][:-1].split('(');p=(r[k]+int(d))&0xffffffff
                if o=='lbu':r[t]=mem[p]
                elif o=='sb':mem[p]=r[t]&255
                else:r['ra']=pc;pc=p&~1
            elif o in ('auipc','lui'):r[t]=((at if o=='auipc' else 0)+(int(x[1],0)<<12))&0xffffffff
            else:
                v=r[x[2]] if x[2] in r else int(x[2],0);u=r[x[1]]
                if o in ('add','addi'):z=u+v
                elif o=='slli':z=u<<v
                elif o=='andi':z=u&v
                else:raise ValueError(o)
                r[t]=z&0xffffffff
        c=(a+b)&255; ck(mem=={0x200033b4:a,0x20002fa1:b,0x20002fa0:c} and (r['a0'],r['a1'],r['ra'])==(16*c,0x4c05,0x4db60))
        sizes[r['a0']]=sizes.get(r['a0'],0)+1
        if r['a0']==80:hits.append(a+b)
ck(set(sizes.values())=={256} and len(sizes)==256 and hits.count(5)==6 and hits.count(261)==250)
print('PASS: 8 inherited exits; 65536 controlled byte pairs; 80-byte request for 6 sums of 5 and 250 sums of 261; not allocator success')
