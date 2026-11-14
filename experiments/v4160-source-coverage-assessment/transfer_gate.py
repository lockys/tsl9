"""Bounded first-gate projection for original memory transfer 0x19bf0.

The complete function inventory and branch offsets are checked before this
fixed-instruction projection; no memory access or later copying is performed.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original',HERE/'transfer_original.py')
original=importlib.util.module_from_spec(spec); spec.loader.exec_module(original)
MASK=0xffffffff


def gate(dst,src,length):
    dst&=MASK; src&=MASK; length&=MASK
    end=(dst+length)&MASK
    if (dst^src)&3: return 0x19c02,end
    if length>3: return 0x19c1a,end
    return 0x19c02,end


def main():
    image=original.mod.entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=original.mod.entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    evidence=json.loads(original.EVIDENCE.read_text(encoding='utf-8'))
    original.validate(image,next(x['operations'] for x in evidence['functions'] if x['start']==original.START))
    count=0
    for dst in range(16):
        for src in range(16):
            for length in range(65536):
                pc,end=gate(dst,src,length)
                if pc!=(0x19c1a if dst%4==src%4 and length>3 else 0x19c02) or end!=dst+length: raise ValueError('gate mismatch')
                count+=1
    for dst in (0,1,3,0xfffffffc,0xffffffff):
        for src in (0,1,3,0xfffffffc,0xffffffff):
            for length in (0,1,3,4,94,106,0xffffffff):
                pc,end=gate(dst,src,length)
                if pc!=(0x19c1a if dst%4==src%4 and length>3 else 0x19c02) or end!=((dst+length)&MASK): raise ValueError('boundary mismatch')
    for sp in range(16):
        for length,src in ((94,0x19d08),(106,0x19d68)):
            dst=(sp-124)&MASK
            pc,_=gate(dst,src,length)
            if pc!=(0x19c1a if sp%4==0 else 0x19c02): raise ValueError('caller alignment mismatch')
    print(f'PASS: {count} alignment/length cases, 175 wrap/boundary cases, 32 caller alignment cases')
    print('Lengths 94/106 with word-aligned incoming SP enter 0x19c1a; other SP alignments enter 0x19c02.')
    print('Fixed-encoding projection only; no copy, successful access, nonwrapping, reachability or hardware claim.')

if __name__=='__main__': main()
