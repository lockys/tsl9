"""Caller trace with bounded APP tail outcomes; not a whole-device interpreter."""
from hashlib import sha256
from pathlib import Path
import re
import subprocess
import sys


def check(ok):
    if not ok:
        raise ValueError('three-page trace mismatch')


def run(rom, tool):
    b = Path(rom).read_bytes()
    check(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    p, end = 0x4408e, 0x440c2
    rows = subprocess.check_output([tool, '-a', 'riscv', '-b', '32', '-s', hex(p), '-D', b[p-0x40000:end-0x40000].hex()], text=True)
    code = {}
    for line in rows.splitlines():
        addr, n, raw, op, *args = line.split(); n = int(n)
        check(int(addr, 16) == p and bytes.fromhex(raw) == b[p-0x40000:p-0x40000+n])
        if p in (0x4408e, 0x440ac):
            h, op, args = {0x4408e: ('7c24','lbu',['a5,14(s0)']),0x440ac: ('4e24','lhu',['a1,12(s0)'])}[p]; check(raw == h)
        code[p] = n, op, ''.join(args).split(','); p += n
    check(p == end)
    C, K, P, A = 0x200031ec, 0x200031bc, 0x20004b00, 0x08077c00
    for stop, gate in [(j,g) for j in range(3) for g in (0x18f2a,0x18f44,0x1978c)] + [(3,None)]:
        # Distinct sentinel makes clearing K+4 observable. All callback side effects
        # outside the five modeled caller locations are intentionally omitted.
        mem = {C+14:3,C+12:256,C+8:A,C+60:0x197be,K:P,K+4:123,P:0}
        r = dict(s0=C,s1=K-32,s2=0,zero=0); pc=0x4408e; events=[]; loads=[]
        for _ in range(100):
            if pc == 0x4403a:break
            here=pc; n,op,x=code[pc]; pc+=n; t=x[0]; v=lambda s:r[s] if s in r else int(s,0)
            def addr(s):
                d,k=re.fullmatch(r'(\d+)\((\w+)\)',s).groups();return r[k]+int(d)
            if op in ('lw','lhu','lbu'):
                r[t]=mem[addr(x[1])]&{'lw':0xffffffff,'lhu':65535,'lbu':255}[op];loads.append(here)
            elif op=='sw':
                a=addr(x[1]);mem[a]=r[t];events.append(('store',a,r[t]))
            elif op=='blt':pc=v(x[2]) if r[t]<v(x[1]) else pc  # both nominal values nonnegative
            elif op in ('li','mv'):r[t]=v(x[1])
            elif op=='auipc':r[t]=(here+(v(x[1])<<12))&0xffffffff
            elif op in ('addi','add','mul','srli'):
                l,h=map(v,x[1:]);r[t]=(l*h if op=='mul' else l>>h if op=='srli' else l+h)&0xffffffff
            elif op=='jalr':
                target=(addr(t) if '(' in t else r[t])&~1;r['ra']=pc
                if target==0x197be:
                    events.append(('page',r['a0'],r['a1'],r['a2'],r['s2'],pc))
                    if r['s2']==stop+1 and gate is not None:pc=gate;break
                    r['a0']=0
                else:check(target==0x20000110);events.append(('release',r['a0']));r['a0']=99
            elif op=='j':pc=v(t)
            else:raise ValueError(op)
        wanted=[]; count=min(stop+1,3)
        for i in range(count):
            a=A+256*i;wanted += [('store',P,a),('page',a,64,P,i+1,0x440c0)]
        if gate is None:wanted += [('release',P),('store',K,0),('store',K+4,0)]
        check(events==wanted and pc==(gate or 0x4403a) and mem[P]==A+256*(count-1))
        check(loads.count(0x4408e)==loads.count(0x44090)==count+int(gate is None))
        check((mem[K],mem[K+4])==((P,123) if gate else (0,0)))
    print('PASS: 9 page/wait cutoffs; 1 all-return trace; release precedes both cache clears')


if __name__=='__main__':run(*sys.argv[1:])
