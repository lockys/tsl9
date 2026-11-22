"""From APP post-fill to reference config gate; assumes a stable stack, successful reads, and V1.31 mapping. No device access."""
from hashlib import sha256
from itertools import product
from pathlib import Path
import re, subprocess, sys
from check_v4160_config_rejections import check, decode


def verify(app, rom, tool):
    check(sha256(app).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'APP identity')
    check(sha256(rom).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'ROM identity')
    code = decode(app,rom,tool)
    for lo,hi in [(0x19a3a,0x19ae6),(0x18f56,0x18f88)]:
        pc = lo
        for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',app[lo-32768:hi-32768].hex()],text=True).splitlines():
            addr,n,h,op,*args = line.split(); n = int(n)
            check(int(addr,16)==pc and bytes.fromhex(h)==app[pc-32768:pc-32768+n], 'APP bytes')
            code[pc]=n,op,''.join(args).split(','); pc+=n
        check(pc==hi,'window end')
    for mask,high in product(range(64),(0,0xbeef,0xffff)):
        six=bytes(255 if mask>>i&1 else 0x51+i for i in range(6))
        sp=0x2000ff70; cfg=sp+16; src=0x1ffff7e8; mem={}; samples=[]; incoming=[]
        def put(p,w,v):
            for i in range(w): mem[p+i]=v>>(8*i)&255
        def get(p,w): return int.from_bytes(bytes(mem[p+i] for i in range(w)),'little')
        put(cfg,64,0); put(src,8,int.from_bytes(six,'little')+(high<<48)); put(0x4002420c,4,17)
        for off in (124,164): put(0x40000+off,4,int.from_bytes(rom[off:off+4],'little'))
        r=dict(sp=sp,s0=0x40000,s1=111,ra=0,zero=0); pc=0x19a3a
        for _ in range(300):
            if pc in (0x19af0,0x43cc4): break
            if pc==0x43c7e: incoming.append((r['a0'],tuple(get(cfg+d,w) for d,w in [(0,4),(4,2),(8,4),(56,4),(60,4)]),get(cfg+24,6)))
            at=pc; n,op,x=code[pc]; pc+=n; t=x[0]
            def val(s): return r[s] if s in r else int(s,0)
            def addr(s):
                d,k=re.fullmatch(r'(-?\d+)\((\w+)\)',s).groups(); return (r[k]+int(d))&0xffffffff
            if op in ('lw','lbu','lhu','sw','sb','sh'):
                p=addr(x[1]); w={'lw':4,'sw':4,'lbu':1,'sb':1,'lhu':2,'sh':2}[op]
                if op.startswith('s'): put(p,w,r[t])
                else:
                    r[t]=get(p,w)
                    if at in (0x18f5a,0x18f78): samples.append((p,w))
            elif op in ('li','lui','auipc','mv','addi','add','and','srli'):
                v=val(x[1]); r[t]=(v if op in ('li','mv') else v<<12 if op=='lui' else at+(v<<12) if op=='auipc' else v&val(x[2]) if op=='and' else v>>val(x[2]) if op=='srli' else v+val(x[2]))&0xffffffff
            elif op in ('beq','beqz','bne','bnez','bleu'):
                y=0 if op.endswith('z') else val(x[1]); take=r[t]<=y if op=='bleu' else ((r[t]==y)==op.startswith('beq'))
                if take: pc=val(x[-1])
            elif op in ('jal','jalr'):
                target=val(x[-1]) if op=='jal' else addr(t) if '(' in t else r[t]; r['ra']=pc; pc=target&~1
            elif op=='ret': pc=r['ra']&~1
            elif op=='j': pc=val(t)
            elif op!='fence.i': raise ValueError(op)
        check(samples==[(src,4),(src+4,4)],'hardware input read addresses')
        check(incoming==[(cfg,(0x2000418c,0x7000,0x08077c00,0x1979a,0x197be),int.from_bytes(six,'little'))],'APP-supplied arguments')
        check((pc,r['a0'])==(0x19af0,3) if mask==63 else pc==0x43cc4,'gate outcome')
    print('PASS: 192 APP-to-gate traces; 189 admitted, 3 status-3 returns; upper 16 bits unused')

if __name__=='__main__': verify(*(Path(p).read_bytes() for p in sys.argv[1:3]),sys.argv[3])
