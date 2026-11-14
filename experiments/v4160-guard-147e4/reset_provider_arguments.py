"""Conditionally derive provider buffer arguments from original reset and APP.

Requires the runtime gp to remain equal to its reset value; provider pointer,
side effects, return behavior, memory mapping and hardware remain unknown.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
reset=load('reset',HERE/'reset_gp_disjoint.py'); setup=load('setup',HERE/'provider_setup_10032.py'); callback=load('callback',HERE.parent/'v4160-dispatch-148b4-model'/'callback_sequence.py')


def main():
    image=setup.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=setup.entry.SHA: raise ValueError('firmware identity mismatch')
    initial=image[0x186aa-0x8000:0x186b2-0x8000]
    if initial!=bytes.fromhex('97c1fe1f93816195'): raise ValueError('reset bytes mismatch')
    gp=reset.reset_gp(initial)
    if gp!=0x20004000: raise ValueError('startup gp mismatch')
    code=image[0x10032-0x8000:0x10044-0x8000]
    if code!=setup.EXPECTED: raise ValueError('provider setup bytes mismatch')
    for pointer in range(65536):
        target,ra,a0,a1,a2,reads,_=setup.run(code,gp,0x10712,pointer)
        if (target,ra,a0,a1,a2,reads)!=(pointer&~1,0x10712,0x2000412c,0,3,[0x40048]): raise ValueError('first provider boundary mismatch')
    for seed in (0,0x55555555,0xffffffff):
        events,_,_,_=callback.run(image,0x1234,2,seed)
        if events[0][0]!=0x10032 or events[2][1:4]!=(0x2000bfb8,0,12): raise ValueError('callback boundary mismatch')
    first=set(range(0x2000412c,0x2000412f)); second=set(range(0x2000bfb8,0x2000bfc4)); payload=set(range(0x2000b9d8,0x2000bde8))
    if first&second or first&payload or second&payload: raise ValueError('range overlap')
    print('PASS: 65536 first provider pointers and 3 callback traces; supplied ranges are pairwise disjoint if gp=0x20004000')
    print('This checks call arguments, not actual provider access widths or writes; no device execution.')

if __name__=='__main__': main()
