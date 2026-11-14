"""Pinned state-3 high-length-byte path; checksum read occurs after stores.

This is a bounded fixed-instruction projection, not a general CPU decoder.
Caller supplies the checksum byte observed after the state/halfword stores.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('third',HERE/'ingress_third_byte.py')
third=importlib.util.module_from_spec(spec); spec.loader.exec_module(third)
MASK=0xffffffff
EXPECTED={0x89b4:bytes.fromhex('631a7701'),0x89b8:bytes.fromhex('1147'),0x89ba:bytes.fromhex('238ee108'),0x89be:bytes.fromhex('13978700'),0x89c2:bytes.fromhex('2397e108'),0x89c6:bytes.fromhex('cdb7')}

def run(code,common,gp,s1,byte,loaded,state=3,s7=3):
    if any(not 0<=x<=MASK for x in (gp,s1,s7)) or any(not 0<=x<=255 for x in (byte,loaded,state)): raise ValueError('invalid input')
    pc=0x89b4; events=[]
    for _ in range(6):
        raw=code.get(pc)
        if raw is None or raw!=EXPECTED.get(pc): raise ValueError(f'unexpected instruction {pc:#x}')
        if pc==0x89b4:
            if state!=s7: return 0x89c8,tuple(events)
        elif pc==0x89ba: events.append(('write',(gp+156)&MASK,1,4))
        elif pc==0x89c2: events.append(('write',(gp+142)&MASK,2,byte<<8))
        elif pc==0x89c6:
            # Reuse separately checked checksum path; suppress state-2 prefix.
            for addr in (0x89a8,0x89ac,0x89ae,0x89b2):
                if common.get(addr)!=third.EXPECTED[addr]: raise ValueError('checksum instruction mismatch')
            events.extend((('read',s1,1,loaded),('write',(gp+165)&MASK,1,(byte+loaded)&255)))
            return 0x897e,tuple(events)
        pc+=len(raw)
    raise ValueError('no exit')

def main():
    image=third.prefix.start.gap.clock.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=third.prefix.start.gap.clock.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    read=lambda mapping:{pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in mapping.items()}
    code=read(EXPECTED); common=read(third.EXPECTED)
    for byte in range(256):
        for loaded in range(256):
            pc,events=run(code,common,0x20004000,0x200040a5,byte,loaded)
            expected=(('write',0x2000409c,1,4),('write',0x2000408e,2,byte<<8),('read',0x200040a5,1,loaded),('write',0x200040a5,1,(byte+loaded)&255))
            if (pc,events)!=(0x897e,expected): raise ValueError('event mismatch')
    for state in range(256):
        if state!=3 and run(code,common,0,0,1,2,state,3)!=(0x89c8,()): raise ValueError('selector mismatch')
    for gp in (0,0xffffff60,0xffffff72,MASK):
        pc,events=run(code,common,gp,(gp+143)&MASK,0x83,0x83)
        if pc!=0x897e or events[-1][3]!=6: raise ValueError('synthetic alias mismatch')
    n=0
    for mapping,key in ((code,'code'),(common,'common')):
        addresses=tuple(EXPECTED) if key=='code' else (0x89a8,0x89ac,0x89ae,0x89b2)
        for pc in addresses:
            for i in range(len(mapping[pc])):
                data=bytearray(mapping[pc]); data[i]^=1; mutant=dict(mapping); mutant[pc]=bytes(data)
                try: run(mutant if key=='code' else code,mutant if key=='common' else common,0,165,1,2)
                except ValueError: n+=1; continue
                raise ValueError('mutation not detected')
    print(f'PASS: 65536 byte/checksum pairs, 256 state values, 4 synthetic alias boundaries, {n} byte mutations')
    print('State 3 writes 4, stores command-independent high length byte, then updates checksum.')
    print('Checksum read follows both writes; actual aliases, alignment traps and hardware not established.')
if __name__=='__main__': main()
