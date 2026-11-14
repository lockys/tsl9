"""Original instruction projection from successful ingress dispatch setup.

Inputs are synthetic successful GP-relative reads; start 0x8a36 is assumed
reached. Stop at the first instruction of the dispatcher, without executing it.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
path=HERE.parent/'v4160-dispatch-148b4-model'/'entry_provenance.py'
spec=importlib.util.spec_from_file_location('entry',path); entry=importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)
MASK=0xffffffff
EXPECTED=bytes.fromhex('83d6e108173600201306e6f983c5410a4e85efb0e060')


def signed(x,bits): return x-(1<<bits) if x&(1<<(bits-1)) else x


def run(code,gp,handle,length,command):
    if len(code)!=22 or not all(0<=x<=MASK for x in (gp,handle)) or not 0<=length<=65535 or not 0<=command<=255: raise ValueError('invalid setup input')
    regs=[0x5a5a5a5a]*32; regs[0]=0; regs[3]=gp; regs[19]=handle
    memory={(gp+142)&MASK:(2,length),(gp+164)&MASK:(1,command)}
    reads=[]; pc=0x8a36; trace=[]
    for _ in range(6):
        off=pc-0x8a36
        if off<0 or off+2>len(code) or pc&1: raise ValueError('invalid setup PC')
        trace.append(pc); h=int.from_bytes(code[off:off+2],'little')
        if h&3!=3:
            q,f3,bit,rd,rs2=h&3,h>>13,(h>>12)&1,(h>>7)&31,(h>>2)&31
            if (q,f3,bit)!=(2,4,0) or not rd or not rs2: raise ValueError('unsupported compressed instruction')
            regs[rd]=regs[rs2]; pc+=2
        else:
            if off+4>len(code): raise ValueError('truncated instruction')
            w=int.from_bytes(code[off:off+4],'little'); op,rd,f3,rs1=w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31
            if op==0x17: regs[rd]=(pc+(w&0xfffff000))&MASK; pc+=4
            elif op==0x13 and f3==0: regs[rd]=(regs[rs1]+signed(w>>20,12))&MASK; pc+=4
            elif op==0x03 and f3 in (4,5):
                address=(regs[rs1]+signed(w>>20,12))&MASK; width=1 if f3==4 else 2
                if address not in memory or memory[address][0]!=width: raise ValueError('unexpected input read')
                reads.append((address,width)); regs[rd]=memory[address][1]; pc+=4
            elif op==0x6f and rd==1:
                target=entry.jal_target(pc,w); regs[1]=pc+4
                return target,regs[1],tuple(regs[i] for i in (10,11,12,13)),reads,trace
            else: raise ValueError('unsupported instruction')
        regs[0]=0
    raise ValueError('no dispatch call')


def check(code,gp,handle,length,command):
    actual=run(code,gp,handle,length,command)
    expect=(0x14056,0x8a4c,(handle,command,0x2000b9d8,length),[((gp+142)&MASK,2),((gp+164)&MASK,1)],[0x8a36,0x8a3a,0x8a3e,0x8a42,0x8a46,0x8a48])
    if actual!=expect: raise ValueError(f'boundary mismatch: {actual!r}')


def main():
    image=entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x8a36-0x8000:0x8a4c-0x8000]
    if code!=EXPECTED: raise ValueError('original bytes mismatch')
    if entry.decode_mv(entry.read_at(image,0x14068,2)) != (8,12): raise ValueError('dispatcher s0 <- a2 move mismatch')
    for length in range(65536): check(code,0x20004000,0x1234,length,0xc0)
    for gp in (0,0xffffff60,0xffffff72,MASK):
        for handle in (0,0x1234,MASK):
            for command in range(256): check(code,gp,handle,514,command)
    for i in range(len(code)):
        altered=bytearray(code); altered[i]^=1
        try: check(altered,0xffffff60,0x1234,514,0xc0)
        except ValueError: continue
        raise ValueError(f'undetected byte mutation {i}')
    print('PASS: 65536 length values, 3072 gp/handle/command boundaries and 22 byte mutations')
    print('Original 0x14068 move s0 <- a2 checked separately; no complete dispatcher or hardware execution.')
    print('From synthetic 0x8a36 entry only; no checksum or full ingress path established.')

if __name__=='__main__': main()
