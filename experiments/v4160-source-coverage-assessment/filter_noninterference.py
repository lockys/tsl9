"""Conservative synthetic composition of the caller with arbitrary bounded writes.

This is not an emulator or a callee MMIO model. It assumes successful accesses,
normal callee returns, preserved registers, and no outside agents. At each call
we adversarially overwrite *every* byte in the previously proven store union.
"""
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bounds',HERE/'filter_stack_bounds.py')
bounds=importlib.util.module_from_spec(spec); spec.loader.exec_module(bounds)
A=bounds.alias; MASK=0xffffffff
spec=importlib.util.spec_from_file_location('gate',HERE/'filter_loop_gate.py')
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)


def run(image,sp):
    sp&=MASK; union=A.all_indices_stores()
    source={(sp+32+i)&MASK for i in range(112)}
    desc={(sp+12+i)&MASK for i in range(20)}
    if source&desc or source&union or desc&union: raise ValueError('unsafe stack')
    mem={addr:((i*29+17)&255) for i,addr in enumerate(sorted(source))}
    reference={addr:mem[addr] for addr in source}
    s0=(sp+32)&MASK; s1=0
    for iteration in range(14):
        result=A.audit.loop.step(image,mem,sp,s0,s1,1,1)
        # Deliberately more permissive than the true callee: overwrite the
        # entire union, allowing arbitrary values on every iteration.
        for addr in union: mem[addr]=(iteration*13+addr)&255
        if any(mem[addr]!=value for addr,value in reference.items()): raise ValueError('source changed')
        s0,s1=result[3:5]
        if s1!=iteration+1 or s0!=(sp+32+8*(iteration+1))&MASK: raise ValueError('iteration mismatch')
        if gate.branch(image,s1,14)!=(0x1298e if iteration==13 else 0x12946): raise ValueError('gate mismatch')
    return s0,s1


def main():
    image=A.audit.loop.calls.case.dispatch.IMAGE.read_bytes()
    A.audit.scan(image); A.verify_stores(image)
    union=A.all_indices_stores()
    if len(union)!=2068: raise ValueError('unexpected union')
    import importlib.util as util
    spec=util.spec_from_file_location('baseflow',HERE/'filter_callee_baseflow.py')
    baseflow=util.module_from_spec(spec); spec.loader.exec_module(baseflow)
    observed,_=baseflow.flow(image)
    for expressions in observed.values():
        c,k=next(iter(expressions))
        for index in range(256):
            if not A.byte_set(((c+k*index)&MASK,),4)<=union: raise ValueError('union incomplete')
    # Fixed pseudo-random SPs plus wrap examples, rejecting overlap explicitly.
    sps=[0,0xffffff80,0xfffffff0,0xffffffff,0x20000f50]
    x=0x12345678
    while len(sps)<128:
        x=(1664525*x+1013904223)&MASK
        if not any(A.classify_all(x)): sps.append(x)
    for sp in sps:
        if run(image,sp)!=((sp+144)&MASK,14): raise ValueError('final state mismatch')
    for sp in (0x40006620,0x40006e00):
        try: run(image,sp)
        except ValueError as exc:
            if str(exc)!='unsafe stack': raise
        else: raise ValueError('unsafe witness accepted')
    print('PASS: 128 synthetic SPs x 14 iterations, arbitrary whole-union writes, two unsafe witnesses')
    print('Conditionally preserves the 112-byte source and counter under stronger-than-callee writes.')
    print('No physical MMIO, callee, exceptions, concurrent agents, or reachability is modeled.')

if __name__=='__main__': main()
