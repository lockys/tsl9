"""Conditional cross-image composition of WCH reference candidate and APP.

Not a continuous CPU: this stitches synthetic call boundaries. Both images
are hash-pinned; callback stub returns normally and preserves s0/SP/stack.
Assumes successful memory accesses, stable state/gp, no relevant aliases or
concurrency, and that this candidate is the installed resident (not proven).
The state-zero gate is entered directly after a reset; intervening control flow
and nonzero input length are assumed, not executed.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
candidate=load('candidate',HERE/'resident_clock_candidates.py')
gap=load('gap',HERE/'clock_gap_composition.py')
start=load('start',HERE/'clock_gap_start_composition.py')
MASK=0xffffffff

def main():
    image=gap.clock.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gap.clock.gate.entry.SHA: raise ValueError('APP identity mismatch')
    read=lambda mapping:{pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in mapping.items()}
    wrapper=read(gap.clock.EXPECTED); gapcode=read(gap.EXPECTED); startcode=read(start.EXPECTED)
    tested=0
    for name,path,digest,entry,cb,ctr,hexbytes in candidate.CANDIDATES:
        file=candidate.ROOT/path
        if not file.exists(): print(f'SKIP: {name} reference carrier unavailable'); continue
        data=file.read_bytes(); expected=bytes.fromhex(hexbytes)
        if hashlib.sha256(data).hexdigest()!=digest or int.from_bytes(data[0x7c:0x80],'little')!=entry: raise ValueError('reference identity mismatch')
        code=data[entry-0x40000:entry-0x40000+len(expected)]
        if code!=expected: raise ValueError('reference bytes mismatch')
        count=0
        for i in range(65536):
            ptr=(0,0x1235)[i&1]; before=(i*65537)&MASK; after=(before^0x87654321)&MASK; step=(0x90000000+i)&MASK
            value,_,_,_,_=candidate.run(code,expected,entry,cb,ctr,ptr,before,after,step,0x20000ff0,0x81bc,0)
            now,_,_,_,_=gap.clock.run(wrapper,0x20001000,0x8908,0,entry,value,0)
            prior=(now-(300 if i&2 else 299))&MASK
            events=gap.run(gapcode,0x20004000,now,prior)
            cleared=any(e[:3]==('write',0x2000409c,1) for e in events)
            if cleared!=bool(i&2): raise ValueError('gap mismatch')
            if cleared:
                byte=(0x55 if i&4 else 0x54)
                pc,writes=start.first(startcode,0x20004000,byte)
                if (pc==0x897e)!=(byte==0x55): raise ValueError('start mismatch')
                if bool(writes)!=(byte==0x55): raise ValueError('state write mismatch')
            count+=1
        print(f'PASS: {name}: {count} candidate-to-APP synthetic compositions',flush=True); tested+=1
    if not tested: raise ValueError('no reference candidates available; composition not run')
    print('Conditional composition only: installed provider identity, callback behavior and hardware not established.')
if __name__=='__main__': main()
