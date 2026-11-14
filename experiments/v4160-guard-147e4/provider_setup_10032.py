"""Decode 0x10032 through the opaque 0x40048 provider boundary.

The pointer is supplied externally. A tail transfer is not a provider call
return or evidence of what the provider does. Successful instruction/data
reads, no trap and no concurrent changes are assumed.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
path=HERE.parent/'v4160-dispatch-148b4-model'/'entry_provenance.py'
spec=importlib.util.spec_from_file_location('entry',path); entry=importlib.util.module_from_spec(spec); spec.loader.exec_module(entry)
MASK=0xffffffff
EXPECTED=bytes.fromhex('b707040003a387040d4681451385c1120283')
CALLER=bytes.fromhex('411106c6eff05f92')


def signed(x,bits): return x-(1<<bits) if x&(1<<(bits-1)) else x


def run(code,gp,ra,pointer):
    if len(code)!=18 or any(not 0<=v<=MASK for v in (gp,ra,pointer)):
        raise ValueError('invalid input')
    r=[0x5a5a5a5a]*32; r[0]=0; r[1]=ra; r[3]=gp; pc=0x10032; reads=[]; trace=[]
    while len(trace)<6:
        off=pc-0x10032
        if off<0 or off+2>len(code) or pc&1: raise ValueError('outside setup')
        h=int.from_bytes(code[off:off+2],'little'); trace.append(pc)
        if h&3!=3:
            q,f3,rd=h&3,h>>13,(h>>7)&31
            if (q,f3)==(1,2) and rd:
                r[rd]=signed((h>>2&31)|((h>>12&1)<<5),6)&MASK; pc+=2
            elif (q,f3,(h>>12)&1,h>>2&31)==(2,4,0,0) and rd:
                return (r[rd]&~1, r[1], r[10],r[11],r[12],reads,trace)
            else: raise ValueError('unsupported compressed opcode')
        else:
            if off+4>len(code): raise ValueError('truncated')
            w=int.from_bytes(code[off:off+4],'little'); op,rd,f3,rs1=w&127,w>>7&31,w>>12&7,w>>15&31
            if op==0x37: r[rd]=w&0xfffff000
            elif op==0x03 and f3==2:
                addr=(r[rs1]+signed(w>>20,12))&MASK
                if addr!=0x40048: raise ValueError('unexpected pointer read')
                reads.append(addr); r[rd]=pointer
            elif op==0x13 and f3==0: r[rd]=(r[rs1]+signed(w>>20,12))&MASK
            else: raise ValueError('unsupported opcode')
            pc+=4
        r[0]=0
    raise ValueError('no tail transfer')


def check(code,gp,ra,pointer):
    got=run(code,gp,ra,pointer)
    expected=(pointer&~1,ra,(gp+300)&MASK,0,3,[0x40048],[0x10032,0x10036,0x1003a,0x1003c,0x1003e,0x10042])
    if got!=expected: raise ValueError(f'provider boundary mismatch: {got!r}')


def main():
    image=entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x10032-0x8000:0x10044-0x8000]; caller=image[0x1070a-0x8000:0x10712-0x8000]
    if code!=EXPECTED or caller!=CALLER: raise ValueError('original bytes mismatch')
    if entry.jal_target(0x1070e,int.from_bytes(caller[4:8],'little'))!=0x10032: raise ValueError('caller target mismatch')
    for gp in range(65536): check(code,(0xffff0000+gp)&MASK,0x10712,0x12345679)
    for gp in (0,1,0xfffffed3,0xfffffed4,MASK):
        for ra in (0,0x10712,MASK):
            for pointer in (0,1,0x40048,0x12345678,MASK): check(code,gp,ra,pointer)
    for i in range(len(code)):
        bad=bytearray(code); bad[i]^=1
        try: check(bad,0xffffff00,0x10712,0x12345679)
        except ValueError: continue
        raise ValueError(f'undetected mutation at byte {i}')
    print('PASS: 65536 gp values, 75 boundary combinations and 18 opcode mutations')
    print('Decoded provider pointer load and tail boundary only; provider effects and return unknown.')

if __name__=='__main__': main()
