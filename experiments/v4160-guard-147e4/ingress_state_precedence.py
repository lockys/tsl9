"""Original-byte state selector and next-state-gate precedence.

Segmented local projection. Entry at 0x89c8, successful reads where taken,
no concurrency, hardware, or whole-parser reachability is assumed.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE/'ingress_state_gate.py')
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
MASK=0xffffffff
EXPECTED=bytes.fromhex('63178703')

def branch(code,a4,s8):
    if len(code)!=4 or any(not 0<=value<=MASK for value in (a4,s8)): raise ValueError('invalid input')
    word=int.from_bytes(code,'little')
    op,f3,rs1,rs2=word&127,(word>>12)&7,(word>>15)&31,(word>>20)&31
    if op!=0x63 or f3!=1 or rs1!=14 or rs2!=24: raise ValueError('not the expected bne registers')
    imm=((word>>31&1)<<12)|((word>>7&1)<<11)|((word>>25&63)<<5)|((word>>8&15)<<1)
    offset=gate.signed(imm,13)
    return (0x89c8+offset)&MASK if a4!=s8 else 0x89cc

def check(code,gatecode,a4,s8,s9,halfword):
    pc=branch(code,a4,s8)
    if a4==s8:
        if pc!=0x89cc: raise ValueError('first state not prioritized')
        return
    if pc!=0x89f6: raise ValueError('state branch target mismatch')
    target,reads,a2,out_a4,trace=gate.run(gatecode,0x20004000,a4,s9,halfword,0x12345678)
    if a4!=s9:
        expected=(0x8a2a,[],0x12345678,a4,[0x89f6])
    else:
        expected=(0x8a4c if halfword>1039 else 0x8a06,[0x2000408a],halfword,1039,[0x89f6,0x89fa,0x89fe,0x8a02])
    if (target,reads,a2,out_a4,trace)!=expected: raise ValueError('next state mismatch')

def main():
    image=gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x89c8-0x8000:0x89cc-0x8000]; gatecode=image[0x89f6-0x8000:0x8a06-0x8000]
    if code!=EXPECTED or gatecode!=gate.EXPECTED: raise ValueError('original bytes mismatch')
    for a4 in range(256):
        for s8 in range(256):
            for s9 in (a4,(a4+1)&255): check(code,gatecode,a4,s8,s9,1039)
    for a4 in (0,1,255,256,MASK):
        for s8 in (0,1,255,256,MASK):
            for s9 in (a4,(a4+1)&MASK):
                for halfword in (0,1039,1040,65535): check(code,gatecode,a4,s8,s9,halfword)
    for i in range(4):
        changed=bytearray(code); changed[i]^=1
        try:
            check(changed,gatecode,5,6,5,1039)
        except ValueError: continue
        raise ValueError(f'undetected selector byte mutation {i}')
    print('PASS: 131072 byte-state cases, 200 full-register boundary cases, 4 selector mutations')
    print('When a4 equals both s8 and s9, the first branch reaches 0x89cc, not the 0x89f6 gate.')
    print('Segmented projections; no continuous CPU or hardware validation.')

if __name__=='__main__': main()
