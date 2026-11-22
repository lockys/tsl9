"""Offline V1.31 queue slice. Args: reference carrier, rasm2. No device access.
Starts after ID/count checks. Synthetic disjoint message records, ordinary RAM,
finite valid prior lists, no concurrent writes. Stops before release or event post.
"""
import hashlib, subprocess, sys
from pathlib import Path

def check(ok):
    if not ok: raise ValueError('queue append projection mismatch')

def decode(img, tool, pc, off, length):
    raw=img[off:off+length]; start=pc; code={}
    for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(pc),'-D',raw.hex()],text=True).splitlines():
        at,w,h,op,*args=line.split();w=int(w)
        check(pc==int(at,16) and bytes.fromhex(h)==raw[pc-start:pc-start+w]);code[pc]=(w,op,''.join(args).split(','));pc+=w
    check(pc==start+length);return code

def run(code,link,tag,n):
    msg=0x21000020;head=0x20003198;nodes=[msg+64*(i+1) for i in range(n)]
    r=dict(a0=msg,a1=msg,s0=7,zero=0); mem={};reads=[];writes=[]
    def put(p,w,v):mem.update((p+i,(v>>(8*i))&255) for i in range(w))
    def get(p,w):return sum(mem[p+i]<<(8*i) for i in range(w))
    def addr(x):
        d,b=x[:-1].split('(');return (int(d)+r[b])&0xffffffff
    put(msg-8,4,link);put(msg-2,1,tag);put(head,4,nodes[0] if n else 0)
    for i,p in enumerate(nodes):put(p-8,4,nodes[i+1] if i+1<n else 0)
    pc=0x4325a
    for _ in range(100):
        if pc in (0x431ba,0x4354a):break
        at=pc;w,op,x=code[pc];pc+=w;t=x[0]
        if op in ('lw','lbu'):
            p=addr(x[1]);reads.append(p);r[t]=get(p,4 if op=='lw' else 1)
        elif op in ('sw','sb'):
            p=addr(x[1]);size=4 if op=='sw' else 1;writes.append((at,p,size,r[t]));put(p,size,r[t])
        elif op in ('li','lui','auipc','addi','mv'):
            a=r[x[1]] if x[1] in r else int(x[1],0);v=a<<12 if op in ('lui','auipc') else a
            r[t]=(v+(at if op=='auipc' else int(x[2],0) if op=='addi' else 0))&0xffffffff
        elif op=='jalr':dest=addr(t)&~1;r['ra']=pc;pc=dest
        elif op=='jal':r['ra']=pc;pc=int(x[-1],0)
        elif op=='ret':pc=r['ra']&~1
        elif op=='beq':
            if r[t]==r[x[1]]:pc=int(x[-1],0)
        elif op=='bnez':
            if r[t]:pc=int(x[-1],0)
        else:raise ValueError((at,op))
    if link or tag!=255:
        check(pc==0x431ba and not writes and reads==([msg-8] if link else [msg-8,msg-2]));return False
    check(pc==0x4354a and (r['a0'],r['a1'])==(7,0x8000))
    check(reads==[msg-8,msg-2,head]+[p-8 for p in nodes])
    check(writes==[(0x4327c,msg-2,1,7),(0x2000021c,msg-8,4,0),
                   (0x20000230 if n else 0x20000224,nodes[-1]-8 if n else head,4,msg)])
    return True

if __name__=='__main__':
    img=Path(sys.argv[1]).read_bytes();check(hashlib.sha256(img).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    code=decode(img,sys.argv[2],0x4325a,0x325a,0x38);code.update(decode(img,sys.argv[2],0x2000021c,0x48c,0x1a))
    results=[run(code,link,tag,n) for n in (0,1,3) for tag in range(256) for link in (0,0x21000060)]
    check(len(results)==1536 and sum(results)==3)
    print('PASS: 1533 rejected before any queue write; 3 appended (empty/one/three prior nodes); post arguments (7,0x8000)')
