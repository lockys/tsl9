"""Bounded projection of ingress index increment and loop comparison.

The increment/branch boundaries are composed, not a continuous CPU emulator.
State processing is assumed to return to 0x897e without changing s0/s2.
No trap, interrupt, memory failure, or hardware behavior is inferred.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
loop=load('loop',HERE/'ingress_loop_provenance.py')
MASK=0xffffffff
EXPECTED=bytes.fromhex('050465bf')

def increment(code,s0):
    if len(code)!=4 or not 0<=s0<=MASK: raise ValueError('invalid input')
    h=int.from_bytes(code[:2],'little')
    if h&3!=1 or h>>13!=0: raise ValueError('expected c.addi')
    rd=(h>>7)&31; imm=((h>>12&1)<<5)|((h>>2)&31)
    if rd!=8: raise ValueError('unexpected increment register')
    result=(s0+loop.prov.gate.signed(imm,6))&MASK
    h=int.from_bytes(code[2:],'little')
    if h&3!=1 or h>>13!=5: raise ValueError('expected c.j')
    imm=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
    pc=0x8980+loop.prov.gate.signed(imm,12)
    return result,pc

def check(code,s0):
    result=increment(code,s0)
    if result!=((s0+1)&MASK,0x8938): raise ValueError('increment mismatch')

def main():
    image=loop.prov.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=loop.prov.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x897e-0x8000:0x8982-0x8000]
    prefix={pc:image[pc-0x8000:pc-0x8000+len(x)] for pc,x in loop.EXPECTED.items()}
    selectors={pc:image[pc-0x8000:pc-0x8000+len(x)] for pc,x in loop.prov.EXPECTED.items()}
    if code!=EXPECTED or prefix!=loop.EXPECTED or selectors!=loop.prov.EXPECTED: raise ValueError('original bytes mismatch')
    for value in range(65536): check(code,value)
    for value in (0xffff,0x10000,0x7fffffff,0xfffffffe,MASK): check(code,value)
    for i in range(4):
        altered=bytearray(code); altered[i]^=1
        try: check(altered,0xffff)
        except ValueError: continue
        raise ValueError(f'undetected byte mutation {i}')
    # Initial s0=0; compare is unsigned low16(s0) < full s2.
    for bound,expected_steps in ((0,0),(1,1),(65535,65535)):
        s0=0; steps=0
        while True:
            target,_,_,_=loop.run(prefix,selectors,0x20004000,s0,bound,0x20001000,0,0,(1,2,3,4))
            if target==0x8942: break
            if target!=0x8970: raise ValueError('unexpected synthetic state path')
            s0,pc=increment(code,s0); steps+=1
            if pc!=0x8938 or steps>65536: raise ValueError('bounded run did not exit')
        if steps!=expected_steps: raise ValueError('bound mismatch')
    for bound in (65536,MASK):
        s0=0
        for _ in range(65536):
            target,_,_,_=loop.run(prefix,selectors,0x20004000,s0,bound,0x20001000,0,0,(1,2,3,4))
            if target!=0x8970: raise ValueError('unexpected exit')
            s0,pc=increment(code,s0)
        if s0!=65536 or pc!=0x8938: raise ValueError('low16 wrap mismatch')
        target,_,reads,_=loop.run(prefix,selectors,0x20004000,s0,bound,0x20001000,0,0,(1,2,3,4))
        if target!=0x8970 or reads[-1]!=0x20011000: raise ValueError('full-width address mismatch')
    print('PASS: 65536 increments, 5 boundaries, 4 byte mutations; bounded runs at 0,1,65535,65536,0xffffffff')
    print('For s2>65535, low16 comparison does not exit in 65536 steps; full s0 and payload address advance.')
    print('Conditional on every state step returning and successful accesses; no actual infinite loop claim.')

if __name__=='__main__': main()
