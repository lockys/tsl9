"""Conditional alias geometry for the reference providers' word access.

The numeric address is an observed reference instruction operand, not an
assertion about the real device or semantics of the peripheral.
"""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('stack',HERE/'filter_stack_disjoint.py')
stack=importlib.util.module_from_spec(spec); spec.loader.exec_module(stack)
MASK=0xffffffff
TARGET=0x4002420c

def interval_for_sp(offset,length):
    # Intersection with [TARGET,TARGET+4), in the 32-bit address ring.
    return ((TARGET-offset-length+1)&MASK,(TARGET+3-offset)&MASK)

def intersects(sp,offset,length):
    return any(((sp+offset+i)&MASK) in range(TARGET,TARGET+4) for i in range(length))

def main():
    image=stack.continuation.entry.calls.case.dispatch.IMAGE.read_bytes()
    import hashlib
    if hashlib.sha256(image).hexdigest()!=stack.continuation.entry.calls.case.dispatch.SHA: raise ValueError('APP identity')
    for label,offset,length in (('workspace',-144,112),('source94',4,94),('source106',4,106),('callee saves',-24,24)):
        lo,hi=interval_for_sp(offset,length)
        if lo>hi: raise ValueError('unexpected wrapped test interval')
        for sp in range(lo-4,hi+5):
            if intersects(sp,offset,length)!=(lo<=sp<=hi): raise ValueError('bad overlap boundary')
        for sp in (0,1,0xfffffff0,0xffffffff,0x20001000):
            if intersects(sp,offset,length)!=(lo<=sp<=hi): raise ValueError('bad wrap boundary')
        print(f'PASS {label}: SP 0x{lo:08x}..0x{hi:08x} inclusive can overlap word 0x{TARGET:08x}; {hi-lo+1} values')
    print('Range geometry only; MMIO mappings, alignment, provider installation and execution unknown.')
if __name__=='__main__': main()
