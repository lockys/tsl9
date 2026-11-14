"""Zero-delay insertion from 0x914a, stop before resident tail transfer.

Stack reloads and resident pointer reads are synthetic successful reads;
no provider, asynchronous memory changes, trapping or hardware are modeled.
"""
import hashlib
import importlib.util
import random
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
v=load('v',HERE/'verify.py'); scan=load('zscan',HERE/'zero_delay_scan.py')
BASE=0x2000be08; MASK=0xffffffff
OPS={0x914a:'b147',0x914c:'b307f702',0x9150:'6244',0x9152:'8545',0x9154:'f240',0x9156:'d244',0x9158:'b249',0x915a:'224a',0x915c:'b395e500',0x9160:'c205',0x9162:'c181',0x9164:'ca97',0x9166:'c8c3',0x9168:'23800700',0x916c:'94c7',0x916e:'b7070400',0x9172:'4249',0x9174:'03a30705',0x9178:'03c5610a',0x917c:'0561',0x917e:'0283'}


def run(image,index,callback,argument,task,target,sp,saved):
    if not 0<=index<15 or not 0<=task<256 or len(saved)!=6 or any(not 0<=x<=MASK for x in (callback,argument,target,sp,*saved)): raise ValueError('bad input')
    # saved = s0, ra, s1, s3, s4, s2; supplied stack words.
    pc=0x914a; a5=a1=t1=0; a0=callback; s2=BASE; regs={}; events=[]
    for _ in range(30):
        if pc==0x917e:
            op=bytes.fromhex(OPS[pc]); off=pc-0x8000
            if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
            return a0,a1,t1,sp,regs,tuple(events)
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0x914a: a5=12; pc+=2
        elif pc==0x914c: a5=(index*a5)&MASK; pc+=4
        elif pc in (0x9150,0x9154,0x9156,0x9158,0x915a,0x9172):
            i,reg,off={0x9150:(0,'s0',24),0x9154:(1,'ra',28),0x9156:(2,'s1',20),0x9158:(3,'s3',12),0x915a:(4,'s4',8),0x9172:(5,'s2',16)}[pc]
            regs[reg]=saved[i]; events.append(('read',(sp+off)&MASK,4,saved[i])); pc+=2
        elif pc==0x9152: a1=1; pc+=2
        elif pc==0x915c: a1=(a1<<(index&31))&MASK; pc+=4
        elif pc==0x9160: a1=(a1<<16)&MASK; pc+=2
        elif pc==0x9162: a1>>=16; pc+=2
        elif pc==0x9164: a5=(a5+s2)&MASK; pc+=2
        elif pc==0x9166: events.append(('write',a5+4,4,a0)); pc+=2
        elif pc==0x9168: events.append(('write',a5,1,0)); pc+=4
        elif pc==0x916c: events.append(('write',a5+8,4,argument)); pc+=2
        elif pc==0x916e: a5=0x40000; pc+=4
        elif pc==0x9174: events.append(('read',a5+80,4,target)); t1=target; pc+=4
        elif pc==0x9178: events.append(('read','gp+166',1,task)); a0=task; pc+=4
        elif pc==0x917c: sp=(sp+32)&MASK; pc+=2
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    rng=random.Random(416002); count=0
    for _ in range(10000):
        index=rng.randrange(15); callback=rng.getrandbits(32); argument=rng.getrandbits(32); task=rng.randrange(256); target=rng.getrandbits(32); sp=rng.getrandbits(30)*4; saved=[rng.getrandbits(32) for _ in range(6)]
        words=[rng.getrandbits(32)|1 for _ in range(15)]; words[index]=0
        pc,idx,_,_=scan.scan(image,words)
        if (pc,idx)!=(0x914a,index): raise ValueError('scan mismatch')
        a0,a1,t1,endsp,regs,events=run(image,index,callback,argument,task,target,sp,saved)
        expected_reads=[('read',(sp+off)&MASK,4,saved[i]) for i,off in enumerate((24,28,20,12,8))]
        slot=BASE+index*12
        expected_reads.extend([('write',slot+4,4,callback),('write',slot,1,0),('write',slot+8,4,argument),('read',(sp+16)&MASK,4,saved[5]),('read',0x40050,4,target),('read','gp+166',1,task)])
        if (a0,a1,t1,endsp)!=(task,1<<index,target,(sp+32)&MASK) or regs!=dict(zip(('s0','ra','s1','s3','s4','s2'),saved)) or events!=tuple(expected_reads): raise ValueError('insert mismatch')
        count+=1
    for addr in OPS:
        bad=bytearray(image); bad[addr-0x8000]^=1
        try: run(bad,0,1,2,3,4,0x1000,[0]*6)
        except ValueError as e:
            if str(e).startswith('opcode mismatch'): continue
        raise ValueError(f'undetected mutation {addr:#x}')
    print(f'PASS: {count} scan-to-zero-delay insertion traces, {len(OPS)} opcode mutants rejected')
    print('Tail-transfer pointer [0x40050] and stack values are synthetic; no provider or hardware execution.')

if __name__=='__main__': main()
