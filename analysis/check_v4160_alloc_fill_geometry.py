"""Reference normal path from 43b8c to 43be2 on a fresh large free block.
Usage: python check_v4160_alloc_fill_geometry.py V131-carrier rasm2
No device access. Cursor and header are inputs; payload address is not.
"""
from hashlib import sha256
from pathlib import Path
import re, subprocess, sys

def ck(x):
    if not x: raise ValueError('allocation/fill trace mismatch')

b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
code={}; regs='zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5'.split()
for lo,raw in [(0x43b8c,b[0x3b8c:0x3be2]),(0x20000040,b[0x2b0:0x380]),(0x2000039c,b[0x60c:0x63a])]:
    p=lo
    for line in subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
        a,n,h,o,*args=line.split();n=int(n);ck(int(a,16)==p and bytes.fromhex(h)==raw[p-lo:p-lo+n]);x=''.join(args).split(',')
        if o in ('fld','fsd'):
            w=int.from_bytes(bytes.fromhex(h),'little');q=w&3;f=w>>13;ck(q in (0,2) and f in (1,5));off=8*((w>>10)&(7 if q==2 else 3))+2*(w>>5&3)+(0 if q==2 else w>>12&1)
            o=('lhu' if q==2 else 'lbu') if f==1 else ('sh' if q==2 else 'sb');x=[regs[8+(w>>2&7)],f'{off}({regs[8+(w>>7&7)]})']
        code[p]=n,o,x;p+=n
    ck(p==lo+len(raw))
M=0xffffffff;G=0x2000319c;F=0x4002420c;S=0x2000ff40;E=0x2000b184;field=0x200031f8
for H in (0x200045ac,0x200046ac): # second cursor is a synthetic sensitivity check
 for c in (0,1,3,4,252,255):
    r=dict(sp=S,s0=0x20003000,ra=0,zero=0);mem={};writes=[];edges=[];pc=0x43b8c
    def put(p,n,v):mem.update({p+i:v>>(8*i)&255 for i in range(n)})
    def get(p,n):return sum(mem[p+i]<<(8*i) for i in range(n))
    for p,n,v in [(0x20003201,1,c),(0x20003190,4,H),(0x2000318c,4,E),(H,4,E),(H+4,2,E-H-8),(H+6,2,0),(G+6,2,28000),(F,4,0x1818),(field,3,0x030100)]:put(p,n,v)
    for _ in range(6500):
        if pc==0x43be2:break
        here=pc;n,o,x=code[pc];pc+=n;t=x[0];v=lambda k:r[k] if k in r else int(k,0)
        def addr(s):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups();return (r[k]+int(d))&M
        if o in ('lw','lhu','lbu','sw','sh','sb'):
            p=addr(x[1]);w={'lw':4,'lhu':2,'lbu':1,'sw':4,'sh':2,'sb':1}[o]
            if o[0]=='l':r[t]=get(p,w)
            else:put(p,w,r[t]);writes.append((here,p,w,r[t]&((1<<(8*w))-1)))
        elif o in ('auipc','lui','li'):r[t]=((here if o=='auipc' else 0)+(v(x[1])<<(0 if o=='li' else 12)))&M
        elif o in ('add','addi','sub','andi','mul','srli','slli'):
            l,h=map(v,x[1:]);r[t]=(l-h if o=='sub' else l&h if o=='andi' else l*h if o=='mul' else l>>h if o=='srli' else l<<h if o=='slli' else l+h)&M
        elif o=='jalr':dest=addr(t)&~1;r['ra']=pc;pc=dest;edges.append((pc,r['a0'],r['a1'],r.get('a2')))
        elif o=='ret':pc=r['ra']&~1
        elif o=='j':pc=v(t)
        elif o in ('bne','beqz','bnez','bltu','bleu'):
            take=(not r[t]) if o=='beqz' else bool(r[t]) if o=='bnez' else r[t]!=v(x[1]) if o=='bne' else r[t]<v(x[1]) if o=='bltu' else r[t]<=v(x[1]);pc=v(x[-1]) if take else pc
        elif o!='fence.i':raise ValueError(o)
    size=576+6*(14+3*((c>>2)+(c&3)));aligned=(size+3)&~3;P=H+8;N=P+aligned
    ck(pc==0x43be2 and edges[0][:3]==(0x20000040,size,1) and edges[1:]==[(0x2000039c,P,0,size)])
    ck(get(0x2000322c,4)==P and get(H,4)==N and get(N,4)==E and get(H+4,2)==aligned and get(H+6,2)==1 and get(N+4,2)==E-N-8)
    ck([(p,w,v) for here,p,w,v in writes if here==0x200003c0]==[(P+i,1,0) for i in range(size)])
    ck(all(p+w<=field or field+3<=p for _,p,w,_ in writes) and get(field,3)==0x030100 and P+size<=N and r['sp']==S)
print('PASS: 12 allocator-to-fill traces, cursor-derived payload, exact byte writes, geometry unchanged')
