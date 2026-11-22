"""Usage: python check_v4160_flag_subtree.py APP.bin rasm2"""
import hashlib
from pathlib import Path
import subprocess
import sys

RANGES = {0x16b0a:0x16b50, 0x16994:0x169dc, 0x16a7c:0x16b0a,
          0x16a30:0x16a7c, 0x16896:0x168de, 0x12bc8:0x12c24}

def check(image, tool):
    if hashlib.sha256(image).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('image')
    edges, indirect, starts = [], [], set()
    for start, end in RANGES.items():
        pc = start
        data = image[start-0x8000:end-0x8000]
        text = subprocess.check_output([tool, '-a','riscv','-b','32','-s',hex(pc),'-D',data.hex()], text=True)
        for line in filter(str.strip, text.splitlines()):
            addr, size, raw, ins = line.split(None, 3)
            width = int(size)
            if int(addr,16) != pc or width not in (2,4) or bytes.fromhex(raw) != data[pc-start:pc-start+width]:
                raise ValueError('instruction boundary')
            starts.add(pc)
            op = ins.split()[0]
            if op.startswith('b') or op in ('j','jal'):
                dst = int(ins.split()[-1],16)
                if not (start <= dst < end or dst in RANGES): raise ValueError('outgoing direct edge')
                edges.append(dst)
            elif op in ('jalr','jr'): indirect.append((pc,ins))
            elif op not in {'ret','addi','andi','li','lui','auipc','mv','sw','lw','lbu','lhu','sh','sb','slli','srli','or','add','mul'}:
                raise ValueError(ins)
            pc += width
        if pc != end: raise ValueError('extent')
    if set(edges)-starts or indirect != [(0x12c0c,'jalr a5')] or len(starts)!=189: raise ValueError('transfer set')
    print('PASS 6 APP ranges; 189 instruction starts; only non-return indirect transfer at 0x12c0c')

if __name__ == '__main__': check(Path(sys.argv[1]).read_bytes(), sys.argv[2])
