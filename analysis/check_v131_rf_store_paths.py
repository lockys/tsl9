"""Args: V1.31 carrier, rasm2. Abstract address/branch walk, NOT hardware execution."""
from pathlib import Path
from hashlib import sha256
import re, subprocess, sys

def need(ok):
    if not ok: raise ValueError('RF store path mismatch')

def walk(b,tool,lo,end,cut=False):
    raw=b[lo-0x40000:end-0x40000]; code={};p=lo
    for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
        addr,w,h,o,*arg=line.split();w=int(w);need(int(addr,16)==p and bytes.fromhex(h)==raw[p-lo:p-lo+w]);code[p]=(w,o,''.join(arg).split(','));p+=w
    need(p==end);todo=[(lo,{'sp':0x2000ff40})];seen=set();stores={};exits=set();edges=set()
    while todo:
        p,r=todo.pop();key=p,tuple(sorted(r.items()))
        if key in seen:continue
        seen.add(key)
        if cut and p==end:exits.add(p);continue
        w,o,x=code[p];t=x[0];n=p+w;r=r.copy()
        if o in ('sw','lw'):
            d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',x[1]).groups();need(r.get(k) is not None);a=(int(d)+r[k])&0xffffffff
            if o=='sw':stores.setdefault(p,set()).add(a)
            else:r[t]={0x20003590:0x40025000,0x2000353c:0x40024200}.get(a)
        elif o=='lui':r[t]=int(x[1],0)<<12
        elif o=='li':r[t]=int(x[1],0)
        elif o=='addi':r[t]=None if r.get(x[1]) is None else (r[x[1]]+int(x[2],0))&0xffffffff
        elif o in ('or','and','andi','ori','srli'):r[t]=None
        elif o=='beqz':
            target=int(x[-1],0);edges.add((p,target));todo.append((target,r)) # explore both, no assumption of poll termination
        elif o=='ret':exits.add(p);continue
        elif o!='nop':raise ValueError((hex(p),o))
        todo.append((n,r))
    need(all(len(a)==1 for a in stores.values()));return [next(iter(stores[p])) for p in sorted(stores)],exits,edges

if __name__=='__main__':
    b=Path(sys.argv[1]).read_bytes();need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22');tool=sys.argv[2];B=0x40025000
    for lo,end,seq,branches in [(0x67198,0x671aa,[4],set()),(0x662da,0x6636e,[80,8,12,12,12,4,0x40024264-B,80,80,8],{(0x66330,0x6633c),(0x6633a,0x6632e)}),(0x6636e,0x663a6,[88,8,12,4,12,4],set())]:
        s,e,j=walk(b,tool,lo,end);need((s,e,j)==([B+i for i in seq],{end-2},branches))
    s,e,j=walk(b,tool,0x6645c,0x664d0,True);F=0x2000ff40-80
    need(s==[F+i for i in (72,68,60,76,64,56,52,48,44,40,36,32,28)]+[B+i for i in (4,40,44,8,4)]+[F+12] and e=={0x664d0} and not j)
    print('PASS: three complete leaf CFGs: 1/10/6 word store sites; both poll edges; long prefix: 14 stack + 5 peripheral stores before first branch')
