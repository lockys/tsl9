"""Conditional caller/filter stack geometry on the RV32 address ring.

Composes fixed instruction projections at a call boundary; neither provider
nor first caller callee is executed. SP, s0, s1 preservation is assumed.
"""
import importlib.util
from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file)
    obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
continuation=module('continuation','callee_12ad0_continuation.py')
entry=module('entry','filter_entry_128fe.py')
MASK=0xffffffff

def check(sp,n):
    # Original caller supplies [sp+4,sp+4+n), callee fill uses [sp-144,sp-32).
    source={(sp+4+i)&MASK for i in range(n)}
    workspace={(sp-144+i)&MASK for i in range(112)}
    saves={(sp-24+i)&MASK for i in range(24)}
    if source & workspace or saves & workspace or saves & source: raise ValueError('unexpected overlap')

def main():
    image=continuation.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=continuation.entry.calls.case.dispatch.SHA: raise ValueError('APP identity')
    for n in (94,106):
        # Translation on the modular ring is a bijection: one exact set
        # intersection covers all 2^32 possible SP values.
        check(0,n)
    for sp in (*range(0,65536,257),0xffffff70,0xffffff80,0xfffffff0,0xffffffff):
        for mode,n in ((1,94),(2,106)):
            call,_=continuation.run(image,mode,sp,0x1453c)
            mem={0x40048+i:0 for i in range(4)}
            first=entry.project(image,mem,sp,0x12b0a,0,0,0,0,0,call[1],n)
            if call[1]!=(sp+4)&MASK or first[1]!=(sp-144)&MASK: raise ValueError('boundary mismatch')
            check(sp,n)
    print('PASS: modular set proof for all 2^32 SP values, source lengths 94 and 106')
    print('PASS: 520 synthetic caller/entry compositions including wrap boundaries')
    print('Conditional on preserved call state and successful accesses; provider, interrupts and hardware not executed.')
if __name__=='__main__': main()
