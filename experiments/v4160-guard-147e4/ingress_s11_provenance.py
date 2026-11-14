"""Conditionally bind ingress length pointer to gp+142 at 0x8934.

The setup and length initialization are segmented, not continuous CPU
execution. The conclusion requires s11 and gp to remain unchanged between
those boundaries, successful accesses, and no intervening writes.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('init',HERE/'ingress_length_initialize.py')
init=importlib.util.module_from_spec(spec); spec.loader.exec_module(init)
MASK=0xffffffff
EXPECTED=bytes.fromhex('938de108')

def pointer(code,gp):
    if len(code)!=4 or not 0<=gp<=MASK: raise ValueError('invalid input')
    w=int.from_bytes(code,'little')
    if (w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31)!=(0x13,27,0,3): raise ValueError('not addi s11,gp')
    return (gp+init.gate.signed(w>>20,12))&MASK

def check(code,gp):
    p=pointer(code,gp)
    if p!=(gp+142)&MASK: raise ValueError('pointer mismatch')
    counter={(gp+138+i)&MASK for i in range(2)}
    length={(p+i)&MASK for i in range(2)}
    if counter & length: raise ValueError('counter overlaps length')

def main():
    image=init.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=init.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x8934-0x8000:0x8938-0x8000]
    body=image[0x89cc-0x8000:0x89da-0x8000]
    if code!=EXPECTED or body!=init.EXPECTED: raise ValueError('original bytes mismatch')
    for gp in range(65536): check(code,gp)
    for gp in (0,0xffffff70,0xffffff72,0xffffff73,0xffffff74,0xffffff75,0xffffff76,0xffffffff): check(code,gp)
    for length in range(65536):
        gp=0x20004000; p=pointer(code,gp); memory={}
        init.put(memory,(gp+138)&MASK,2,0xffff); init.put(memory,p,2,length)
        value,events=init.run(body,gp,p,0,memory)
        if value!=length or events[1] != ('read',p,2,length): raise ValueError('length affected by counter clear')
    for i in range(4):
        altered=bytearray(code); altered[i]^=1
        try: check(altered,0x20004000)
        except ValueError: continue
        raise ValueError(f'undetected byte mutation {i}')
    print('PASS: 65536 gp values, 8 wrap boundaries, 65536 counter/length cases, 4 mutations')
    print('Conditional on stable gp and s11, s11=gp+142 is disjoint from counter gp+138.')
    print('Not a continuous CPU trace, proof of register stability, or hardware validation.')

if __name__=='__main__': main()
