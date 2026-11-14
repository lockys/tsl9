"""Bounded original instruction projection before the ingress dispatch setup.

Inputs and the LBU are synthetic and successful. Entry at 0x8a2a is assumed;
no claims about how registers or checksum memory were produced.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('entry',HERE.parent/'v4160-dispatch-148b4-model'/'entry_provenance.py'); entry=importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)
MASK=0xffffffff
EXPECTED=bytes.fromhex('6311a70303c7510a631df700')

def signed(x,bits): return x-(1<<bits) if x&(1<<(bits-1)) else x

def run(code,gp,a4,s10,a5,loaded):
    if len(code)!=12 or any(not 0<=v<=MASK for v in (gp,a4,s10,a5)) or not 0<=loaded<=255: raise ValueError('invalid inputs')
    r=[0]*32; r[3]=gp; r[14]=a4; r[26]=s10; r[15]=a5; pc=0x8a2a; reads=[]; trace=[]
    for _ in range(3):
        if pc in (0x8a4c,0x8a36): return pc,reads,trace
        off=pc-0x8a2a
        if off<0 or off+4>len(code) or pc&1: raise ValueError('outside gate')
        w=int.from_bytes(code[off:off+4],'little'); trace.append(pc)
        op,rd,f3,rs1,rs2=w&127,w>>7&31,w>>12&7,w>>15&31,w>>20&31
        if op==0x63 and f3==1:
            imm=(w>>31&1)<<12 | (w>>7&1)<<11 | (w>>25&63)<<5 | (w>>8&15)<<1
            pc=(pc+signed(imm,13))&MASK if r[rs1]!=r[rs2] else pc+4
        elif op==3 and f3==4:
            address=(r[rs1]+signed(w>>20,12))&MASK
            if address!=(gp+165)&MASK: raise ValueError('unexpected read')
            reads.append(address); r[rd]=loaded; pc+=4
        else: raise ValueError('unsupported instruction')
        r[0]=0
    if pc in (0x8a4c,0x8a36): return pc,reads,trace
    raise ValueError('gate did not finish')


def check(code,gp,a4,s10,a5,loaded):
    result=run(code,gp,a4,s10,a5,loaded)
    if a4!=s10: want=(0x8a4c,[],[0x8a2a])
    else: want=(0x8a36 if loaded==a5 else 0x8a4c,[(gp+165)&MASK],[0x8a2a,0x8a2e,0x8a32])
    if result!=want: raise ValueError(f'gate mismatch: {result!r} != {want!r}')


def main():
    image=entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x8a2a-0x8000:0x8a36-0x8000]
    if code!=EXPECTED: raise ValueError('original bytes mismatch')
    for loaded in range(256):
        for a5 in range(256): check(code,0x20004000,7,7,a5,loaded)
    for loaded in range(256):
        for first,second in ((0,1),(MASK,0),(0,MASK),(MASK,MASK)):
            for a5 in (0,loaded,loaded|0x100,MASK): check(code,MASK,first,second,a5,loaded)
    for i in range(len(code)):
        mutant=bytearray(code); mutant[i]^=1
        try:
            for args in ((0x20004000,7,7,0,0),(0x20004000,7,8,0,0),(0x20004000,7,7,1,0),(0x20004000,7,7,2,2),(0x20004000,7,7,1,2)): check(mutant,*args)
        except ValueError: continue
        raise ValueError(f'undetected byte mutation {i}')
    print('PASS: 65536 checksum pairs, 4096 boundary cases and 12 byte mutations')
    print('Conditional local entry and successful LBU only; not a complete packet or hardware test.')

if __name__=='__main__': main()
