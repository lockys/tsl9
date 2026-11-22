"""Args: V1.31 reference BIN, rasm2. Offline, conditional WCH compressed byte load."""
from hashlib import sha256
from pathlib import Path
import subprocess, sys


def check(ok):
    if not ok: raise ValueError('RF join mismatch')


def audit(image, tool):
    check(sha256(image).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    lo,hi=0x665b0,0x67190; raw=image[lo-0x40000:hi-0x40000]; pc=lo; code=[]
    for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
        addr,n,h,op=line.split(maxsplit=3); n=int(n);check(int(addr,16)==pc and n in (2,4) and bytes.fromhex(h)==raw[pc-lo:pc-lo+n]);code.append((pc,op));pc+=n
    check(pc==hi and code[-1]==(0x6718e,'ret') and all(op.split()[0] in 'lbu fld lui sw lw addi sub andi li or mul div slli and ori srli'.split() for _,op in code[:-1]))
    check(code[-3:]==[(0x6718a,'lw s11, 28(sp)'),(0x6718c,'addi sp, sp, 80'),(0x6718e,'ret')] and (0x67172,'lw ra, 76(sp)') in code)
    prefix=code[:next(i+1 for i,(at,_) in enumerate(code) if at==0x6662c)]; M=0xffffffff
    for d in range(-255,256):
        first,last=max(d,0),max(-d,0); r={'s0':0x20003000,'s3':0x20003000,'s1':0x20002fa6,'sp':0x2000ff00}; B=0x40025000; sampled=[0x12345678,0xfedcba98]; outs=[];ram={0x20003594:last,0x20002fa6:first,0x20003590:B}
        for at,op in prefix:
            t,*args=op.replace(',','').split(); rd=args[0]
            if at==0x665b4:
                check(raw[4:6]==bytes.fromhex('9420'));t='lbu';rd='a3';args=[rd,'0(s1)']
            if t in ('lw','lbu','sw'):
                off,k=args[1][:-1].split('(');p=r[k]+int(off)
                if t=='sw':
                    if p==B+160:outs.append(r[rd])
                    else:check(p==r['sp']+8);ram[p]=r[rd]
                else:r[rd]=sampled[len(outs)] if p==B+160 else ram[p]
            else:
                v=lambda k:r[k] if k in r else int(k,0)
                a=v(args[1]); b=v(args[2]) if len(args)>2 else 0
                if t=='div':
                    signed=a if a<2**31 else a-2**32;check(b==39);z=(abs(signed)//b)*(-1 if signed<0 else 1)
                elif t=='li':z=a
                elif t=='lui':z=a<<12
                elif t=='addi':z=a+b
                elif t=='andi':z=a&b
                elif t=='sub':z=a-b
                elif t=='mul':z=a*b
                elif t=='or':z=a|b
                elif t=='slli':z=a<<b
                else:raise ValueError(op)
                r[rd]=z&M
        check(outs==[(sampled[0]&~15)|(d&15),(sampled[1]&~240)|((int(d*38/39)&15)<<4)])
    print(f'PASS: {len(code)} linear instructions through ret; 511 signed differences, 1022 word stores matched independent samples')

if __name__=='__main__':audit(Path(sys.argv[1]).read_bytes(),sys.argv[2])
