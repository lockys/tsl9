#!/usr/bin/env python3
"""Limited RV32I/C interpreter for the original TX copy test and one iteration."""
import argparse,hashlib,importlib.util,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('tx',HERE/'tx-copy-step.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);MASK=0xffffffff

def execute(code,r,mem):
    r=r[:];events=[];pc=0x8b0a
    for _ in range(20):
        if pc==0x8b14 or (pc==0x8b0a and events):return pc,r,events
        h=int.from_bytes(bytes(code[pc+i] for i in range(2)),'little')
        if h&3!=3:
            if h==0x8141:r[10]>>=16
            elif h==0x0585:r[11]=(r[11]+1)&MASK
            elif h==0x972a:r[14]=(r[14]+r[10])&MASK
            elif h==0xb745:pc=0x8b0a;continue
            else:raise ValueError('unsupported compressed instruction')
            pc+=2;continue
        w=int.from_bytes(bytes(code[pc+i] for i in range(4)),'little');op=w&127;rd=(w>>7)&31;f=(w>>12)&7;rs1=(w>>15)&31;rs2=(w>>20)&31
        if op==0x13 and f==1 and w>>25==0:r[rd]=(r[rs1]<<rs2)&MASK
        elif op==0x13 and f==7:r[rd]=r[rs1]&((w>>20)&0xfff)
        elif op==0x33 and f==0 and w>>25==0:r[rd]=(r[rs1]+r[rs2])&MASK
        elif op==3 and f==4:
            imm=w>>20;imm=imm-4096 if imm&2048 else imm;addr=(r[rs1]+imm)&MASK;r[rd]=mem[addr];events.append(('read',addr,r[rd]))
        elif op==0x23 and f==0:
            imm=((w>>25)<<5)|((w>>7)&31);imm=imm-4096 if imm&2048 else imm;addr=(r[rs1]+imm)&MASK;value=r[rs2]&255;mem[addr]=value;events.append(('write',addr,value))
        elif op==0x63 and f==6:
            imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1);imm=imm-8192 if imm&4096 else imm
            pc=(pc+imm)&MASK if r[rs1]<r[rs2] else pc+4;continue
        else:raise ValueError(f'unsupported opcode {w:08x}')
        r[0]=0;pc+=4
    raise ValueError('step limit')

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args();raw=(a.root/m.BIN).read_bytes();m.need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==m.SHA,'firmware identity')
    code={}
    for addr,h in m.WINDOWS:
        b=bytes.fromhex(h);m.need(raw[addr-0x8000:addr-0x8000+len(b)]==b,'instruction bytes');code.update({addr+i:v for i,v in enumerate(b)})
    rng=random.Random(0x8b52)
    for low in range(65536):
        for n in (low,low+1):
            i=(rng.getrandbits(16)<<16)|low;src=rng.getrandbits(32);dst=rng.getrandbits(32);sum_=rng.getrandbits(32);value=low&255
            r=[0]*32;r[8]=n;r[9]=src;r[11]=i;r[14]=sum_;r[15]=dst
            mem={(src+i)&MASK:value};other=mem.copy();pc,regs,events=execute(code,r,mem);expected=m.step(i,n,src,dst,sum_,other)
            m.need((pc,regs[11],regs[14],events)==expected and mem==other,'differential')
    r=[0]*32;r[8]=1;r[9]=0x1000;r[11]=0;r[14]=255;r[15]=0x2000
    reference=execute(code,r,{0x1000:7})
    for addr,bit in ((0x8b0e,0x04),(0x8b5e,0x04),(0x8b60,0x04),(0x8b6a,0x04)):
        altered=code.copy();altered[addr]^=bit
        try: actual=execute(altered,r,{0x1000:7})
        except (ValueError,KeyError): continue
        m.need(actual!=reference,'mutation survived')
    print('PASS: 131072 original-byte decoder versus event-model cases; 4 compressed mutations rejected')
    print('LIMIT: limited interpreter, compressed cases fixed, successful accesses, no exceptions/interrupts or hardware; implementations may share errors')
if __name__=='__main__':main()
