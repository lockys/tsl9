"""Trace accepted config copy to first page-length sample. Args: APP, V1.31, rasm2.
Synthetic source config, stack, MMIO and page; reference RAM mapping and Xwchc assumed.
"""
from hashlib import sha256
from pathlib import Path
import re, subprocess, sys

def ck(x):
    if not x: raise ValueError('geometry chain mismatch')
a,b=[Path(x).read_bytes() for x in sys.argv[1:3]]
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
code={}; compact='s0 s1 a0 a1 a2 a3 a4 a5'.split()
def window(img,base,lo,hi):
    raw=img[lo-base:hi-base];p=lo
    for line in subprocess.check_output([sys.argv[3],'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
        addr,n,h,o,*args=line.split();n=int(n);ck(int(addr,16)==p and bytes.fromhex(h)==raw[p-lo:p-lo+n]);x=''.join(args).split(',')
        if o in ('fld','fsd'):
            w=int.from_bytes(bytes.fromhex(h),'little');q=w&3;f=w>>13;ck(img is b and q in (0,2) and f in (1,5));d=8*((w>>10)&(7 if q==2 else 3))+2*(w>>5&3)+(0 if q==2 else w>>12&1);o=('lhu' if q==2 else 'lbu') if f==1 else ('sh' if q==2 else 'sb');x=[compact[w>>2&7],f'{d}({compact[w>>7&7]})']
        code[p]=n,o,x;p+=n
    ck(p==hi)
for l,h in [(0x197f0,0x1995c),(0x8520,0x854a),(0x19124,0x19142),(0x1908c,0x1909e),(0x188e2,0x189fe),(0x19160,0x1917e),(0x18a66,0x18aa6),(0x1979a,0x197b8)]:window(a,0x8000,l,h)
for l,h in [(0x43cc4,0x43d4e),(0x43b3e,0x43c06),(0x430e0,0x43174),(0x4329a,0x432a4),(0x44022,0x44072)]:window(b,0x40000,l,h)
for l,h in [(0x40,0x110),(0x332,0x36c),(0x39c,0x3ca)]:window(b,0x20000000-0x270,0x20000000+l,0x20000000+h)
M=0xffffffff;C=0x200031ec;U=0x2000ff80;S=0x2000ff50;A=0x08077c00;B=0x40012400
for length,count in [(0,3),(513,7),(1,0)]:
 for equal in (False,True):
    mem={};events=[];vis=[];polls=0;pc=0x43cc4;r={'zero':0,'sp':S,'ra':0,'s1':U,**{'s'+str(i):i for i in range(2,12)}}
    def put(p,n,v):mem.update({p+i:v>>(8*i)&255 for i in range(n)})
    def get(p,n):return sum(mem[p+i]<<(8*i) for i in range(n))
    put(U,64,0);put(U,4,0x2000418c);put(U+4,2,0x7000);put(U+8,4,A);put(U+12,4,length+(count<<16)+(8<<24));put(U+44,4,0x197f0);put(U+56,4,0x1979a);put(U+60,4,0x197be);put(A,4,A^int(not equal));put(0x4004c,4,int.from_bytes(b[76:80],'little'))
    for p in [0x4002420c,0x40021004,0x40021018,0x4002100c,B+76,*range(B,B+60,4)]:put(p,4,p)
    for step in range(20000):
        if pc in (0x44038,0x20000040) and 0x44022 in vis:break
        if pc in (0x197f0,0x43d3a,0x43104,0x20000040,0x43be2,0x44022,0x1979a):vis.append(pc)
        at=pc;n,o,x=code[pc];pc+=n;t=x[0];v=lambda s:r[s] if s in r else int(s,0)
        def addr(s):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (r[k]+int(d))&M
        if o in ('sw','sh','sb','lw','lhu','lbu'):
            p=addr(x[1]);w={'sw':4,'lw':4,'sh':2,'lhu':2,'sb':1,'lbu':1}[o]
            if o[0]=='s':put(p,w,r[t])
            elif at==0x18a8e:ck(p==B);r[t]=2 if polls else 0;polls+=1
            else:r[t]=get(p,w)
            if p<C+15 and p+w>C+12:events.append((at,o,p-C,w))
        elif o=='jal':r['ra']=pc;pc=v(x[-1])
        elif o=='jalr':dest=(addr(t) if '(' in t else r[t])&~1;r['ra']=pc;pc=dest
        elif o=='j':pc=v(t)
        elif o=='ret':pc=r['ra']&~1
        elif o in ('beq','bne','beqz','bnez','bltu','bleu'):
            y=0 if o.endswith('z') else v(x[1]);take=r[t]==y if o.startswith('beq') else r[t]!=y if o.startswith('bne') else r[t]<y if o=='bltu' else r[t]<=y;pc=v(x[-1]) if take else pc
        elif o in ('li','mv','lui','auipc','snez','not'):
            y=v(x[1]);r[t]=((y<<12)+at if o=='auipc' else y<<12 if o=='lui' else int(y!=0) if o=='snez' else ~y if o=='not' else y)&M
        elif o in ('add','addi','sub','and','andi','or','ori','mul','sll','slli','srli'):
            y,z=map(v,x[1:]);r[t]=(y+z if o in ('add','addi') else y-z if o=='sub' else y*z if o=='mul' else y&z if o in ('and','andi') else y|z if o in ('or','ori') else y>>(z&31) if o=='srli' else y<<(z&31))&M
        elif o!='fence.i':raise ValueError((hex(at),o))
    ck(vis==[0x197f0,0x43d3a,0x43104,0x20000040,0x43be2,0x44022,0x1979a] and polls==2)
    defaults=[(0x43cf0,'lhu',12,2)]+([] if length else [(0x43cf8,'sh',12,2)])+[(0x43cfa,'lbu',14,1)]+([] if count else [(0x43d00,'sb',14,1)])
    ck(len(events)==6+len(defaults)+int(not equal) and events[6:]==defaults+([] if equal else [(0x44060,'lhu',12,2)]))
    ck([e[1:] for e in events[:6]]==[('sb',i,1) for i in (12,13,14)*2]);ck(get(C+12,2)==(length or 256) and get(C+14,1)==(count or 1))
    ck(pc==(0x44038 if equal else 0x20000040) and (equal or (r['a0'],r['a1'])==((length or 256),78)))
print('PASS: 6 continuous config-copy to readback traces; 3 mismatch length samples, 3 equal exits')
