"""Fixed original-instruction projection of the state-one ingress byte gate.
Assumes state==1, s5==1, successful access, and no asynchronous writes.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('start',HERE/'clock_gap_start_composition.py')
start=importlib.util.module_from_spec(spec); spec.loader.exec_module(start)
EXPECTED={0x8982:bytes.fromhex('631c5701'),0x8986:bytes.fromhex('1307f007'),0x898a:bytes.fromhex('6391e70c'),0x898e:bytes.fromhex('8947'),0x8990:bytes.fromhex('238ef108'),0x8994:bytes.fromhex('a382010a'),0x8998:bytes.fromhex('ddb7')}
MASK=0xffffffff

def run(code,gp,byte,state=1,s5=1):
    if not 0<=gp<=MASK or not 0<=byte<=255 or not 0<=state<=255 or not 0<=s5<=MASK: raise ValueError('bad input')
    pc=0x8982; events=[]
    for _ in range(7):
        raw=code.get(pc)
        if raw is None or raw!=EXPECTED.get(pc): raise ValueError(f'unexpected instruction {pc:#x}')
        if pc==0x8982:
            if state!=s5: return 0x899a,tuple(events)
        elif pc==0x898a:
            if byte!=127: return 0x8a4c,tuple(events)
        elif pc==0x8990: events.append(('write',(gp+156)&MASK,1,2))
        elif pc==0x8994: events.append(('write',(gp+165)&MASK,1,0))
        elif pc==0x8998: return 0x897e,tuple(events)
        pc+=len(raw)
    raise ValueError('no exit')

def main():
    image=start.gap.clock.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=start.gap.clock.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code={pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in EXPECTED.items()}
    first={pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in start.EXPECTED.items()}
    for a in range(256):
        for b in range(256):
            pc,writes=start.first(first,0x20004000,a)
            if a!=85:
                if (pc,writes)!=(0x8a4c,()): raise ValueError('first byte mismatch')
                continue
            if writes!=(('write',0x2000409c,1,1),): raise ValueError('first state mismatch')
            pc,writes=run(code,0x20004000,b,writes[0][3])
            expected=(0x897e,(('write',0x2000409c,1,2),('write',0x200040a5,1,0))) if b==127 else (0x8a4c,())
            if (pc,writes)!=expected: raise ValueError('second byte mismatch')
    for state in range(256):
        pc,writes=run(code,MASK,127,state,1)
        expected=0x897e if state==1 else 0x899a
        if pc!=expected: raise ValueError('selector mismatch')
        if state==1 and writes!=(('write',155,1,2),('write',164,1,0)): raise ValueError('wrap mismatch')
    n=0
    for pc,raw in code.items():
        for i in range(len(raw)):
            data=bytearray(raw); data[i]^=1; mutant=dict(code); mutant[pc]=bytes(data)
            try: run(mutant,0x20004000,127)
            except ValueError: n+=1; continue
            raise ValueError('mutation not detected')
    print(f'PASS: 65536 byte pairs, 256 state values and {n} byte mutations')
    print('Conditional state-zero/one composition accepts only 55 7f and then writes state=2, checksum=0.')
    print('Requires successful consecutive processing, stable state/gp and no intervening side effects; no hardware claim.')
if __name__=='__main__': main()
