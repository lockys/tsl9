"""Projection after first 0x128fe provider returns through second call.

All registers are then-live inputs; no claim the first provider preserves them.
Provider word is synthetic, loads successful, and no external callee executes.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('entry',HERE/'case01_callee_entry.py')
entry=importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)
START=0x12920
CODE=bytes.fromhex('930700071306000763e487001376f40fb7070400fc47a68508108297')
MASK=0xffffffff


def project(image,sp,s0,s1,provider):
    if image[START-0x8000:START-0x8000+len(CODE)]!=CODE: raise ValueError('instruction mismatch')
    if entry.branch(0x12928,CODE[8:12])!=0x12930: raise ValueError('branch target mismatch')
    sp&=MASK; s0&=MASK; s1&=MASK; provider&=MASK
    a2=112 if s0>112 else s0&255
    return provider&0xfffffffe,(sp+32)&MASK,s1,a2,0x1293c


def main():
    image=entry.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=entry.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    for s0 in range(65536):
        result=project(image,0x20000f50,s0,0x12345678,0x12345679)
        if result!=(0x12345678,0x20000f70,0x12345678,min(s0,112),0x1293c): raise ValueError('cap mismatch')
    cases=0
    for sp in (0,1,0xffffffe0,0xffffffff):
        for s0 in (0,1,111,112,113,255,256,0xffffffff):
            for s1 in (0,0x12345678,0xffffffff):
                for provider in (0,1,0x40000001,0xffffffff):
                    result=project(image,sp,s0,s1,provider)
                    if result!=(provider&0xfffffffe,(sp+32)&MASK,s1,min(s0,112),0x1293c): raise ValueError('boundary mismatch')
                    cases+=1
    for i in range(len(CODE)):
        bad=bytearray(image); bad[START-0x8000+i]^=1
        try: project(bad,0,0,0,0)
        except ValueError: continue
        raise ValueError('mutation accepted')
    print(f'PASS: 65536 s0 values, {cases} full-width boundary cases, {len(CODE)} instruction-byte mutations')
    print('From then-live state, indirect slot 0x4004c is called with (sp+32, s1, min_unsigned(s0,112)).')
    print('Prior provider may alter state and slot; target identity, effects, reachability and hardware unverified.')

if __name__=='__main__': main()
