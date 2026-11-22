"""CLI: python SCRIPT V131 rasm2. Small caller/helper trace, stops at fresh ID load
or at the first unmodelled registration on the zero flag path. No hardware.
"""
from hashlib import sha256
from pathlib import Path
import re, subprocess, sys

ID=0x200035f5
FLAG=0x2000319f

def need(ok,msg):
    if not ok: raise ValueError(msg)

def decode(b,tool):
    code={}
    for lo,hi in [(0x6dd86,0x6dd96),(0x5a004,0x5a026),(0x60856,0x6089a),(0x58ef2,0x58f14)]:
        raw=b[lo-0x40000:hi-0x40000];pc=lo
        for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
            a,n,h,op,*args=line.split();n=int(n);need(int(a,16)==pc and bytes.fromhex(h)==raw[pc-lo:pc-lo+n],'instruction span')
            code[pc]=(n,op,[x.rstrip(',') for x in args]);pc+=n
        need(pc==hi,'window end')
    return code

def run(code,flag,shared):
    sp=0x2000ffc0;pc=0x6dd86;r=dict(sp=sp,ra=0x8ebe,a0=24);m={FLAG:flag,ID:shared};stores=[];calls=[]
    def value(x):return r[x] if x in r else int(x,0)
    def address(x):
        d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x).groups();return (int(d)+r[k])&0xffffffff
    for _ in range(100):
        if pc in (0x43c4e,0x6dd96):break
        n,o,x=code[pc];pc+=n;t=x[0] if x else ''
        if o in ('lw','lbu','sw'):
            p=address(x[1]);w=1 if o=='lbu' else 4
            if o=='sw':
                stores.append((p,r[t]));m.update({p+i:r[t]>>(8*i)&255 for i in range(4)})
            else:r[t]=sum(m[p+i]<<(8*i) for i in range(w))
        elif o=='addi':r[t]=(value(x[1])+value(x[2]))&0xffffffff
        elif o=='lui':r[t]=value(x[1])<<12
        elif o=='jal':r['ra']=pc;pc=value(x[-1]);calls.append(pc)
        elif o=='ret':pc=r['ra']&~1
        elif o=='bnez':pc=value(x[-1]) if r[t] else pc
        else:raise ValueError(o)
    stack=[(sp-4,0x8ebe),(sp-20,0x6dd8e),(sp-36,0x5a00c)]
    need(m[ID]==shared and all(not p<=ID<p+4 for p,_ in stores),'ID changed')
    if flag:
        fixed=[(0x2000343c,0x5e8bc),(0x200034f8,0x60516),(0x20003450,0x57cbe),(0x200034f0,0x58c52),(0x200034f4,0x595b8)]
        need((pc,r['a5'],r['sp'])==(0x6dd96,shared,sp-16) and stores==stack+fixed and calls==[0x5a004,0x60856,0x58ef2],'nonzero trace')
    else:need(pc==0x43c4e and r['a0']==0x5352c and stores==stack and calls==[0x5a004,0x60856,0x43c4e],'zero boundary')

if __name__=='__main__':
    b=Path(sys.argv[1]).read_bytes();need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22','reference identity');code=decode(b,sys.argv[2])
    for flag in range(256):
        for shared in (0,11,255):run(code,flag,shared)
    print('PASS: 765 nonzero traces to fresh ID sample, 5 fixed non-stack writes each; 3 zero traces stop at registration of 5352c')
