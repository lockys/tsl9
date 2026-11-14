"""Scaling behavior on 16-bit inputs and at first RV32 multiplication wrap.

These are arithmetic domains, not proof of what any actual caller supplies.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('common',HERE/'common.py'); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
N=1<<32


def main():
    image=c.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=c.v.SHA: raise ValueError('firmware identity mismatch')
    previous=-1
    for delay in range(65536):
        result=c.run(image,1,delay,0)[2]
        if result!=(delay*8)//5 or (result==0)!=(delay==0): raise ValueError(f'16-bit mismatch {delay}')
        if result<=previous: raise ValueError('not strictly increasing')
        previous=result
    # first_wrap is the smallest x with mathematical x*1000 >= 2^32.
    first_wrap=(N+999)//1000
    if not (1000*(first_wrap-1)<N<=1000*first_wrap): raise ValueError('bad threshold')
    before=c.run(image,1,first_wrap-1,0)[2]
    after=c.run(image,1,first_wrap,0)[2]
    if (first_wrap,before,after)!=(4294968,6871947,1): raise ValueError('first wrap mismatch')
    if previous!=104856: raise ValueError('16-bit endpoint mismatch')
    # Reachability of the largest residue follows from gcd=8. x=2^29-1
    # has residue 2^32-1000 (not maximum); solve target 2^32-8 instead.
    inverse=pow(125,-1,1<<29)
    witness=(((N-8)//8)*inverse)%(1<<29)
    if (witness*1000)%N!=N-8: raise ValueError('upper residue witness mismatch')
    maxout=(N-8)//625
    if c.run(image,1,witness,0)[2]!=maxout or maxout!=6871947: raise ValueError('upper bound mismatch')
    print(f'PASS: all 65536 16-bit inputs strictly increasing; 0 -> 0, 65535 -> {previous}')
    print(f'PASS: first multiply wrap at {first_wrap}; output {before} -> {after}')
    print(f'PASS: global output maximum {maxout}, witnessed by input {witness}')
    print('Domains are hypothetical; no caller range or provider behavior is established.')

if __name__=='__main__': main()
