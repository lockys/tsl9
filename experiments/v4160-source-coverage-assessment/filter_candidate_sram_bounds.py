"""Conditional filter stack containment in a 64-KiB candidate address range.

This is address arithmetic, not a physical RAM or actual-SP assertion.
"""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bounds',HERE/'filter_reference_mmio_bounds.py')
bounds=importlib.util.module_from_spec(spec); spec.loader.exec_module(bounds)
LOW,HIGH=0x20000000,0x20010000


def valid(sp,n):
    # workspace [sp-144,sp-32), saved callee words [sp-24,sp),
    # and source [sp+4,sp+4+n), all inside a candidate SRAM interval.
    return LOW<=sp-144 and sp+4+n<=HIGH


def main():
    for n in (94,106):
        lo=LOW+144; hi=HIGH-4-n
        for sp in (lo-1,lo,lo+1,hi-1,hi,hi+1):
            if valid(sp,n)!=(lo<=sp<=hi): raise ValueError('containment mismatch')
        aligned_first=(lo+15)&~15; aligned_last=hi&~15
        for offset,length in ((-144,112),(4,n),(-24,24)):
            mlo,mhi=bounds.interval_for_sp(offset,length)
            if not (hi<mlo or lo>mhi): raise ValueError('candidate SRAM and MMIO overlap')
        print(f'PASS length {n}: candidate-contained SP 0x{lo:08x}..0x{hi:08x} inclusive; {(aligned_last-aligned_first)//16+1} 16-byte-aligned values; no numerical overlap with reference MMIO word')
    print('Conditional candidate SRAM only; actual physical capacity, mapping, stack usage and provider not established.')
if __name__=='__main__': main()
