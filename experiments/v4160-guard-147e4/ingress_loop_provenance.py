"""Trace ingress loop entry to the local length-initialization boundary.

The test starts at 0x8938 after the separately verified 0x8934 s11 setup.
Reads are successful synthetic bytes; no IRQ, trap or concurrency is modeled.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
prov=load('prov',HERE/'ingress_a5_provenance.py')
s11=load('s11',HERE/'ingress_s11_provenance.py')
MASK=0xffffffff
EXPECTED={0x8938:bytes.fromhex('93170401'),0x893c:bytes.fromhex('c183'),
          0x893e:bytes.fromhex('63e22703'),0x8962:bytes.fromhex('b3078a00'),
          0x8966:bytes.fromhex('03c7c109')}

def run(code,selectors,gp,s0,s2,s4,state,byte,states):
    if any(not 0<=x<=MASK for x in (gp,s0,s2,s4)) or not 0<=state<=255 or not 0<=byte<=255: raise ValueError('invalid input')
    r=[(i*0x1020305)&MASK for i in range(32)]; r[0]=0; r[3]=gp; r[8]=s0; r[18]=s2; r[20]=s4; r[27]=s11.pointer(s11.EXPECTED,gp)
    pc=0x8938; reads=[]; trace=[]
    for _ in range(5):
        if pc==0x8942: return pc,r[27],reads,trace
        if pc==0x896a:
            target,_,tailreads,tailtrace=prov.run(selectors,r[14],states,byte,r[15])
            return target,r[27],reads+tailreads,trace+tailtrace
        if pc not in code: raise ValueError(f'outside prefix {pc:#x}')
        raw=code[pc]; trace.append(pc)
        if len(raw)==2:
            h=int.from_bytes(raw,'little')
            if h&0xec03!=0x8001: raise ValueError('expected c.srli')
            rd=8+((h>>7)&7); shift=((h>>12&1)<<5)|((h>>2)&31)
            if shift>=32: raise ValueError('invalid shift')
            r[rd]>>=shift; pc+=2
        elif len(raw)==4:
            w=int.from_bytes(raw,'little'); op,rd,f3,rs1,rs2=w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31
            if op==0x13 and f3==1 and w>>25==0:
                r[rd]=(r[rs1]<<rs2)&MASK; pc+=4
            elif op==0x33 and f3==0 and w>>25==0:
                r[rd]=(r[rs1]+r[rs2])&MASK; pc+=4
            elif op==3 and f3==4:
                addr=(r[rs1]+prov.gate.signed(w>>20,12))&MASK
                if addr!=(gp+156)&MASK: raise ValueError('unexpected state read')
                reads.append(addr); r[rd]=state; pc+=4
            elif op==0x63 and f3==6:
                imm=((w>>31&1)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
                pc=pc+prov.gate.signed(imm,13) if r[rs1]<r[rs2] else pc+4
            else: raise ValueError('unsupported instruction')
        else: raise ValueError('bad instruction width')
        r[0]=0
    if pc==0x896a:
        target,_,tailreads,tailtrace=prov.run(selectors,r[14],states,byte,r[15])
        return target,r[27],reads+tailreads,trace+tailtrace
    if pc==0x8942: return pc,r[27],reads,trace
    raise ValueError('prefix did not terminate')

def check(code,selectors,gp,s0,s2,s4,state,byte):
    result=run(code,selectors,gp,s0,s2,s4,state,byte,(1,2,3,4))
    if (s0&65535)>=s2: expected=(0x8942,(gp+142)&MASK,[],[0x8938,0x893c,0x893e])
    else:
        target,_,tailreads,tailtrace=prov.run(selectors,state,(1,2,3,4),byte,(s4+s0)&MASK)
        expected=(target,(gp+142)&MASK,[(gp+156)&MASK]+tailreads,[0x8938,0x893c,0x893e,0x8962,0x8966]+tailtrace)
    if result!=expected: raise ValueError(f'loop mismatch {result!r}')

def main():
    image=prov.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=prov.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    code={pc:image[pc-0x8000:pc-0x8000+len(x)] for pc,x in EXPECTED.items()}
    selectors={pc:image[pc-0x8000:pc-0x8000+len(x)] for pc,x in prov.EXPECTED.items()}
    setup=image[0x8934-0x8000:0x8938-0x8000]
    if code!=EXPECTED or selectors!=prov.EXPECTED or setup!=s11.EXPECTED: raise ValueError('original bytes mismatch')
    for s0 in range(65536):
        check(code,selectors,0x20004000,s0,32768,0x20001000,4,0xab)
    for gp in (0,0xffffff76,MASK):
        for s0 in (0,1,65535,65536,0xffffffff):
            for s2 in (0,1,65535,65536,MASK):
                for state in (0,1,2,3,4,5): check(code,selectors,gp,s0,s2,MASK,state,0xff)
    for pc,raw in code.items():
        for i in range(len(raw)):
            mutated=dict(code); item=bytearray(raw); item[i]^=1; mutated[pc]=bytes(item)
            try:
                for s0,s2 in ((0,1),(1,1),(65535,65536),(0xffff0001,2)):
                    check(mutated,selectors,0x20004000,s0,s2,0x20001000,4,0xab)
            except ValueError: continue
            raise ValueError(f'undetected mutation {pc:#x}+{i}')
    print('PASS: 65536 loop indices, 450 boundary cases and 18 byte mutations')
    print('On the tested local path, gp and s11 remain unchanged before 0x89cc; entry assumes prior s11 setup.')
    print('No asynchronous changes, faults, calls, or real hardware were modeled.')

if __name__=='__main__': main()
