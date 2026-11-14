"""Trace LBU of a5 through the local ingress state-selector chain.

Entry at 0x896a and successful memory access are assumed. Other branches stop
at their first instruction; no complete parser or hardware execution is claimed.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('gate',HERE/'ingress_state_gate.py')
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
MASK=0xffffffff
EXPECTED={0x896a:bytes.fromhex('83c70700'),0x896e:bytes.fromhex('11eb'),
          0x8982:bytes.fromhex('631c5701'),0x899a:bytes.fromhex('631d6701'),
          0x89b4:bytes.fromhex('631a7701'),0x89c8:bytes.fromhex('63178703')}
EXITS={0x8970,0x8986,0x899e,0x89b8,0x89cc,0x89f6}

def run(blocks,a4,states,byte,pointer):
    if not 0<=a4<=MASK or len(states)!=4 or any(not 0<=x<=MASK for x in states) or not 0<=byte<=255 or not 0<=pointer<=MASK: raise ValueError('invalid input')
    r=[(i*0x1020305)&MASK for i in range(32)]; r[0]=0; r[14]=a4; r[15]=pointer
    for i,value in enumerate(states): r[21+i]=value
    pc=0x896a; reads=[]; trace=[]
    for _ in range(6):
        if pc in EXITS: return pc,r[15],reads,trace
        if pc not in blocks: raise ValueError(f'outside chain {pc:#x}')
        code=blocks[pc]; trace.append(pc)
        if len(code)==2:
            h=int.from_bytes(code,'little')
            if h&3!=1 or h>>13!=7: raise ValueError('expected c.bnez')
            rs1=8+((h>>7)&7)
            imm=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
            pc=pc+gate.signed(imm,9) if r[rs1] else pc+2
        elif len(code)==4:
            w=int.from_bytes(code,'little'); op,rd,f3,rs1,rs2=w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31
            if op==3 and f3==4:
                address=(r[rs1]+gate.signed(w>>20,12))&MASK
                reads.append(address); r[rd]=byte; pc+=4
            elif op==0x63 and f3==1:
                imm=((w>>31&1)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
                pc=pc+gate.signed(imm,13) if r[rs1]!=r[rs2] else pc+4
            else: raise ValueError('unsupported instruction')
        else: raise ValueError('unexpected instruction width')
        r[0]=0
    if pc in EXITS: return pc,r[15],reads,trace
    raise ValueError('chain did not finish')

def check(blocks,a4,states,byte,pointer):
    if a4==0: pc,trace=0x8970,[0x896a,0x896e]
    elif a4==states[0]: pc,trace=0x8986,[0x896a,0x896e,0x8982]
    elif a4==states[1]: pc,trace=0x899e,[0x896a,0x896e,0x8982,0x899a]
    elif a4==states[2]: pc,trace=0x89b8,[0x896a,0x896e,0x8982,0x899a,0x89b4]
    elif a4==states[3]: pc,trace=0x89cc,[0x896a,0x896e,0x8982,0x899a,0x89b4,0x89c8]
    else: pc,trace=0x89f6,[0x896a,0x896e,0x8982,0x899a,0x89b4,0x89c8]
    result=run(blocks,a4,states,byte,pointer)
    if result!=(pc,byte,[pointer],trace): raise ValueError(f'chain mismatch {result!r}')

def main():
    image=gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=gate.entry.SHA: raise ValueError('firmware identity mismatch')
    blocks={pc:image[pc-0x8000:pc-0x8000+len(expected)] for pc,expected in EXPECTED.items()}
    if blocks!=EXPECTED: raise ValueError('original bytes mismatch')
    for state in range(256):
        for byte in range(256): check(blocks,state,(1,2,3,4),byte,0x20001000)
    for value in (0,1,2,3,4,5,255,256,MASK):
        for states in ((1,2,3,4),(value,value,value,value),(MASK,0,256,5)):
            for pointer in (0,MASK): check(blocks,value,states,0xff,pointer)
    for pc,code in blocks.items():
        for i in range(len(code)):
            mutant=dict(blocks); altered=bytearray(code); altered[i]^=1; mutant[pc]=bytes(altered)
            try:
                for state in (0,1,2,3,4,5): check(mutant,state,(1,2,3,4),0xab,0x20001000)
            except ValueError: continue
            raise ValueError(f'undetected mutation {pc:#x}+{i}')
    print('PASS: 65536 state/byte cases, 54 duplicate/full-width cases, 22 byte mutations')
    print('For this local selector chain, a5 at 0x89cc is the zero-extended loaded byte.')
    print('Does not establish entry reachability, trap behavior, concurrency or actual hardware.')

if __name__=='__main__': main()
