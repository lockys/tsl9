"""Decode length-value routing and state write at 0x89da–0x89f6.

Local projection assumes successful writes; events are not hardware effects.
The input a4 is a full RV32 value, not assumed to equal a stored halfword.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE/'ingress_state_gate.py')
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
MASK=0xffffffff
EXPECTED=bytes.fromhex('19e3194731a09306004163e6e6001547238ee1086dbf238e010855bf')

def run(code,gp,a4):
    if len(code)!=28 or not 0<=gp<=MASK or not 0<=a4<=MASK: raise ValueError('invalid input')
    r=[(i*0x1020305)&MASK for i in range(32)]; r[0]=0; r[3]=gp; r[14]=a4
    pc=0x89da; events=[]; trace=[]
    for _ in range(8):
        if pc==0x89a8: return events,trace,r[14]
        off=pc-0x89da
        if off<0 or off+2>len(code) or pc&1: raise ValueError('outside local block')
        h=int.from_bytes(code[off:off+2],'little'); trace.append(pc)
        if h&3!=3:
            f3=h>>13
            if h&3==1 and f3==7: # C.BNEZ
                rs1=8+((h>>7)&7)
                imm=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
                pc=pc+gate.signed(imm,9) if r[rs1]!=0 else pc+2
            elif h&3==1 and f3==2: # C.LI
                rd=(h>>7)&31
                if rd==0: raise ValueError('invalid c.li')
                r[rd]=gate.signed(((h>>12&1)<<5)|((h>>2)&31),6)&MASK; pc+=2
            elif h&3==1 and f3==5: # C.J
                imm=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
                pc+=gate.signed(imm,12)
            else: raise ValueError('unsupported compressed instruction')
        else:
            if off+4>len(code): raise ValueError('truncated instruction')
            w=int.from_bytes(code[off:off+4],'little'); op,rd,f3,rs1,rs2=w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31
            if op==0x13 and f3==0:
                r[rd]=(r[rs1]+gate.signed(w>>20,12))&MASK; pc+=4
            elif op==0x63 and f3==6:
                imm=((w>>31&1)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
                pc=pc+gate.signed(imm,13) if r[rs1]<r[rs2] else pc+4
            elif op==0x23 and f3==0:
                imm=((w>>25)<<5)|((w>>7)&31); addr=(r[rs1]+gate.signed(imm,12))&MASK
                events.append((addr,1,r[rs2]&255)); pc+=4
            else: raise ValueError('unsupported instruction')
        r[0]=0
    if pc==0x89a8: return events,trace,r[14]
    raise ValueError('route did not terminate')

def check(code,gp,value):
    events,trace,_=run(code,gp,value)
    expected=6 if value==0 else (5 if value<=1040 else 0)
    if events!=[((gp+156)&MASK,1,expected)]: raise ValueError('route mismatch')
    expected_trace=([0x89da,0x89dc,0x89de,0x89ea,0x89ee] if value==0 else
                    [0x89da,0x89e0,0x89e4,0x89e8,0x89ea,0x89ee] if value<=1040 else
                    [0x89da,0x89e0,0x89e4,0x89f0,0x89f4])
    if trace!=expected_trace: raise ValueError('route trace mismatch')

def main():
    image=gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x89da-0x8000:0x89f6-0x8000]
    if code!=EXPECTED: raise ValueError('original bytes mismatch')
    for value in range(65536): check(code,0x20004000,value)
    for gp in (0,0xffffff64,MASK):
        for value in (0,1,1039,1040,1041,65535,65536,0x80000000,MASK): check(code,gp,value)
    for i in range(len(code)):
        altered=bytearray(code); altered[i]^=1
        try:
            for value in (0,1,1040,1041,65536): check(altered,0x20004000,value)
        except ValueError: continue
        raise ValueError(f'undetected byte mutation {i}')
    print('PASS: 65536 halfword values, 27 full-width/wrap cases, 28 byte mutations')
    print('Full a4=0 routes state 6, 1..1040 routes 5, >1040 routes 0; local successful writes only.')

if __name__=='__main__': main()
