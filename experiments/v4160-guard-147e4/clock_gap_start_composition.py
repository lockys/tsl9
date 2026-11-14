"""Compose timeout state reset with the parser's state-zero byte gate.

Projections are stitched at memory boundaries; successful accesses, stable gp,
no asynchronous writes and no alias affecting the state byte are assumed.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
gap=load('gap',HERE/'clock_gap_composition.py')
loop=load('loop',HERE/'ingress_loop_provenance.py')
EXPECTED={0x8970:bytes.fromhex('13075005'),0x8974:bytes.fromhex('639ce70c'),0x8978:bytes.fromhex('8547'),0x897a:bytes.fromhex('238ef108')}

def first(code,gp,byte):
    if not 0<=gp<=0xffffffff or not 0<=byte<=255: raise ValueError('invalid input')
    pc=0x8970; a4=0; a5=byte
    for _ in range(4):
        raw=code.get(pc)
        if raw is None or raw!=EXPECTED.get(pc): raise ValueError(f'unexpected instruction at {pc:#x}')
        if pc==0x8970: a4=85
        elif pc==0x8974:
            if a5!=a4: return 0x8a4c,()
        elif pc==0x8978: a5=1
        elif pc==0x897a: return 0x897e,(('write',(gp+156)&0xffffffff,1,a5),)
        pc+=len(raw)
    raise ValueError('no exit')

def main():
    image=gap.clock.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gap.clock.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    read=lambda mapping:{pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in mapping.items()}
    c=read(EXPECTED); g=read(gap.EXPECTED); prefix=read(loop.EXPECTED); selectors=read(loop.prov.EXPECTED)
    if prefix!=loop.EXPECTED or selectors!=loop.prov.EXPECTED: raise ValueError('loop bytes mismatch')
    count=0
    for old in range(256):
        for byte in range(256):
            gp=0x20004000; state=old; events=gap.run(g,gp,300,0)
            for event in events:
                if event[:3]==('write',gp+156,1): state=event[3]
            if state!=0: raise ValueError('missing reset')
            pc,_,reads,regs=loop.run(prefix,selectors,gp,0,1,0x20001000,state,byte,(1,2,3,4))
            if pc!=0x8970 or reads[-1]!=0x20001000: raise ValueError('unexpected loop route')
            pc,writes=first(c,gp,byte)
            expected=(0x897e,(('write',gp+156,1,1),)) if byte==85 else (0x8a4c,())
            if (pc,writes)!=expected: raise ValueError('state zero mismatch')
            count+=1
    for pc,raw in c.items():
        for i in range(len(raw)):
            altered=bytearray(raw); altered[i]^=1; mutant=dict(c); mutant[pc]=bytes(altered)
            try: first(mutant,0x20004000,85)
            except ValueError: continue
            raise ValueError('mutation undetected')
    print(f'PASS: {count} old-state/input-byte combinations; 14 byte mutations')
    print('After a modeled reset and successful first-byte read, 0x55 writes state 1; all other bytes take 0x8a4c.')
    print('Conditional stitched projections, not real packet reachability or hardware execution.')
if __name__=='__main__': main()
