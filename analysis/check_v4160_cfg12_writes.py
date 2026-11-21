"""Inventory RV32 stores in two fixed APP windows. Supply the decoded APP BIN."""
from pathlib import Path
from hashlib import sha256
import sys


def check(b):
    if sha256(b).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('APP identity')

    def stores(start, stop):
        p = start
        rows = []
        while p < stop:
            i = p - 0x8000
            h = int.from_bytes(b[i:i+2], 'little')
            size = 4 if h & 3 == 3 else 2
            if size == 4:
                w = int.from_bytes(b[i:i+4], 'little')
                if w & 127 == 35:
                    imm = ((w >> 25) << 5) | ((w >> 7) & 31)
                    rows.append(((w >> 15) & 31, (imm ^ 2048)-2048, 1 << ((w >> 12) & 7)))
            elif h >> 13 == 6 and h & 3 == 2:  # c.swsp
                rows.append((2, ((h >> 9) & 15)*4 + ((h >> 7) & 3)*64, 4))
            p += size
        if p != stop:
            raise ValueError('window boundary')
        return rows

    direct = [(16,4),(20,2),(24,4),(30,2),(32,2),(34,1),(36,2),(72,4),(76,4),(52,4),(46,2),(60,4),(48,2),(64,4)]
    if stores(0x19a3a,0x19aec) != [(2,o,n) for o,n in direct]+[(14,23,1)]:
        raise ValueError('caller stores')
    if stores(0x18f56,0x18f88) != [(10,o,1) for o in range(6)]:
        raise ValueError('helper stores')
    touched = {i for o,n in direct for i in range(o,o+n)} | set(range(8,14)) | set(range(40,46))
    if touched & {28,29}:
        raise ValueError('field overwritten')
    print('PASS: 14 direct stack stores, 6 helper bytes, 6 loop destinations; sp+28..29 untouched after clear')


if __name__ == '__main__':
    check(Path(sys.argv[1]).read_bytes())
