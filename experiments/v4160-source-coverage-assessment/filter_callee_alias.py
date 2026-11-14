"""Address-set check for the filter caller and 0x18ba2's stores.

Conditional on the byte actually read by the callee being 0..13 and standard
32-bit arithmetic; a prior aliased store could change that byte, so this is not
an unconditional complete store set. Addresses do not establish mapping,
accepted writes or stable MMIO.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audit',HERE/'filter_callee_registers.py')
audit=importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)
MASK=0xffffffff
FIXED=(0x40006600,0x40006604,0x4000660c,0x40006614,0x4000661c)


def byte_set(starts,size):
    return {(addr+i)&MASK for addr in starts for i in range(size)}


def writes(index):
    if not 0<=index<14: raise ValueError('index outside caller sequence')
    # Conservative union: mutually exclusive branches are intentionally merged.
    return byte_set((*FIXED,0x40006640+8*index,0x40006644+8*index),4)


def classify(sp):
    sp&=MASK
    source=byte_set(((sp+32)&MASK,),112)
    descriptor=byte_set(((sp+12)&MASK,),20)
    all_stores=set().union(*(writes(i) for i in range(14)))
    return source&all_stores,descriptor&all_stores


def main():
    image=audit.loop.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=audit.loop.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    audit.scan(image)
    for i in range(14):
        if len(writes(i))!=28: raise ValueError('unexpected overlapping store words')
    # Independent interval test in a non-wrapping sweep around the peripheral.
    for sp in range(0x40000000,0x40010000):
        actual=classify(sp)
        starts=[*FIXED]+[0x40006640+4*i for i in range(28)]
        expected=[]
        for offset,size in ((32,112),(12,20)):
            expected.append({x for a in starts for x in range(a,a+4) if sp+offset<=x<sp+offset+size})
        if actual!=tuple(expected): raise ValueError('interval comparison failed')
    source,descriptor=classify(0x40006620)
    if 0x40006640 not in source or descriptor: raise ValueError('source overlap witness failed')
    source,descriptor=classify(0x400065f4)
    if 0x40006600 not in descriptor: raise ValueError('descriptor overlap witness failed')
    for sp in (0,0x20000f50,0xffffff80,0xfffffff0,0xffffffff):
        source,descriptor=classify(sp)
        if source or descriptor: raise ValueError('unexpected control overlap')
    print('PASS: 65536 stack addresses, 14 index store unions, two overlap witnesses and five controls')
    print('When the callee actually reads index 0..13, potential writes overlap source at synthetic sp=0x40006620.')
    print('Prior aliased writes can change the index; no unconditional store-set completeness is claimed.')
    print('Address intersection only; no assertion that peripheral memory is ordinary RAM or the witness is reachable.')

if __name__=='__main__': main()
