"""Compose callee and caller projections using separately supplied live reads.

Neither a continuous CPU nor concurrency/provider behavior is simulated.
"""
import hashlib
import importlib.util
from pathlib import Path
import random
HERE=Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

callee,entry,paths,tail=(load(n) for n in ('callee','verify','paths','tail'))


def main():
    image=callee.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=callee.SHA: raise ValueError('firmware identity mismatch')
    code=image[entry.BASE-0x8000:entry.BASE-0x8000+len(entry.CODE)]
    if code!=entry.CODE: raise ValueError('entry bytes mismatch')
    rng=random.Random(0x135e6)
    # Two qualifying groups and one neither-qualified group.
    pre_cases=((0x1234,1,1,0xfffe,0,0),(0xfffe,0,0,0x1234,2,255),(0xfffe,0,0,0xfffe,0,0))
    # First qualifies caller, second qualifies caller, or direct return.
    post_cases=((0x1234,0,0xfffe,0),(0xfffe,0,0x1234,0),(0xfffe,0,0xfffe,0))
    outcomes=set(); changed=0; count=0
    for i in range(18000):
        pre=pre_cases[i%3]; post=post_cases[(i//3)%3]
        delta=(0,34,35,0xffffffff)[(i//9)%4]
        result,sp_after,ra_after,events=callee.run(image,pre,0x20000ff0,0x13d50,rng.getrandbits(32))
        if (result,sp_after,ra_after,events)!=callee.expected(pre,0x20000ff0,0x13d50): raise ValueError('callee mismatch')
        if pre[0]!=post[0]: changed+=1
        # entry.run stubs the call with the result computed above and post-call H0.
        pc,regs,saved,calls,reads=entry.run(code,pre[0],post[0],result,0x20001000,0x12345678)
        if regs[10]!=result or regs[13]!=post[0] or saved!={0x20000ffc:0x12345678}: raise ValueError('callee/entry boundary mismatch')
        next_pc,a0,sp,ra,readset=paths.run(image,*post,result,0x20001000,0x12345678)
        if (pc != (0x13d72 if post[0]==0xfffe else 0x13d68) or a0!=result or reads[0]!=readset[0]): raise ValueError('caller state mismatch')
        if next_pc==0x12345678:
            if (sp,ra)!=(0x20001000,0x12345678): raise ValueError('return frame mismatch')
            outcomes.add(('return',result)); count+=1; continue
        if (sp,ra,next_pc)!=(0x20000ff0,0x13d50,0x13da2 if result==0 else 0x13d8a): raise ValueError('tail input mismatch')
        previous=rng.getrandbits(32); clock=(previous+delta)&0xffffffff
        dest,args,restored_sp,restored_ra,rds,wrs,clls=tail.run(image,result,clock,previous,0x20002000,0x20001000,0x12345678)
        if (restored_sp,restored_ra)!=(0x20001000,0x12345678): raise ValueError('tail frame mismatch')
        if result: expected=(0x9124,(0x13346,0,100,0)); kind='nonzero'
        elif delta<=34: expected=(0x9124,(0x13346,0,35,0)); kind='short'
        else: expected=(0x13346,(0,)); kind='long'
        if (dest,args)!=expected: raise ValueError('tail output mismatch')
        outcomes.add((kind,result)); count+=1
    required={('return',0),('return',1),('nonzero',1),('short',0),('long',0)}
    if outcomes!=required or not changed: raise ValueError(f'missing cases {outcomes}')
    print(f'PASS: {count} composed cases, {changed} with different pre/post halfwords; all 5 result/outcome combinations')
    print('Boundary reconstruction only: separate supplied reads may require an intervening write; no continuous CPU, actual provider, concurrency, or hardware.')

if __name__=='__main__': main()
