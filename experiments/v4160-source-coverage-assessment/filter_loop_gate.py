"""Conditional loop gate at 0x1298a, after the unknown callee returns.

No assumption is made about the real callee's ABI; register preservation is
an explicit condition in the fourteen-iteration composition below.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('loop',HERE/'filter_loop_step.py')
loop=importlib.util.module_from_spec(spec); spec.loader.exec_module(loop)
MASK=0xffffffff
INIT=bytes.fromhex('8144054a85493949')
BRANCH=bytes.fromhex('e39e24fb')


def branch(image,s1,s2):
    init=image[0x1293e-0x8000:0x12946-0x8000]
    if init!=INIT: raise ValueError('init instruction mismatch')
    decoded=[]
    for i in range(0,len(init),2):
        ins=int.from_bytes(init[i:i+2],'little')
        if ins&0xe003!=0x4001: raise ValueError('not c.li')
        imm=((ins>>2)&31)|(((ins>>12)&1)<<5)
        if imm&32: imm-=64
        decoded.append(((ins>>7)&31,imm))
    if decoded!=[(9,0),(20,1),(19,1),(18,14)]: raise ValueError('init operands mismatch')
    raw=image[0x1298a-0x8000:0x1298e-0x8000]
    if raw!=BRANCH: raise ValueError('branch instruction mismatch')
    word=int.from_bytes(raw,'little')
    if (word&127, (word>>12)&7,(word>>15)&31,(word>>20)&31)!=(0x63,1,9,18): raise ValueError('not bne s1,s2')
    imm=((word>>31)&1)<<12|((word>>7)&1)<<11|((word>>25)&63)<<5|((word>>8)&15)<<1
    if imm&4096: imm-=8192
    target=(0x1298a+imm)&MASK
    if target!=0x12946: raise ValueError('incorrect target')
    return target if (s1&MASK)!=(s2&MASK) else 0x1298e


def main():
    image=loop.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=loop.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    for x in range(65536):
        for y in (x, x^1,14):
            result=branch(image,x,y)
            if result!=(0x1298e if x==y else 0x12946): raise ValueError('gate mismatch')
    # The tested post-call path assumes each callee returns and preserves the
    # live sp/s0/s1/s2/s3/s4 and relevant input memory; it is not an ABI proof.
    mem={0x1000+i:i&255 for i in range(112)}
    s0=0x1000; s1=0; visits=[]
    while True:
        result=loop.step(image,mem,0x2000,s0,s1,1,1)
        visits.append((s0,s1)); s0,s1=result[3:5]
        if branch(image,s1,14)==0x1298e: break
        if len(visits)>=256: raise ValueError('unexpected wrap')
    if len(visits)!=14 or s0!=0x1070 or s1!=14: raise ValueError('iteration count mismatch')
    if visits!=[(0x1000+8*i,i) for i in range(14)]: raise ValueError('iteration sequence mismatch')
    # Changed s2 may make the 8-bit counter incapable of reaching the exit.
    if any(branch(image,x,256)!=0x12946 for x in range(256)): raise ValueError('counter width mismatch')
    for address in list(range(0x1293e,0x12946))+list(range(0x1298a,0x1298e)):
        bad=bytearray(image); bad[address-0x8000]^=1
        try: branch(bad,0,14)
        except ValueError: continue
        raise ValueError('mutation accepted')
    print('PASS: 196608 gate comparisons, 14 conditional iterations, 256 changed-s2 checks, 12 byte mutations')
    print('Fourteen iterations require normal return and preservation of live state and input; callee is not executed.')

if __name__=='__main__': main()
