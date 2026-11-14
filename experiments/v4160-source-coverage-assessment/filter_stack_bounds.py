"""Exact modular SP overlap ranges for the conservative filter store union.

Only memory addresses, not execution, accessibility, reachability, DMA,
interrupts, other callees, or side effects of MMIO are modeled.
"""
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('alias',HERE/'filter_callee_alias.py')
alias=importlib.util.module_from_spec(spec); spec.loader.exec_module(alias)
MASK=0xffffffff


def bad_sp(offset,length,union):
    return {(addr-offset-i)&MASK for addr in union for i in range(length)}


def intervals(values):
    result=[]
    for n in sorted(values):
        if not result or n!=result[-1][1]: result.append([n,n+1])
        else: result[-1][1]+=1
    return tuple(map(tuple,result))


def main():
    image=alias.audit.loop.calls.case.dispatch.IMAGE.read_bytes()
    alias.audit.scan(image); alias.verify_stores(image)
    union=alias.all_indices_stores()
    for offset,length in ((32,112),(12,20)):
        bad=bad_sp(offset,length,union)
        ranges=intervals(bad)
        print(f'offset={offset} size={length} unsafe SP intervals: '+', '.join(f'[{a:#x},{b:#x})' for a,b in ranges))
        # Independent direct shared-byte intersection, including every nearby
        # SP and controls near modular wrap.
        for sp in list(range(0x40005f00,0x40007000))+[0,1,0xffffff00,0xfffffff0,0xffffffff,0x20000f50]:
            direct=any(((sp+offset+i)&MASK) in union for i in range(length))
            if direct!=(sp in bad): raise ValueError('modular preimage mismatch')
        # Every bad-SP candidate is close to this finite union; offsets cannot
        # wrap the low endpoints, so no unsafe candidates occur outside sweep.
        if not bad.issubset(range(0x40005f00,0x40007000)): raise ValueError('unexpected modular wrap')
        for a,b in ranges:
            if a not in bad or b-1 not in bad or a-1 in bad or b in bad: raise ValueError('boundary mismatch')
    print('PASS: exact modular preimages, 8704 nearby SP checks, wrap controls and interval boundaries')
    print('Safe from these callee stores only; no assumption about external writes or physical address mapping.')

if __name__=='__main__': main()
