"""After normal return from 64298: trace to 53868 using V1.31 copied-RAM mapping.
Arguments: reference carrier and rasm2. No model of 64298 or peripheral side effects.
"""
from hashlib import sha256
from pathlib import Path
import re, subprocess, sys

def ck(ok):
    if not ok: raise ValueError('optional role continuation mismatch')

def decode(b,tool):
    code={}
    for p,i,n in [(0x537b6,0x137b6,22),(0x57ac4,0x17ac4,20),(0x63704,0x23704,18),(0x5e758,0x1e758,20),(0x2000039c,0x60c,46)]:
        raw=b[i:i+n]; end=p+n
        for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(p),'-D',raw.hex()],text=True).splitlines():
            addr,w,h,o,*args=line.split();w=int(w);ck(int(addr,16)==p and bytes.fromhex(h)==raw[p-end+n:p-end+n+w]);code[p]=(w,o,''.join(args).split(','));p+=w
        ck(p==end)
    return code

def trace(code,sp,io,shared):
    pc=0x537b6;r={'zero':0,'sp':sp};m={};events=[];ID=0x200035f5;B=0x4002420c;O=0x200033b8
    def put(p,w,v):m.update({p+i:v>>(8*i)&255 for i in range(w)})
    def get(p,w):return sum(m[p+i]<<(8*i) for i in range(w))
    for i in range(4):put(sp+4*i,4,100+i)
    put(B,4,io);put(ID,1,shared)
    for _ in range(180):
        if pc==0x53868:break
        at=pc;w,o,x=code[at];pc+=w;t=x[0]
        def addr(s):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (r[k]+int(d))&0xffffffff
        if o in ('sw','sb','lw'):
            p=addr(x[1]);n=1 if o=='sb' else 4
            if o=='lw':r[t]=get(p,n)
            else:events.append((p,n,r[t]));put(p,n,r[t])
        elif o=='li':r[t]=int(x[1],0)
        elif o in ('auipc','lui'):r[t]=((at if o=='auipc' else 0)+(int(x[1],0)<<12))&0xffffffff
        elif o in ('add','addi'):r[t]=(r[x[1]]+(r[x[2]] if o=='add' else int(x[2],0)))&0xffffffff
        elif o=='jal':ck(t=='ra');r[t]=pc;pc=int(x[-1],0)
        elif o=='jr':pc=addr(t)&~1
        elif o=='j':pc=int(t,0)
        elif o=='ret':pc=r['ra']&~1
        elif o in ('beqz','bnez','bne'):
            b=r[x[1]] if o=='bne' else 0
            if (r[t]==b)==(o=='beqz'):pc=int(x[-1],0)
        elif o!='fence.i':raise ValueError((at,o))
    expected=[(B,4,0)]+[(0x20003454+i,1,0) for i in range(28)]+[(B,4,io),(O+196,4,0),(O+192,1,0),(O+200,1,0),(O+204,4,0)]
    ck(pc==0x53868 and events==expected and get(ID,1)==shared and r['sp']==sp+16 and [r[k] for k in ('s2','s1','s0','ra')]==list(range(100,104)))

if __name__=='__main__':
    b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22');code=decode(b,sys.argv[2])
    for sp in (0x2000ff40,0x2000ff60):
        for io in (0,0x12345678,0xffffffff):
            for shared in (0,11,255):trace(code,sp,io,shared)
    print('PASS: 18 post-return traces to 53868; 34 ordered stores each; shared ID untouched')
