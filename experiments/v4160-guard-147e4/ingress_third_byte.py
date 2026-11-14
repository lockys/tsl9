"""Pinned APP instruction projection for ingress state 2 (0x899a..0x89b4).

Loaded checksum is supplied after the two writes: it may reflect aliasing.
Assume successful accesses and no asynchronous changes during this fragment.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prefix',HERE/'ingress_second_byte.py')
prefix=importlib.util.module_from_spec(spec); spec.loader.exec_module(prefix)
MASK=0xffffffff
EXPECTED={0x899a:bytes.fromhex('631d6701'),0x899e:bytes.fromhex('0d47'),0x89a0:bytes.fromhex('238ee108'),0x89a4:bytes.fromhex('2382f10a'),0x89a8:bytes.fromhex('03c70400'),0x89ac:bytes.fromhex('ba97'),0x89ae:bytes.fromhex('a382f10a'),0x89b2:bytes.fromhex('f1b7')}

def run(code,gp,s1,byte,loaded,state=2,s6=2):
    if any(not 0<=v<=MASK for v in (gp,s1,s6)) or any(not 0<=v<=255 for v in (byte,loaded,state)): raise ValueError('invalid input')
    pc=0x899a; events=[]; a5=byte; a4=state
    for _ in range(8):
        raw=code.get(pc)
        if raw is None or raw!=EXPECTED.get(pc): raise ValueError(f'unexpected instruction at {pc:#x}')
        if pc==0x899a:
            if a4!=s6: return 0x89b4,tuple(events)
        elif pc==0x899e: a4=3
        elif pc==0x89a0: events.append(('write',(gp+156)&MASK,1,a4))
        elif pc==0x89a4: events.append(('write',(gp+164)&MASK,1,a5))
        elif pc==0x89a8: events.append(('read',s1,1,loaded)); a4=loaded
        elif pc==0x89ac: a5=(a5+a4)&MASK
        elif pc==0x89ae: events.append(('write',(gp+165)&MASK,1,a5&255))
        elif pc==0x89b2: return 0x897e,tuple(events)
        pc+=len(raw)
    raise ValueError('no exit')

def main():
    image=prefix.start.gap.clock.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=prefix.start.gap.clock.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code={pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in EXPECTED.items()}
    for byte in range(256):
        for loaded in range(256):
            pc,events=run(code,0x20004000,0x200040a5,byte,loaded)
            expected=(('write',0x2000409c,1,3),('write',0x200040a4,1,byte),('read',0x200040a5,1,loaded),('write',0x200040a5,1,(byte+loaded)&255))
            if pc!=0x897e or events!=expected: raise ValueError('event mismatch')
    for state in range(256):
        pc,events=run(code,MASK,0,7,9,state,2)
        if state!=2 and (pc,events)!=(0x89b4,()): raise ValueError('selector mismatch')
    # The earlier 0x8930 setup establishes s1=gp+165, if both are stable.
    if image[0x8930-0x8000:0x8934-0x8000]!=bytes.fromhex('9384510a'): raise ValueError('s1 setup mismatch')
    for gp in range(65536):
        s1=(gp+165)&MASK
        if s1 in ((gp+156)&MASK,(gp+164)&MASK): raise ValueError('unexpected byte alias')
    # Artificial counterexample when s1 does not have that established value:
    # command write changes what the subsequent checksum read observes.
    pc,events=run(code,0x20004000,0x200040a4,0x83,0x83)
    if pc!=0x897e or events[-1][3]!=6: raise ValueError('alias witness mismatch')
    n=0
    for pc,raw in code.items():
        for i in range(len(raw)):
            data=bytearray(raw); data[i]^=1; mutant=dict(code); mutant[pc]=bytes(data)
            try: run(mutant,0x20004000,0x200040a5,1,2)
            except ValueError: n+=1; continue
            raise ValueError('mutation not detected')
    print(f'PASS: 65536 byte/checksum pairs, 256 state values, alias witness, {n} byte mutations')
    print('State 2 writes state=3, command byte, reads checksum, writes low8(command+loaded).')
    print('Conditional s1=gp+165 avoids these two byte writes; artificial s1 alias is not shown reachable.')
    print('Read is after both writes; no claim of packet execution or hardware.')
if __name__=='__main__': main()
