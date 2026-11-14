"""Stable-field synthetic composition of callee and caller projections.

Successful loads and normal stub returns are assumed. No physical memory,
concurrency, provider side effects, or continuous CPU are simulated.
"""
import hashlib
import importlib.util
import itertools
from pathlib import Path
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
    outcomes={}; witnesses={}; count=0
    for fields in itertools.product((0xfffe,0x1234),(0,1,255),(0,1,255),(0xfffe,0x1234),(0,1,255),(0,1,255)):
        h0,m0,activity0,h1,m1,activity1=fields
        first_active=h0!=0xfffe and m0!=0 and activity0!=0
        second_active=h1!=0xfffe and m1!=0 and activity1!=0
        for delta in (0,34,35,0xffffffff):
            sp,ra,gp=0x20001000,0x12345678,0x20002000
            result,csp,cra,events=callee.run(image,fields,sp-16,0x13d50,0xffffffff)
            if (result,csp,cra,events)!=callee.expected(fields,sp-16,0x13d50): raise ValueError('callee mismatch')
            if result != int(first_active or second_active): raise ValueError('independent result mismatch')
            pc,regs,saved,calls,reads=entry.run(code,h0,h0,result,sp,ra)
            if regs[10]!=result or regs[13]!=h0 or saved!={sp-4:ra}: raise ValueError('entry mismatch')
            p,a0,psp,pra,pathreads=paths.run(image,h0,m0,h1,m1,result,sp,ra)
            if pc!=(0x13d72 if h0==0xfffe else 0x13d68) or a0!=result or reads[0]!=pathreads[0]: raise ValueError('boundary mismatch')
            pass_first=h0!=0xfffe and m0==0
            pass_second=h1!=0xfffe and m1==0
            caller_pass=pass_first or pass_second
            cross_group=(pass_first and second_active) or (first_active and pass_second)
            if bool(result and caller_pass)!=bool(cross_group): raise ValueError('cross-group equivalence mismatch')
            # If the first passes, it short-circuits regardless of second.
            if not caller_pass:
                if (p,psp,pra)!=(ra,sp,ra): raise ValueError('return mismatch')
                kind=('return',result)
            else:
                if (p,psp,pra)!=((0x13da2 if result==0 else 0x13d8a),sp-16,0x13d50): raise ValueError('caller mismatch')
                previous=0xffffffef; clock=(previous+delta)&0xffffffff
                dest,args,tsp,tra,_,_,_=tail.run(image,result,clock,previous,gp,sp,ra)
                if (tsp,tra)!=(sp,ra): raise ValueError('tail frame mismatch')
                if result:
                    # Under stable fields a nonzero result and caller success
                    # require one active group and the other group to pass.
                    if not cross_group:
                        raise ValueError('nonzero witness invariant')
                    expected=(0x9124,(0x13346,0,100,0)); kind=('nonzero',1)
                elif delta<=34: expected=(0x9124,(0x13346,0,35,0)); kind=('short',0)
                else: expected=(0x13346,(0,)); kind=('long',0)
                if (dest,args)!=expected: raise ValueError('tail mismatch')
            outcomes[kind]=outcomes.get(kind,0)+1
            witnesses.setdefault(kind,fields)
            count+=1
    required={('return',0),('return',1),('nonzero',1),('short',0),('long',0)}
    if set(outcomes)!=required: raise ValueError(f'missing outcomes {outcomes}')
    print(f'PASS: {count} stable-field cases; 5 result/outcome combinations')
    print('PASS: nonzero result + continuation requires one active group and the other group passing')
    print(f'Counts: {outcomes}')
    print('Synthetic finite values, stable fields, normal returning stubs; no physical execution.')

if __name__=='__main__': main()
