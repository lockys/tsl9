"""Conditionally model the APP clock wrapper 0x81b0..0x81ca.

Resident [0x4007c] is unknown and replaced by a normal-return stub; its
return value and its effect on s2 are explicit inputs. Stack accesses succeed;
the stub does not modify the saved return address or stack pointer.
This is a fixed-instruction projection, not a general instruction decoder.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE/'ingress_state_gate.py')
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
MASK=0xffffffff
EXPECTED={0x81b0:bytes.fromhex('b7070400'),0x81b4:bytes.fromhex('fc5f'),0x81b6:bytes.fromhex('4111'),0x81b8:bytes.fromhex('06c6'),0x81ba:bytes.fromhex('8297'),0x81bc:bytes.fromhex('a947'),0x81be:bytes.fromhex('3305f502'),0x81c2:bytes.fromhex('b240'),0x81c4:bytes.fromhex('4101'),0x81c6:bytes.fromhex('1181'),0x81c8:bytes.fromhex('8280')}

def run(code,sp,ra,s2,resident_ptr,resident_result,resident_s2):
    if any(not 0<=x<=MASK for x in (sp,ra,s2,resident_ptr,resident_result,resident_s2)): raise ValueError('outside RV32')
    pc=0x81b0; a0=0; a5=0; events=[]; saved=None
    for _ in range(11):
        raw=code.get(pc)
        if raw!=EXPECTED.get(pc) or raw is None: raise ValueError(f'unexpected instruction at {pc:#x}')
        if pc==0x81b0: a5=0x40000
        elif pc==0x81b4:
            events.append(('read',a5+124,4)); a5=resident_ptr
        elif pc==0x81b6: sp=(sp-16)&MASK
        elif pc==0x81b8:
            saved=ra; events.append(('write',(sp+12)&MASK,4,ra))
        elif pc==0x81ba:
            events.append(('call',a5&~1,0x81bc)); a0=resident_result; s2=resident_s2; ra=0x81bc
        elif pc==0x81bc: a5=10
        elif pc==0x81be: a0=(a0*a5)&MASK
        elif pc==0x81c2:
            events.append(('read',(sp+12)&MASK,4)); ra=saved
        elif pc==0x81c4: sp=(sp+16)&MASK
        elif pc==0x81c6: a0>>=4
        elif pc==0x81c8: return a0,s2,sp,ra,tuple(events)
        pc+=len(raw)
    raise ValueError('no return')

def main():
    image=gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code={pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in EXPECTED.items()}
    for value in range(65536):
        out,s2,sp,ra,events=run(code,0x20001000,0x8908,0x12345678,0x1235,value,0x87654321)
        if (out,s2,sp,ra)!=(value*10>>4,0x87654321,0x20001000,0x8908): raise ValueError('result mismatch')
        if events!=(('read',0x4007c,4),('write',0x20000ffc,4,0x8908),('call',0x1234,0x81bc),('read',0x20000ffc,4)): raise ValueError('event mismatch')
    for value in (0,1,0x19999999,0x1999999a,0x7fffffff,MASK):
        for sp in (0,4,16,0x20001000,MASK):
            for saved in (0,65536,MASK):
                out,s2,newsp,ra,_=run(code,sp,0x8908,saved,0,value,saved)
                if (out,s2,newsp,ra)!=(((value*10)&MASK)>>4,saved,sp,0x8908): raise ValueError('boundary mismatch')
    mutations=0
    for pc,raw in code.items():
        for i in range(len(raw)):
            mutant=dict(code); data=bytearray(raw); data[i]^=1; mutant[pc]=bytes(data)
            try: run(mutant,16,0x8908,0,0,0,0)
            except ValueError: mutations+=1; continue
            raise ValueError('mutation not detected')
    print(f'PASS: 65536 result values, 90 boundaries, {mutations} byte mutations')
    print('Conditional normal return: a0=((resident_result*10) mod 2^32)>>4; s2 equals resident post-call s2.')
    print('Resident target, its side effects, return, actual stack and hardware are not verified.')

if __name__=='__main__': main()
