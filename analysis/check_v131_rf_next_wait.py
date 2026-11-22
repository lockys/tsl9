"""V1.31 reference BIN, rasm2. CPU-visible addresses only, synthetic independent IO reads."""
from hashlib import sha256
from itertools import product
from pathlib import Path
import subprocess,sys


def ck(ok):
    if not ok: raise ValueError('RF wait trace mismatch')


def audit(image,tool):
    ck(sha256(image).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    code={}; B=0x40025000; T=0x40024200; M=0xffffffff
    for lo,hi in [(0x6424a,0x64252),(0x67198,0x671aa),(0x662da,0x6636e)]:
        raw=image[lo-0x40000:hi-0x40000]; pc=lo
        for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
            a,n,h,op=line.split(maxsplit=3); n=int(n);ck(int(a,16)==pc and n in (2,4) and bytes.fromhex(h)==raw[pc-lo:pc-lo+n]);code[pc]=(n,op.replace(',','').split());pc+=n
        ck(pc==hi)
    counts=[0,0,0]
    for choices in product(range(3),repeat=3): # 0: timer zero; 1: flag set; 2: still busy
        pc=0x6424a;r={}; reads=[];writes=[]; idx=-1
        for _ in range(128):
            if pc==0x64252 or (idx==2 and pc==0x6632e):break
            at=pc;n,ins=code[pc];pc+=n;o,*x=ins
            if o in ('lw','sw'):
                d,k=x[1][:-1].split('(');addr=(r[k]+int(d))&M
                if o=='sw':writes.append((at,addr,r[x[0]]));continue
                if addr==0x20003590:z=B
                elif addr==0x2000353c:z=T
                elif at==0x6632e:ck(addr==T+100);idx+=1;z=0 if choices[idx]==0 else 0xffffffff
                elif at==0x66332:ck(addr==B+156);z=0x100 if choices[idx]==1 else 0xfeff
                elif at==0x6634a:ck(addr==B+156);z=0x16 # distinct from last poll status
                else:ck(B<=addr<B+160);z=(0x76543210+at)&M
                r[x[0]]=z;reads.append((at,addr,z))
            elif o=='jal':r['ra']=pc;pc=int(x[1],0)
            elif o=='ret':pc=r['ra']&~1
            elif o=='beqz':
                if not r[x[0]]:pc=int(x[1],0)
            elif o!='nop':
                a=r[x[1]] if x[1] in r else int(x[1],0);b=(r[x[2]] if x[2] in r else int(x[2],0)) if len(x)>2 else 0
                if o=='lui':z=a<<12
                elif o=='li':z=a
                elif o=='addi':z=a+b
                elif o in ('or','ori'):z=a|b
                elif o in ('and','andi'):z=a&b
                elif o=='srli':z=a>>b
                else:raise ValueError(ins)
                r[x[0]]=z&M
        else:raise ValueError('unexpected cycle')
        exit_kind=next((x for x in choices if x!=2),2);counts[exit_kind]+=1
        expected=[]
        for x in choices:
            expected.append(T+100)
            if x!=0:expected.append(B+156)
            if x!=2:break
        ck([addr for at,addr,z in reads if at in (0x6632e,0x66332)]==expected)
        ck((0x6632c,T+100,80) in writes and all(addr!=B+160 for _,addr,_ in reads+writes))
        ck(pc==(0x6632e if exit_kind==2 else 0x64252))
        ck([(addr,z&31) for at,addr,z in writes if at==0x6635e]==([] if exit_kind==2 else [(B+80,0x16)]))
    ck(counts==[13,13,1]);print('PASS: 13 timer exits, 13 status exits, 1 bounded busy prefix; no access to B+160 from 6424a through the wait helper')

if __name__=='__main__':audit(Path(sys.argv[1]).read_bytes(),sys.argv[2])
