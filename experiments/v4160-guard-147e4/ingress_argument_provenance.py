"""Decode ingress argument saves and first external call at 0x8900.

Stops at the call target; does not assume the callee returns or preserves s2.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE/'ingress_state_gate.py')
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
MASK=0xffffffff
EXPECTED=bytes.fromhex('aa89328a36896d30')

def execute(code,a0,a2,a3,ra):
    if len(code)!=8 or any(not 0<=x<=MASK for x in (a0,a2,a3,ra)): raise ValueError('invalid input')
    r=[(i*0x1234567)&MASK for i in range(32)]; r[0]=0; r[1]=ra; r[10]=a0; r[12]=a2; r[13]=a3
    pc=0x8900
    for _ in range(4):
        off=pc-0x8900
        if off<0 or off+2>len(code): raise ValueError('outside block')
        h=int.from_bytes(code[off:off+2],'little')
        if h&3==2 and h>>12==8: # C.MV, bit12=0, rd/rs2 nonzero
            rd=(h>>7)&31; rs2=(h>>2)&31
            if not rd or not rs2: raise ValueError('invalid c.mv')
            r[rd]=r[rs2]; pc+=2
        elif h&3==1 and h>>13==1: # RV32 C.JAL
            imm=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
            r[1]=(pc+2)&MASK; pc=(pc+gate.signed(imm,12))&MASK
            return pc,r[1],r[19],r[20],r[18]
        else: raise ValueError('unsupported instruction')
    raise ValueError('call not reached')

def check(code,a0,a2,a3,ra):
    got=execute(code,a0,a2,a3,ra)
    expected=(0x81b0,0x8908,a0,a2,a3)
    if got!=expected: raise ValueError(f'argument mismatch: {got!r}')

def main():
    image=gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x8900-0x8000:0x8908-0x8000]
    if code!=EXPECTED: raise ValueError('original bytes mismatch')
    for a3 in range(65536): check(code,0x12345678,0x20001000,a3,0xffffffff)
    for a0 in (0,1,MASK):
        for a2 in (0,0x20001000,MASK):
            for a3 in (0,65535,65536,0x80000000,MASK):
                for ra in (0,MASK): check(code,a0,a2,a3,ra)
    for i in range(8):
        mutant=bytearray(code); mutant[i]^=1
        try: check(mutant,0x12345678,0x20001000,0x80010000,0xffffffff)
        except ValueError: continue
        raise ValueError(f'undetected byte mutation {i}')
    print('PASS: 65536 a3 values, 90 full-width boundaries and 8 byte mutations')
    print('Before call 0x81b0: s3=a0, s4=a2, s2=a3, ra=0x8908; no truncation in these instructions.')
    print('Callee behavior, upstream caller input width, reachability and hardware remain unknown.')

if __name__=='__main__': main()
