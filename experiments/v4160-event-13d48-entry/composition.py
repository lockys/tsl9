"""Compose three projections at explicit boundaries; not a continuous CPU."""
import hashlib
import importlib.util
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location(name, HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

entry, paths, tail = (load(n) for n in ('verify','paths','tail'))


def main():
    image=entry.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[entry.BASE-0x8000:entry.BASE-0x8000+len(entry.CODE)]
    if code!=entry.CODE: raise ValueError('entry bytes mismatch')
    rng=random.Random(0x13d48)
    outcomes=set()
    for i in range(24000):
        sp, ra, gp = 0x20001000, 0x10000200, 0x20002000
        h0=(0xfffe if i%2 else rng.randrange(0xfffe))
        h1=(0xfffe if i%3==0 else rng.randrange(0xfffe))
        m0=(0 if i%4==0 else rng.randrange(1,256))
        m1=(0 if i%5==0 else rng.randrange(1,256))
        result=(0 if i%2 else 1)
        previous=rng.getrandbits(32)
        delta=(0,34,35,0xffffffff)[i%4]
        clock=(previous+delta)&0xffffffff
        p1, regs, saved, calls, reads=entry.run(code,h0^1,h0,result,sp,ra)
        if p1 != (0x13d72 if h0==0xfffe else 0x13d68): raise ValueError('entry branch mismatch')
        if regs[10]!=result or regs[13]!=h0 or regs[14]!=0xfffe or regs[15]!=0x2000c794 or regs[2]!=(sp-16):
            raise ValueError('entry-to-branch state mismatch')
        if saved!={sp-4:ra} or calls!=[(0x135e6,0)] or reads!=[0x2000c796]: raise ValueError('entry side effects mismatch')
        path=paths.run(image,h0,m0,h1,m1,result,sp,ra)
        p2,a0,path_sp,path_ra,path_reads=path
        if a0!=regs[10] or path_reads[0]!=reads[0]: raise ValueError('path boundary mismatch')
        success=(h0!=0xfffe and m0==0) or ((h0==0xfffe or m0!=0) and h1!=0xfffe and m1==0)
        if not success:
            if (p2,path_sp,path_ra)!=(ra,sp,ra): raise ValueError('direct return mismatch')
            outcomes.add('return')
            continue
        if (p2,path_sp,path_ra)!=((0x13da2 if result==0 else 0x13d8a),sp-16,0x13d50):
            raise ValueError('tail boundary mismatch')
        # tail.run repeats only the branch at 0x13d88, using the same a0.
        dest,args,sp2,ra2,rds,wrs,clls=tail.run(image,a0,clock,previous,gp,sp,ra)
        if (sp2,ra2)!=(sp,ra): raise ValueError('tail restore mismatch')
        if result:
            expected=(0x9124,(0x13346,0,100,0),(),(),())
            outcomes.add('nonzero')
        elif delta<=34:
            expected=(0x9124,(0x13346,0,35,0),(gp+344,),(),(0x81b0,))
            outcomes.add('short')
        else:
            expected=(0x13346,(0,),(gp+344,),((gp+344,clock),),(0x81b0,))
            outcomes.add('long')
        if (dest,args,rds,wrs,clls)!=expected: raise ValueError('composed tail mismatch')
    if outcomes!={'return','nonzero','short','long'}: raise ValueError(f'missing outcomes: {outcomes}')
    print('PASS: 24000 boundary-composed cases; direct return and all three tail outcomes')
    print('Not continuous instruction execution: call stubs and reconstructed boundary state; no hardware or concurrency.')


if __name__=='__main__': main()
