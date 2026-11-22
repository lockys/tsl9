"""Audit register destinations and the one wait in three RF callees. Inputs: V1.31 BIN, rasm2."""
from hashlib import sha256
from pathlib import Path
import subprocess
import sys


def audit(blob, tool):
    if sha256(blob).hexdigest() != '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22':
        raise ValueError('wrong carrier')
    def window(lo, hi):
        pc = lo
        ops = {}
        raw = blob[lo-0x40000:hi-0x40000]
        for line in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',raw.hex()],text=True).splitlines():
            addr, n, h, op = line.split(maxsplit=3)
            n = int(n)
            if int(addr,16)!=pc or n not in (2,4) or bytes.fromhex(h)!=raw[pc-lo:pc-lo+n]:
                raise ValueError('decode mismatch')
            ops[pc] = op
            pc += n
        if pc!=hi: raise ValueError('incomplete decode')
        return ops
    seq = window(0x64246,0x64256)
    if list(seq.values()) != ['jal ra, '+hex(x) for x in (0x6645c,0x67198,0x662da,0x6636e)]: raise ValueError('caller')
    for lo,hi in [(0x67198,0x671aa),(0x662da,0x6636e),(0x6636e,0x663a6)]:
        ops = window(lo,hi)
        branches = {}
        for pc,op in ops.items():
            name = op.split()[0]
            if name in ('lw','li','lui','addi','andi','ori','and','or','srli'):
                if op.split()[1].rstrip(',') not in ('a2','a3','a4','a5'): raise ValueError(op)
            elif name=='beqz': branches[pc]=op
            elif name=='ret' and pc==hi-2: pass
            elif name not in ('sw','nop'): raise ValueError(op)
        if ops[hi-2]!='ret': raise ValueError('no return')
        if lo==0x662da:
            poll={0x6632e:'lw a5, 100(a2)',0x66330:'beqz a5, 0x6633c',0x66332:'lw a5, 156(a3)',0x66336:'srli a5, a5, 0x8',0x66338:'andi a5, a5, 1',0x6633a:'beqz a5, 0x6632e'}
            if any(ops[p]!=o for p,o in poll.items()) or set(branches)!={0x66330,0x6633a}: raise ValueError('poll mismatch')
        elif branches: raise ValueError('unexpected branch')
        print(f'PASS {lo:#x}: {len(ops)} instructions, {len(branches)} conditional branches, no s4 destination or nested call')
    first = window(0x6645c,0x66480)
    if first[0x6645c]!='addi sp, sp, -80' or first[0x66470]!='sw s4, 56(sp)': raise ValueError('first frame')
    print('First callee saves s4 at entry SP-24; its reload and frame integrity not verified here.')

if __name__=='__main__': audit(Path(sys.argv[1]).read_bytes(),sys.argv[2])
