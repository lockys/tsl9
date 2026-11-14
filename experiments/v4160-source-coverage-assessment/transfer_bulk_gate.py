"""Unsigned bulk-loop gate projection at 0x19c34..0x19c40.

Only arithmetic is modeled, after an assumed successful alignment phase.
A synthetic address is not evidence that target hardware can access it.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original',HERE/'transfer_original.py')
original=importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
spec_gate=importlib.util.spec_from_file_location('entry_gate',HERE/'transfer_gate.py')
entry_gate=importlib.util.module_from_spec(spec_gate); spec_gate.loader.exec_module(entry_gate)
MASK=0xffffffff


def gate(end,cursor):
    end &= MASK; cursor &= MASK
    aligned_end=end & 0xfffffffc
    threshold=(aligned_end-32)&MASK
    return aligned_end,threshold,0x19c9c if threshold<=cursor else 0x19c40


def main():
    image=original.mod.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=original.mod.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    evidence=json.loads(original.EVIDENCE.read_text(encoding='utf-8'))
    original.validate(image,next(x['operations'] for x in evidence['functions'] if x['start']==original.START))
    cases=0
    for cursor in range(0x1000,0x1100,4):
        for length in range(0,1025):
            end=cursor+length
            aligned,threshold,target=gate(end,cursor)
            words=length//4
            if (aligned,threshold)!=(cursor+4*words,cursor+4*words-32): raise ValueError('threshold mismatch')
            if target!=(0x19c40 if words>8 else 0x19c9c): raise ValueError('gate mismatch')
            cases+=1
    # Unsigned subtract wraps for aligned end below 32.
    for end in range(32):
        aligned,threshold,target=gate(end,0)
        if aligned!=(end&~3) or threshold!=((aligned-32)&MASK) or target!=0x19c40: raise ValueError('underflow mismatch')
    for cursor in (0,4,28,32,0xffffffd8,0xfffffffc,0xffffffff):
        for end in (0,3,28,31,32,35,0xfffffffc,0xffffffff):
            aligned,threshold,target=gate(end,cursor)
            if target!=(0x19c9c if threshold<=cursor else 0x19c40): raise ValueError('unsigned mismatch')
    # The entry's byte-count condition is met for dst=0, src=4, len=4,
    # but no claim is made that address 0 or 4 is accessible on hardware.
    if entry_gate.gate(0,4,4)!=(0x19c1a,4) or gate(4,0)!=(4,0xffffffe4,0x19c40): raise ValueError('underflow witness mismatch')
    print(f'PASS: {cases} nonwrapping gate cases, 32 threshold-underflow cases, 56 unsigned boundaries')
    print('Aligned synthetic dst=0 src=4 length=4 reaches a wrapped threshold 0xffffffe4; the gate selects a bulk step.')
    print('No memory access, actual mapped-address validity, full loop, interrupts or hardware execution claimed.')

if __name__=='__main__': main()
