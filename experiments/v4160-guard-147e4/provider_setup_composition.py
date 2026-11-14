"""Reconstruct the 0x1070a -> 0x10032 opaque-provider boundary.

No continuous CPU execution: the 0x10032 segment is substituted at the
callback model's first stub boundary. Both provider pointer reads, all other
callees and provider side effects remain independent external assumptions.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent; OTHER=HERE.parent/'v4160-dispatch-148b4-model'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
setup=load('setup',HERE/'provider_setup_10032.py'); callback=load('callback',OTHER/'callback_sequence.py')
MASK=0xffffffff


def main():
    image=setup.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=setup.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x10032-0x8000:0x10044-0x8000]
    if code!=setup.EXPECTED or image[0x1070a-0x8000:0x10712-0x8000]!=setup.CALLER: raise ValueError('original bytes mismatch')
    if setup.entry.jal_target(0x1070e,setup.entry.read_at(image,0x1070e,4))!=0x10032: raise ValueError('wrong initial call')
    count=0
    for gp in tuple(range(4096))+(0x2000be8c,0xfffffed4,MASK):
        for pointer in (0,1,0x13572468,MASK):
            events,preserved,stack,writes=callback.run(image,0x1234,2,gp,(0x20001000,0x1234,20))
            if events[0][0]!=0x10032 or events[0][1:3]!=(0x1234,2) or events[0][4]!=0x10712: raise ValueError('first boundary mismatch')
            dest,ra,a0,a1,a2,reads,trace=setup.run(code,gp,events[0][4],pointer)
            if (dest,ra,a0,a1,a2,reads,trace)!=(pointer&~1,0x10712,(gp+300)&MASK,0,3,[0x40048],[0x10032,0x10036,0x1003a,0x1003c,0x1003e,0x10042]): raise ValueError('provider setup mismatch')
            if events[2][0]!=0x13572468 or events[2][1:4]!=(0x2000bfb8,0,12): raise ValueError('second provider boundary mismatch')
            if preserved!=(0x14800,0x20002000,0x20001000,0x1234,20) or writes!=[(0x2000bfb8,0)] or stack!={0x20001ffc:0x14800}: raise ValueError('post-callback projection mismatch')
            count+=1
    # This equality is an address calculation only, not evidence of the real gp.
    if setup.run(code,0x2000be8c,0x10712,0x13572468)[2] != 0x2000bfb8:
        raise ValueError('illustrative gp address mismatch')
    print(f'PASS: {count} reconstructed callback/provider boundary cases, including distinct first and second provider pointers')
    print('All provider and other callee returns/side effects are assumptions; no hardware or continuous execution.')

if __name__=='__main__': main()
