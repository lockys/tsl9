"""Trace the nominal APP prefix through five calls. APP, rasm2 path. Not hardware."""
import sys,re,subprocess
from pathlib import Path
from hashlib import sha256

def ck(v):
    if not v: raise ValueError('two-call trace mismatch')
a=Path(sys.argv[1]).read_bytes(); ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
code={}
for p,e in [(0x197f0,0x1989a),(0x8520,0x854a),(0x19124,0x19142),(0x1908c,0x1909e),(0x188e2,0x1892e),(0x19160,0x1917e),(0x1892e,0x18986)]:
    lines=subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(p),'-D',a[p-32768:e-32768].hex()],text=True)
    for line in lines.splitlines():
        addr,n,raw,op,*args=line.split(); ck(int(addr,16)==p and bytes.fromhex(raw)==a[p-32768:p-32768+int(n)]);code[p]=(int(n),op,''.join(args).split(','));p+=int(n)
    ck(p==e)
M=0xffffffff; sp=0x2000fed0; d=sp+32; base=0x40012400
for seed in [0,0xffffffff,0xa5c39e71]:
    ram={}; writes=[]; reads=[]; r={'zero':0,'sp':sp+128,'ra':0,**{'s'+str(i):seed for i in range(12)}}
    def run(pc,end):
        for _ in range(128):
            if pc==end:return
            n,op,x=code[pc];pc+=n;t=x[0];val=lambda k:r[k] if k in r else int(k,0)
            if op in ('sw','sb','lw','lbu'):
                off,reg=re.fullmatch(r'(\d+)\((\w+)\)',x[1]).groups();loc=(r[reg]+int(off))&M;size=1 if op in ('sb','lbu') else 4
                if op in ('sw','sb'):
                    writes.append((loc,size,r[t]&((1<<(size*8))-1)));ram.update({loc+i:r[t]>>(8*i)&255 for i in range(size)})
                else:
                    reads.append((loc,size));r[t]=sum(ram.get(loc+i,seed>>(8*(i%4))&255)<<(8*i) for i in range(size))
            elif op=='jal':ck(t=='ra');r[t]=pc;pc=val(x[1])
            elif op=='ret':pc=r['ra']
            elif op=='j':pc=val(t)
            elif op=='not':r[t]=(~val(x[1]))&M
            elif op=='bne':pc=val(x[2]) if r[t]!=val(x[1]) else pc
            elif op in ('bnez','beqz'):
                if bool(r[t])==(op=='bnez'):pc=val(x[1])
            elif op in ('bleu','bltu'):
                if (r[t]<=val(x[1]) if op=='bleu' else r[t]<val(x[1])):pc=val(x[2])
            elif op in ('li','mv','lui'):r[t]=(val(x[1])<<(12 if op=='lui' else 0))&M
            elif op in ('addi','add','andi','and','or','slli'):
                v,w=val(x[1]),val(x[2]);r[t]=(v+w if op in ('addi','add') else v&w if op in ('andi','and') else v|w if op=='or' else v<<w)&M
            else:raise ValueError(op)
        raise ValueError('step bound')
    run(0x197f0,0x19814);writes.clear();run(0x19814,0x19818);ck(writes==[(d+i,4,0) for i in range(0,32,4)])
    run(0x19818,0x1986e);ck(r['s1']==base and writes[8:]==[(sp+i,4,seed) for i in range(4,25,4)])
    writes.clear();reads.clear();run(0x1986e,0x19172)
    port=0x4002100c; prior=seed|512; fresh=prior^0x80000000
    ck(writes==[(0x40021018,4,seed|512),(0x40021004,4,(seed&0xffff3fff)|0xc000),(sp-4,4,0x1987e),(port,4,prior)])
    # A peripheral may return a different value on its next read. Inject one changed bit.
    ram.update({port+i:fresh>>(8*i)&255 for i in range(4)});run(0x19172,0x1987e)
    ck(writes[-1]==(port,4,fresh&~512) and len(writes)==5 and reads==[(0x40021018,4),(0x40021004,4),(port,4),(sp-4,4),(port,4)])
    ck(r['sp']==sp and r['s0']==0x40012000 and r['s1']==base and r['ra']==0x1987e and all(ram[d+i]==0 for i in range(32)))
    run(0x1987e,0x19896);writes.clear();reads.clear();run(0x19896,0x1989a)
    ck(writes==[(base+4,4,seed&0xe0f0feff),(base+8,4,(seed&0xfff1f7fd)|0xe0000),(base+44,4,seed&0xff0fffff)])
    ck([p-d for p,n in reads if d<=p<d+32]==[24,0,28,4,12,16,8,20]);ck(all(p+4<=0x2000321c or p>=0x20003220 for p in [*range(d,d+32,4),*(w[0] for w in writes)]))
print('PASS: five calls in order; 4 intermediate MMIO writes, 1 stack save, fresh read honored; three patterns')
