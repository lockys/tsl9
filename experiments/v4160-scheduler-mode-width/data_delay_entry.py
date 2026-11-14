"""Entry gates 0xb29a..0xb2aa/0xb2fe with synthetic returning call stubs.

Both calls are assumed to preserve sp and the saved return-address stack slot.
No provider effects, aliasing, traps, interrupt interference or hardware.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py')); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
caller=load('data_delay_caller'); v=caller.v
MASK=0xffffffff
OPS={0xb29a:'7971',0xb29c:'06d6',0xb29e:'ef40e03b',0xb2a2:'39e9',0xb2a4:'ef204014',0xb2a8:'21e9',0xb2f8:'b250',0xb2fa:'4561',0xb2fc:'8280'}


def run(image,first,second,sp,ra):
    if any(not 0<=x<=MASK for x in (first,second,sp,ra)): raise ValueError('bad input')
    pc=0xb29a; original_ra=ra; a0=0; events=[]
    for _ in range(12):
        if pc==0xb2aa: return ('body',a0,sp,ra,tuple(events))
        op=bytes.fromhex(OPS[pc]); off=pc-0x8000
        if image[off:off+len(op)]!=op: raise ValueError(f'opcode mismatch {pc:#x}')
        if pc==0xb29a: sp=(sp-48)&MASK; pc+=2
        elif pc==0xb29c: events.append(('write',(sp+44)&MASK,4,ra)); pc+=2
        elif pc==0xb29e: events.append(('call',0xf65c)); ra=pc+4; a0=first; pc+=4
        elif pc==0xb2a2: pc=0xb2f8 if a0 else 0xb2a4
        elif pc==0xb2a4: events.append(('call',0xd3e8)); ra=pc+4; a0=second; pc+=4
        elif pc==0xb2a8: pc=0xb2f8 if a0 else 0xb2aa
        elif pc==0xb2f8: events.append(('read',(sp+44)&MASK,4,original_ra)); ra=original_ra; pc+=2
        elif pc==0xb2fa: sp=(sp+48)&MASK; pc+=2
        elif pc==0xb2fc: return ('return',a0,sp,ra,tuple(events))
    raise ValueError('instruction limit')


def main():
    image=v.BIN.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=v.SHA: raise ValueError('firmware identity mismatch')
    for first in range(256):
        for second in range(256):
            sp=0x20001000; ra=0x12345678; pushed=(sp-4)&MASK
            events=[('write',pushed,4,ra),('call',0xf65c)]
            if first:
                events.append(('read',pushed,4,ra)); expected=('return',first,sp,ra,tuple(events))
            else:
                events.append(('call',0xd3e8))
                if second:
                    events.append(('read',pushed,4,ra)); expected=('return',second,sp,ra,tuple(events))
                else: expected=('body',0,(sp-48)&MASK,0xb2a8,tuple(events))
            if run(image,first,second,sp,ra)!=expected: raise ValueError('gate mismatch')
    for byte in range(256):
        kind,a0,sp,ra,_=run(image,0,0,0x20001000,0x12345678)
        args,end,restored,_=caller.run(image,byte,0,0x20000000,0x20001234,sp,0x12345678)
        if kind!='body' or a0!=0 or ra!=0xb2a8 or args!=(0xb254,0,(0,60000,300000,600000)[byte>>6],0) or end!=0x20001000 or restored!=0x12345678: raise ValueError('body composition mismatch')
    for addr in OPS:
        bad=bytearray(image); bad[addr-0x8000]^=1
        for a,b in ((1,0),(0,1),(0,0)):
            try: run(bad,a,b,0x20001000,0x12345678)
            except ValueError as e:
                if str(e).startswith('opcode mismatch'): break
        else: raise ValueError(f'mutant accepted {addr:#x}')
    print('PASS: 65536 call-result pairs, short circuit and restored exit verified')
    print('PASS: all 256 bytes composed across both-zero gate; 9 opcode mutations rejected')
    print('Providers are returning stubs; side effects, reachability and hardware unknown.')

if __name__=='__main__': main()
