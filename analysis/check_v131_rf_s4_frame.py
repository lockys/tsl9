"""Trace both local paths of reference routine 6645c. External calls assumed to return."""
from hashlib import sha256
from pathlib import Path
import re
import subprocess
import sys


def audit(image, tool):
    lo, hi = 0x6645c, 0x67198
    if sha256(image).hexdigest() != '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22':
        raise ValueError('wrong reference')
    raw = image[lo-0x40000:hi-0x40000]
    code = {}; p = lo
    for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
        addr,n,h,op = line.split(maxsplit=3); n=int(n)
        if int(addr,16)!=p or n not in (2,4) or bytes.fromhex(h)!=raw[p-lo:p-lo+n]: raise ValueError('decode')
        code[p]=(p+n,op); p+=n
    if p!=hi: raise ValueError('window')
    for taken in (False,True):
        p=lo; depth=0; frame=[]; calls=[]; seen=set(); last_s4=None
        while True:
            if p in seen: raise ValueError('cycle')
            seen.add(p); q,op=code[p]; name=op.split()[0]
            if name=='beq':
                if (p,op)!=(0x664d0,'beq a2, a4, 0x67190'): raise ValueError(op)
                if taken: q=0x67190
            elif name=='j':
                if (p,op)!=(0x67194,'j 0x665b0'): raise ValueError(op)
                q=0x665b0
            elif name=='jalr':
                prev=code[p-4][1]; imm=re.fullmatch(r'auipc ra, (0x[0-9a-f]+)',prev)
                off=re.fullmatch(r'jalr (-?\d+)\(ra\)',op)
                calls.append(((p-4+(int(imm[1],16)<<12)+int(off[1])) & 0xfffffffe))
            elif op.startswith('addi sp, sp, '): depth+=int(op.rsplit(' ',1)[1])
            elif name in ('sw','sb','fsd','lw') and '(sp)' in op:
                d=depth+int(op.split(', ')[1].split('(')[0]); width={'sb':1,'fsd':8}.get(name,4)
                if d < -20 and d+width > -24: frame.append((p,op,d))
            elif name=='ret':
                if p!=0x6718e or depth!=0: raise ValueError('return frame')
                break
            elif name not in 'sw sb fsd lw lui andi and or ori auipc srli lbu fld sub li mul div slli addi'.split(): raise ValueError(op)
            if op.split()[1].rstrip(',')=='s4' and name not in ('sw','sb','fsd'): last_s4=p
            p=q
        if frame!=[(0x66470,'sw s4, 56(sp)',-24),(0x6717c,'lw s4, 56(sp)',-24)] or last_s4!=0x6717c: raise ValueError('s4 slot')
        if calls!=([0x20002df2]*3 if not taken else []): raise ValueError('helper targets')
        print(f'PASS: branch taken={taken}, {len(seen)} local instructions, {len(calls)} calls, s4 saved/reloaded at entry SP-24')

if __name__=='__main__': audit(Path(sys.argv[1]).read_bytes(),sys.argv[2])
