"""Conditional composition of clock wrapper arithmetic and ingress gap check.

Resident results are synthetic. Saved stack is stable, loads/stores succeed,
and the timestamp is supplied at the read boundary. Not hardware execution.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('clock',HERE/'clock_wrapper_81b0.py')
clock=importlib.util.module_from_spec(spec); spec.loader.exec_module(clock)
MASK=0xffffffff
EXPECTED={0x8908:bytes.fromhex('9387010a'),0x890c:bytes.fromhex('9c43'),0x890e:bytes.fromhex('1307b012'),0x8912:bytes.fromhex('b307f540'),0x8916:bytes.fromhex('6374f700'),0x891a:bytes.fromhex('238e0108'),0x891e:bytes.fromhex('23a0a10a')}

def run(code,gp,now,prior):
    if any(not 0<=v<=MASK for v in (gp,now,prior)): raise ValueError('invalid RV32 value')
    pc=0x8908; events=[]; a5=0; a4=0
    for _ in range(7):
        raw=code.get(pc)
        if raw is None or raw!=EXPECTED.get(pc): raise ValueError(f'unexpected instruction at {pc:#x}')
        if pc==0x8908: a5=(gp+160)&MASK
        elif pc==0x890c: events.append(('read',a5,4,prior)); a5=prior
        elif pc==0x890e: a4=299
        elif pc==0x8912: a5=(now-a5)&MASK
        elif pc==0x8916:
            if a4>=a5: pc=0x891e; continue
        elif pc==0x891a: events.append(('write',(gp+156)&MASK,1,0))
        elif pc==0x891e:
            events.append(('write',(gp+160)&MASK,4,now)); return tuple(events)
        pc+=len(raw)
    raise ValueError('no exit')

def main():
    image=clock.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=clock.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code={pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in EXPECTED.items()}
    for prior in range(65536):
        for delta in (0,299,300,MASK):
            now=(prior+delta)&MASK; events=run(code,0x20004000,now,prior)
            expected=(('read',0x200040a0,4,prior),)+((('write',0x2000409c,1,0),) if delta>299 else ())+ (('write',0x200040a0,4,now),)
            if events!=expected: raise ValueError('gap mismatch')
    wrapper={pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in clock.EXPECTED.items()}
    for k in range(1,10):
        boundary=(k*(1<<32)+9)//10
        before=clock.run(wrapper,0x20001000,0x8908,0,0,boundary-1,0)[0]
        after=clock.run(wrapper,0x20001000,0x8908,0,0,boundary,0)[0]
        if (before,after)!= (0x0fffffff,0): raise ValueError('unexpected wrapper discontinuity')
        events=run(code,0x20004000,after,before)
        if (after-before)&MASK !=0xf0000001 or len(events)!=3 or events[1]!=('write',0x2000409c,1,0): raise ValueError('wrap witness mismatch')
    for pc,raw in code.items():
        for i in range(len(raw)):
            data=bytearray(raw); data[i]^=1; mutant=dict(code); mutant[pc]=bytes(data)
            try: run(mutant,0x20004000,300,0)
            except ValueError: continue
            raise ValueError('mutation not detected')
    print('PASS: 262144 gap cases, 9 synthetic clock discontinuity witnesses, 26 byte mutations')
    print('At each witness, consecutive resident values yield 0x0fffffff -> 0; modular difference 0xf0000001 clears gp+156.')
    print('Conditional synthetic composition only; no claim about resident monotonicity, real timing or hardware.')

if __name__=='__main__': main()
