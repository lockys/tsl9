"""Synthetic cross-segment witness: zero delay + full table + existing key.

This combines separate fixed-instruction projections with reconstructed
boundary state; it is not a continuous machine or hardware test. Provider
calls are assumed to return, preserve saved registers, and not mutate table,
stack or gp. All reads succeed; no concurrent writes or memory aliases.
"""
import hashlib
import importlib.util
from pathlib import Path
import random
HERE=Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py')); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
z=load('zero_delay_scan'); setup=load('setup'); m=load('match_scan'); u=load('match_update'); c=load('common'); e=load('resident_exit'); d=load('delay_precedence')


def main():
    image=z.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=z.v.SHA: raise ValueError('firmware identity mismatch')
    rng=random.Random(416005); seen=set()
    for n in range(20000):
        index=n%15; callback=0x1333c; mode=(0,1,0x100,0xffffffff)[n%4]; old=(0,0x87654321)[(n//4)%2]; result=(0,0xdeadbeef)[(n//8)%2]
        words=[0xabcdef01]*15; words[index]=callback
        if d.branch(image,0)!=0x913c or z.scan(image,words)[0]!=0x9188: raise ValueError('zero-delay scan mismatch')
        if setup.run(image,callback,mode,0,0x12345678)!=(callback,mode,z.BASE,0,0x12345678,z.BASE): raise ValueError('setup mismatch')
        pc,found,_,_=m.scan(image,words,callback)
        if (pc,found)!=(0x91a2,index): raise ValueError('match mismatch')
        task=rng.randrange(256); target=0x12345678; sp=0x1000; saved=[rng.getrandbits(32) for _ in range(6)]
        a0,a1,events=u.run(image,index,old,mode,0x12345678,task,target)
        if (a0,a1)!=(task,1<<index) or events[-2:]!=(('write',z.BASE+12*index,1,mode&255),('write',z.BASE+12*index+8,4,0x12345678)): raise ValueError('update mismatch')
        pc,mask,scaled,a5=c.run(image,a1,0,mode)
        if (pc,mask,scaled,a5)!=(0x922c if mode==0 else 0x91ea,1<<index,0,0x40000): raise ValueError('common mismatch')
        kind,dest,out,_,_,_=e.run(image,mode,task,sp,saved,target,result)
        expected=('return',saved[1],int(result==0)) if mode==0 else ('tail',target,task)
        if (kind,dest,out)!=expected: raise ValueError('exit mismatch')
        seen.add((index,mode,old,result))
    if len(seen)!=15*4*2*2: raise ValueError(f'missing cases {len(seen)}')
    print(f'PASS: 20000 composed zero-delay/full-table/matching-key cases; {len(seen)} boundary combinations')
    print('PASS: mode zero calls resident; nonzero mode tail-jumps; scaled delay remains zero')
    print('Segments reconnected at boundaries; providers assumed benign, no continuous CPU or hardware execution.')

if __name__=='__main__': main()
