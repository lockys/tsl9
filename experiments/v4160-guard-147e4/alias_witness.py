"""Conditional byte-alias witness for the 0x1070a -> 0x14800 boundary.

Segments use successful synthetic accesses and stubbed callees. This does not
establish that the device can supply the selected pointer, that all callees
return, or that their actual side effects preserve the two-byte input.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent; OTHER=HERE.parent/'v4160-dispatch-148b4-model'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
prefix=load('prefix',OTHER/'payload_gate.py'); predecessor=load('predecessor',OTHER/'predecessor.py'); callback=load('callback',OTHER/'callback_sequence.py')


def run(image,base,initial):
    if len(initial)!=4 or initial[:2]!=bytes.fromhex('ffff'): raise ValueError('expected four-byte witness')
    memory={(base+i)&0xffffffff:v for i,v in enumerate(initial)}
    pc,reads,_,regs=prefix.run(image,20,memory[base],memory[(base+1)&0xffffffff],base,0x1234)
    if pc!=0x147f8 or reads!=[base,(base+1)&0xffffffff] or (regs[10],regs[11])!=(0x1234,2): raise ValueError('prefix mismatch')
    before=memory[(base+2)&0xffffffff] | memory[(base+3)&0xffffffff]<<8
    _,preserved,_,writes=callback.run(image,0x1234,2,0,(base,0x1234,20))
    if preserved!=(0x14800,0x20002000,base,0x1234,20) or writes!=[(0x2000bfb8,0)]: raise ValueError('callback boundary mismatch')
    # Input memory is the only modeled alias. Other storage and stub effects are separate.
    for address,value in writes:
        if address in memory: memory[address]=value
    after=memory[(base+2)&0xffffffff] | memory[(base+3)&0xffffffff]<<8
    window=image[0xc800:0xc812]
    if window!=bytes.fromhex('8357240005676384e70209676386e70285ef'): raise ValueError('precheck bytes mismatch')
    before_pc,before_addr=predecessor.run(window,before,base)
    after_pc,after_addr=predecessor.run(window,after,base)
    if before_addr != (base+2)&0xffffffff or after_addr!=before_addr: raise ValueError('wrong input address')
    return before,after,before_pc,after_pc


def main():
    image=prefix.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=prefix.SHA: raise ValueError('firmware identity mismatch')
    if run(image,0x2000bfb6,bytes.fromhex('ffff0100')) != (1,0,0x14848,0x14812): raise ValueError('alias witness mismatch')
    if run(image,0x20001000,bytes.fromhex('ffff0100')) != (1,1,0x14848,0x14848): raise ValueError('disjoint control mismatch')
    for value in range(256):
        before,after,bpc,apc=run(image,0x2000bfb6,bytes((255,255,value,0)))
        if (before,after,bpc,apc)!=(value,0,0x14812 if value==0 else 0x14848,0x14812): raise ValueError('low-byte alias mismatch')
    for value in range(256):
        before,after,bpc,apc=run(image,0x2000bfb5,bytes((255,255,0,value)))
        expected_pc=0x14812 if value==0 else 0x1482e if value==0x10 else 0x14838 if value==0x20 else 0x14848
        if (before,after,bpc,apc)!=(value<<8,0,expected_pc,0x14812): raise ValueError('high-byte alias mismatch')
    print('PASS: 512 low/high-byte alias cases and disjoint control; 0x0001 -> 0x0000 changes precheck 0x14848 -> 0x14812')
    print('Conditional synthetic memory only; callback callees are stubs, no device reachability claim.')

if __name__=='__main__': main()
