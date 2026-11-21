"""Inventory three V1.31 leaf bodies; assume stable initialized pointer slots."""
from hashlib import sha256
from pathlib import Path
import sys


def check(blob):
    if sha256(blob).hexdigest() != '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22':
        raise ValueError('reference identity')
    slots = {0x20003590: 0x40025000, 0x2000353c: 0x40024200}
    for start, end, expected in [
        (0x67198,0x671aa,[0x5004]),
        (0x662da,0x6636e,[0x5050,0x5008,0x500c,0x500c,0x500c,0x5004,0x4264,0x5050,0x5050,0x5008]),
        (0x6636e,0x663a6,[0x5058,0x5008,0x500c,0x5004,0x500c,0x5004]),
    ]:
        pc = start; regs = {}; writes = []
        while pc < end:
            w = int.from_bytes(blob[pc-0x40000:pc-0x40000+4], 'little'); h = w & 65535
            if h & 3 == 3:
                rd, rs, op = w>>7&31, w>>15&31, w&127
                if op == 55: regs[rd] = w & 0xfffff000
                elif op == 3 and w>>12&7 == 2: regs[rd] = slots.get(regs.get(rs,0)+((w>>20^2048)-2048))
                elif op == 19: regs.pop(rd,None)
                else: raise ValueError(hex(pc))
                pc += 4
            else:
                q, f, rs, rt = h&3, h>>13, 8+(h>>7&7), 8+(h>>2&7)
                if q == 0 and f == 2: regs.pop(rt,None)
                elif q == 0 and f == 6:
                    off = ((h>>10&7)<<3) | ((h>>6&1)<<2) | ((h>>5&1)<<6)
                    writes.append(regs[rs]+off)
                elif q == 1 and f in (0,2,3): regs.pop(h>>7&31,None)
                elif q == 1 and f == 4: regs.pop(rs,None)
                elif q == 1 and f == 6: pass  # poll branches only; not an execution trace
                elif h == 0x8082 and pc+2 == end: pass
                else: raise ValueError(hex(pc))
                pc += 2
        if pc != end or writes != [0x40020000+x for x in expected]: raise ValueError(hex(start))
        print(f'PASS {start:#x}: {len(writes)} peripheral word-store sites')


if __name__ == '__main__':
    check(Path(sys.argv[1]).read_bytes())
