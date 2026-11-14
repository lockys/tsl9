"""Prove full 32-bit preimage of zero in the scheduler's wrapped scaling.

For x in [0,2^32), y = ((1000*x) mod 2^32) // 625 is zero exactly
when the multiplication residue is 0..624. gcd(1000,2^32)=8, so only
79 multiples of 8 in that range are attainable; each has 8 preimages.
This is arithmetic/byte-projection evidence, not caller reachability.
"""
import hashlib
import importlib.util
import math
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('common',HERE/'common.py'); common=importlib.util.module_from_spec(spec); spec.loader.exec_module(common)
N=1<<32; G=8; MOD=N//G


def zero_preimages():
    if math.gcd(1000,N)!=G: raise ValueError('unexpected gcd')
    inverse=pow(1000//G,-1,MOD)
    if (inverse*(1000//G))%MOD!=1: raise ValueError('inverse mismatch')
    results=set()
    for residue in range(0,625,G):
        root=((residue//G)*inverse)%MOD
        for lift in range(G):
            x=root+lift*MOD
            if ((1000*x)%N)!=residue: raise ValueError('bad root')
            results.add(x)
    if len(results)!=632 or 0 not in results: raise ValueError('bad preimage count')
    return results


def main():
    image=common.v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=common.v.SHA: raise ValueError('firmware identity mismatch')
    roots=zero_preimages()
    # A 32-bit linear congruence has exactly gcd(1000,2^32)=8 roots for
    # each divisible residue. Any zero quotient must have one of the 79
    # enumerated residues, so the set is complete without 2^32 iteration.
    for delay in sorted(roots):
        for mode in (0,1,256,0xffffffff):
            pc,mask,scaled,a5=common.run(image,0x80010001,delay,mode)
            if (pc,mask,scaled,a5)!=(0x922c if mode==0 else 0x91ea,1,0,0x40000): raise ValueError('instruction projection mismatch')
        for neighbour in ((delay-1)%N,(delay+1)%N):
            scaled=((neighbour*1000)%N)//625
            if (scaled==0)!=(neighbour in roots): raise ValueError('boundary mismatch')
            if common.run(image,1,neighbour,0)[2]!=scaled: raise ValueError('neighbour projection mismatch')
    nonzero=sorted(roots-{0})
    print(f'PASS: 79 residues × 8 preimages = {len(roots)} zero-output inputs, {len(nonzero)} nonzero')
    print(f'PASS: smallest nonzero input={nonzero[0]} (0x{nonzero[0]:08x}); multiplication residue={(nonzero[0]*1000)%N}')
    print('PASS: all preimages under four modes and neighbouring input boundaries vs bounded original instructions')
    print('Arithmetic only; no claim caller can supply these values or that any provider behaves accordingly.')

if __name__=='__main__': main()
