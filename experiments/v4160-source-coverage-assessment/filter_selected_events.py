"""Selected-path MMIO event projection, conditional on a stable descriptor.

This models successful volatile reads as six independent supplied values. It
neither executes original instructions nor asserts any physical MMIO effects.
"""
import importlib.util
from pathlib import Path
import random

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('route',HERE/'filter_descriptor_route.py')
route=importlib.util.module_from_spec(spec); spec.loader.exec_module(route)
MASK=0xffffffff


def project7(index,fields,reads):
    if not 0<=index<14 or len(fields)!=4 or len(reads)!=7: raise ValueError('invalid input')
    if any(not 0<=v<=65535 for v in fields) or any(not 0<=v<=MASK for v in reads): raise ValueError('out of range')
    base=0x40006400; mask=1<<index; inv=(~mask)&MASK
    ctl,active,scale,mode,fifo,active2,_=reads
    # The final control read is independent of the first control write.
    fr1=(fields[3]<<16)|fields[1]; fr2=(fields[2]<<16)|fields[0]
    return ((base+512,ctl|1),(base+540,active&inv),(base+524,scale&inv),
            (base+576+index*8,fr1),(base+580+index*8,fr2),
            (base+516,mode|mask),(base+532,fifo&inv),
            (base+540,active2|mask),(base+512,reads[6]&0xfffffffe))


def main():
    image=route.A.audit.loop.calls.case.dispatch.IMAGE.read_bytes()
    route.flow.flow(image)
    rng=random.Random(0x4160); checks=0
    for index in range(14):
        for _ in range(1024):
            fields=tuple(rng.randrange(65536) for _ in range(4)); reads=tuple(rng.getrandbits(32) for _ in range(7))
            events=project7(index,fields,reads); mask=1<<index
            addrs=[0x40006600,0x4000661c,0x4000660c,0x40006640+8*index,0x40006644+8*index,0x40006604,0x40006614,0x4000661c,0x40006600]
            if [a for a,_ in events]!=addrs: raise ValueError('event order or address')
            values=[reads[0]|1,reads[1]&~mask,reads[2]&~mask,(fields[3]<<16)|fields[1],(fields[2]<<16)|fields[0],reads[3]|mask,reads[4]&~mask,reads[5]|mask,reads[6]&~1]
            if [v for _,v in events]!=values: raise ValueError('value mismatch')
            checks+=1
    for index in range(14):
        # Cross-check how caller fills the fields and the four path decisions.
        fields,_,_,_,_,_,path,_=route.describe(image,0x20001000,(1,2,3,4),index)
        if fields!=(32,64,96,128) or path!=(0x18bd4,0x18c8a,0x18c2a,0x18c3c): raise ValueError('route mismatch')
    try: project7(14,(0,0,0,0),(0,)*7)
    except ValueError: pass
    else: raise ValueError('invalid index accepted')
    print(f'PASS: {checks} projected write sequences; 14 caller descriptor/route cases')
    print('Seven MMIO reads are independent; no provider or physical MMIO is executed.')

if __name__=='__main__': main()
