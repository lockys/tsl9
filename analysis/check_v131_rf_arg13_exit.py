"""Check control-flow convergence, not device execution. Arguments: reference BIN, rasm2."""
from hashlib import sha256
from pathlib import Path
import subprocess
import sys


def check(blob, tool):
    if sha256(blob).hexdigest() != '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22':
        raise ValueError('wrong reference')
    lo, hi = 0x63e58, 0x63fa0
    pc = lo
    code = {}
    for line in subprocess.check_output([tool, '-a', 'riscv', '-b', '32', '-s', hex(lo), '-D', blob[lo-0x40000:hi-0x40000].hex()], text=True).splitlines():
        a, n, h, op = line.split(maxsplit=3)
        n = int(n)
        if int(a,16) != pc or bytes.fromhex(h) != blob[pc-0x40000:pc-0x40000+n]:
            raise ValueError('disassembly mismatch')
        code[pc] = (pc+n, op)
        pc += n
    if pc != hi: raise ValueError('incomplete window')
    anchors = {0x63f00:'beqz a5, 0x63f56',0x63f0e:'mv s1, a0',0x63f26:'jalr a5',0x63f28:'li a4, 6',0x63f2a:'bne s1, a4, 0x63f6a',0x63f6a:'li a5, 7',0x63f6c:'bne s1, a5, 0x63f7e',0x63f52:'jal ra, 0x63e58',0x63ed4:'sb zero, 7(a5)',0x63ed8:'ret',0x63f5e:'sw s2, 524(a5)',0x63f68:'ret'}
    if any(code[p][1] != op for p,op in anchors.items()): raise ValueError('unexpected anchor')
    ends=[]
    def walk(p, seen):
        if p in seen: raise ValueError('unexpected cycle')
        q, op = code[p]; path = seen+(p,); name=op.split()[0]
        if p==0x63f68:
            for point in (0x63f4a,0x63f52,0x63ed4,0x63ed8,0x63f56,0x63f5e):
                if point not in path: raise ValueError('missing common path')
            ends.append(path);return
        if p==0x63ed8: return walk(0x63f56,path)
        if p==0x63f26: return walk(q,path)  # assumes callback returns with s0/s1/s2 and stack preserved
        if p in (0x63f2a,0x63f6c) or name in ('jal','j'): return walk(int(op.split()[-1],16),path)
        if name in ('beq','bne','beqz','bnez'): walk(int(op.split()[-1],16),path)
        elif name not in ('lui','addi','lw','sw','sb','andi','ori','and','or','srli','li','mv','nop','fld','fsd'): raise ValueError(op)
        walk(q,path)  # fld/fsd labels here stand for assumed fall-through WCH data accesses
    walk(0x63f02,())
    print('PASS:',len(ends),'structural paths;',sum(0x63f26 in x for x in ends),'with assumed callback return; all reach inner restore')

if __name__=='__main__': check(Path(sys.argv[1]).read_bytes(),sys.argv[2])
