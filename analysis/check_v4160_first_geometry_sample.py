"""From V1.31 44022 entry through APP readback to first allocation call (or early exit).
Run with decoded APP, reference carrier and rasm2. Input geometry is a precondition,
not a claim about earlier init, physical flash, or which ROM a device has installed.
"""
from pathlib import Path
from hashlib import sha256
import re, subprocess, sys

def check(x):
    if not x: raise ValueError('geometry sample mismatch')

a,b=[Path(p).read_bytes() for p in sys.argv[1:3]]
check([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
code={}
for lo,raw in [(0x44022,b[0x4022:0x4072]),(0x1979a,a[0x1179a:0x117b8]),(0x20000332,b[0x5a2:0x5dc])]:
    p=lo
    for line in subprocess.check_output([sys.argv[3],'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
        addr,n,h,o,*args=line.split();n=int(n);check(int(addr,16)==p and bytes.fromhex(h)==raw[p-lo:p-lo+n]);x=''.join(args).split(',')
        if p==0x44060:check(h=='4a24');o,x='lhu',['a0','12(s0)'] # conditional Xwchc
        code[p]=n,o,x;p+=n
    check(p==lo+len(raw))
A,C,S,F=0x08077c00,0x200031ec,0x2000ff20,0x4002420c
for length in (0,1,255,256,65535):
 for count in (0,3,255):
  for equal in (False,True):
    mem={};r=dict(sp=S+32,s0=123,s1=456,s2=789,ra=0x43c06,zero=0);pc=0x44022;writes=[];reads=[]
    def put(p,n,v):mem.update({p+i:v>>(8*i)&255 for i in range(n)})
    def get(p,n):return sum(mem[p+i]<<(8*i) for i in range(n))
    for p,v in [(C+8,A),(C+12,length+(count<<16)+(8<<24)),(C+56,0x1979a),(C+60,0x197be),(A,A if equal else A^1),(F,0xa1234567),(0x4004c,int.from_bytes(b[76:80],'little'))]:put(p,4,v)
    for _ in range(160):
        if pc in (0x44038,0x20000040):break
        here=pc;n,o,x=code[pc];pc+=n;t=x[0];v=lambda k:r[k] if k in r else int(k,0)
        def addr(s):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (r[k]+int(d))&0xffffffff
        if o in ('lw','lbu','lhu','sw','sb'):
            p=addr(x[1]);w={'lw':4,'lbu':1,'lhu':2,'sw':4,'sb':1}[o]
            if o.startswith('l'):r[t]=get(p,w);reads.append((here,p,w))
            else:put(p,w,r[t]);writes.append((p,w))
        elif o in ('li','mv','lui','auipc'):r[t]=(v(x[1])*(4096 if o in ('lui','auipc') else 1)+(here if o=='auipc' else 0))&0xffffffff
        elif o in ('add','addi','slli'):r[t]=(v(x[1])<<v(x[2]) if o=='slli' else v(x[1])+v(x[2]))&0xffffffff
        elif o=='jalr':target=(addr(t) if '(' in t else r[t])&~1;r['ra']=pc;pc=target
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=v(t)
        elif o in ('beq','bne','beqz','bnez'):
            rhs=0 if o.endswith('z') else v(x[1]);pc=v(x[-1]) if (r[t]==rhs)==o.startswith('beq') else pc
        elif o!='fence.i':raise ValueError(o)
    check(writes==[(S+24,4),(S+28,4),(S+20,4),(S+16,4),(S-4,4),(F,4)]+[(S+12+i,1) for i in range(4)]+[(F,4)])
    relevant=[row for row in reads if row[1]<C+15 and row[1]+row[2]>C+12];check(relevant==([] if equal else [(0x44060,C+12,2)]))
    check(get(C+12,4)==length+(count<<16)+(8<<24) and pc==(0x44038 if equal else 0x20000040))
    if not equal:check((r['a0'],r['a1'])==(length,78))
print('PASS: 30 entry-to-boundary traces; 11 ordered stores each; 15 halfword samples, no page-count read')
