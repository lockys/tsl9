"""Bounded full-table return at 0x9234, no provider invocation.

Input a0=1 comes from 0x924c. Stack read values are synthetic; traps, aliasing,
interrupts and real hardware are not modeled.
"""
import hashlib
import importlib.util
from pathlib import Path
import random
HERE=Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py')); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
v=load('verify'); z=load('zero_delay_scan'); m=load('match_scan'); free=load('free_scan'); setup=load('setup'); branch=load('delay_precedence')
MASK=0xffffffff
OPS={0x9234:'f240',0x9236:'6244',0x9238:'d244',0x923a:'4249',0x923c:'b249',0x923e:'224a',0x9240:'0561',0x9242:'8280'}


def run(image,sp,saved,a0):
    if len(saved)!=6 or any(not 0<=x<=MASK for x in (sp,a0,*saved)): raise ValueError('bad input')
    pc=0x9234; regs={}; events=[]
    mapping={0x9234:('ra',1,28),0x9236:('s0',0,24),0x9238:('s1',2,20),0x923a:('s2',3,16),0x923c:('s3',4,12),0x923e:('s4',5,8)}
    for _ in range(9):
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc in mapping:
            name,i,offset=mapping[pc]; regs[name]=saved[i]; events.append(('read',(sp+offset)&MASK,4,saved[i])); pc+=2
        elif pc==0x9240: sp=(sp+32)&MASK; pc+=2
        elif pc==0x9242: return a0,regs['ra'],sp,regs,tuple(events)
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    rng=random.Random(416006); delays=(0,1,300,0xffffffff); modes=(0,1,0x100,0xffffffff)
    for n in range(20000):
        callback=0 if n&1 else 0x1333c; delay=delays[n%4]; mode=modes[(n//4)%4]
        words=[rng.choice((1,0xabcdef01,0xffffffff)) for _ in range(15)]
        if branch.branch(image,delay)==0x913c and z.scan(image,words)[0]!=0x9188: raise ValueError('zero scan mismatch')
        if setup.run(image,callback,mode,delay,0)!=(callback,mode,z.BASE,delay,0,z.BASE): raise ValueError('setup mismatch')
        if m.scan(image,words,callback)[:2]!=(0x9206,15): raise ValueError('match miss mismatch')
        pc,idx,_,a0,reads=free.scan(image,words)
        if (pc,idx,a0,len(reads))!=(0x9234,15,1,15): raise ValueError('full scan mismatch')
        sp=0xfffffff0 if n&1 else 0x1000; saved=[rng.getrandbits(32) for _ in range(6)]
        value,dest,end,regs,events=run(image,sp,saved,a0)
        expected=tuple(('read',(sp+off)&MASK,4,saved[i]) for i,off in ((1,28),(0,24),(2,20),(3,16),(4,12),(5,8)))
        if (value,dest,end)!=(1,saved[1],(sp+32)&MASK) or regs!=dict(zip(('s0','ra','s1','s2','s3','s4'),saved)) or events!=expected: raise ValueError('full exit mismatch')
    for addr in OPS:
        bad=bytearray(image); bad[addr-0x8000]^=1
        try: run(bad,0x1000,[0]*6,1)
        except ValueError as e:
            if str(e).startswith('opcode mismatch'): continue
        raise ValueError(f'mutant accepted {addr:#x}')
    print('PASS: 20000 composed full/nonmatching table cases across delay/mode boundaries')
    print('PASS: return a0=1, six ordered stack reads, no modeled provider call; 8 opcode mutations rejected')
    print('Only bounded projections; stable table, successful independent reads, no traps or hardware.')

if __name__=='__main__': main()
