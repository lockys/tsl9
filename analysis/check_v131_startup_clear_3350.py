"""Bounded RV32 startup clear-loop check on the reference carrier, no device I/O."""
from hashlib import sha256
from pathlib import Path
import sys


def need(ok, label):
    if not ok:
        raise ValueError(label)


def check(b):
    need(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'reference identity')
    def word(offset):
        return int.from_bytes(b[offset:offset+4], 'little')
    # The entry copies a small ROM window into RAM before calling 0x6de0c.
    def pair(pc, reg):
        u, i = word(pc-0x40000), word(pc+4-0x40000)
        need(u & 4095 == reg*128+0x17 and i & 0xfffff == reg*32768+reg*128+0x13, 'auipc/addi')
        return (pc+(u & 0xfffff000)+(i >> 20)-((i >> 31) << 12)) & 0xffffffff
    src, dst, end = [pair(pc, reg) for pc, reg in [(0x6de8e,10),(0x6de96,11),(0x6de9e,12)]]
    need((src,dst,end)==(0x40280,0x20000010,0x20000040), 'entry copy range')
    need(b[0x2dea6:0x2debe].hex()=='63fcc5008322050023a0550011059105e3eac5feeff03ff5', 'copy loop and call')
    need(b[0x2de76:0x2de7e].hex()=='1723f91f6700c31a' and (0x6de76+0x1ff92000+428)==0x20000022, 'tail')
    pos = src-0x40000+(0x20000022-dst)
    code = b[pos:pos+30]
    need(code.hex()=='b737002037370020938787ef130747616373f700828023a007009107d5bf', 'clear body')
    start = 0x20003000+(int.from_bytes(code[8:12], 'little', signed=True)>>20)
    last = 0x20003000+(int.from_bytes(code[12:16], 'little', signed=True)>>20)
    writes = range(start,last+1,4)
    need((start,last,len(writes))==(0x20002ef8,0x20003614,456), 'inclusive word range')
    hits = [(i,p) for i,p in enumerate(writes) if p <= 0x20003350 < p+4]
    need(hits==[(278,0x20003350)], 'selected word')
    print('PASS: copied clear body; 456 word stores; store #279 clears 0x20003350..53')


if __name__ == '__main__':
    check(Path(sys.argv[1]).read_bytes())
