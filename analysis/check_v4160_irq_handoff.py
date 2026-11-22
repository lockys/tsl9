"""Count SYSTEM opcodes only at instruction starts in pinned boot windows."""
from hashlib import sha256
from pathlib import Path
import sys


def scan(data, base, start, end):
    pc, count, system = start, 0, []
    while pc < end:
        i = pc - base
        h = int.from_bytes(data[i:i+2], 'little')
        size = 2 if h & 3 != 3 else 4
        if h & 31 == 31 or pc + size > end or len(data[i:i+size]) != size:
            raise ValueError('incomplete or long instruction')
        if size == 4 and h & 127 == 0x73:
            system.append((pc, int.from_bytes(data[i:i+4], 'little')))
        pc += size
        count += 1
    return count, system


def check(path, digest, base, spans, expected):
    data = Path(path).read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError('input identity')
    results = [scan(data, base, a, b) for a, b in spans]
    if sum((sites for _, sites in results), []) != expected:
        raise ValueError('unexpected SYSTEM sites')
    print('PASS', [n for n, _ in results], 'SYSTEM PCs', [hex(pc) for pc, _ in expected])


if __name__ == '__main__':
    check(sys.argv[1], '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 0x8000,
          [(0x18704,0x18734),(0x1874a,0x18834)], [(0x1870c,0x3002a073),(0x1871c,0x30529073),(0x1872c,0x34129073)])
    check(sys.argv[2], '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 0x40000,
          [(0x40000,0x40004),(0x40280,0x402b0),(0x6de0c,0x6dec2)], [(0x6debe,0x30200073)])
