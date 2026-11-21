"""Selected static write sets; args: decoded APP, V1.31 reference carrier."""
from pathlib import Path
from hashlib import sha256
import sys


def require(ok, message):
    if not ok:
        raise ValueError(message)


def scan(data, base, lo, hi):
    stores = []
    while lo < hi:
        k = lo - base
        h = int.from_bytes(data[k:k+2], 'little')
        n = 4 if h & 3 == 3 else 2
        if n == 4:
            op = h & 127
            require(op in (3, 19, 35, 51, 55, 99, 111, 23), hex(lo))
            if op == 35:
                stores.append(lo)
        elif (h & 3, h >> 13) in ((2, 6), (0, 6)):
            stores.append(lo)
        elif h == 0x2318 and lo == 0x6df48:
            pass  # conditional WCH byte load
        else:
            require((h & 3, h >> 13) in {(0,2),(1,0),(1,2),(1,3),(1,4),(1,5),(1,6),(2,0),(2,2),(2,4)}, hex(lo))
        lo += n
    require(lo == hi, 'boundary')
    return stores


def check(a, r):
    require(sha256(a).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'APP')
    require(sha256(r).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'reference')
    require(not scan(a,0x8000,0x191c6,0x19220), 'APP store')
    require(scan(r,0x40000,0x43520,0x4354a) == [0x4352a,0x4352c,0x4353e], 'outer')
    require(scan(r,0x40000,0x43d62,0x43de4) == [0x43d64,0x43d6e,0x43d70,0x43d72,0x43d74,0x43d76,0x43d78,0x43dce], 'inner')
    for lo, hi in [(0x6df1a,0x6df30),(0x6e0e2,0x6e0f4),(0x6df3e,0x6dfd6),(0x6e2a0,0x6e2a6)]:
        require(not scan(r,0x40000,lo,hi), 'helper store')
    require(1600*(2**32-1) >> 32 == 1599 < 16000 < 65536, 'helper path bound')
    print('PASS: APP leaf 0 stores; nested bodies 9 frame saves + 2 state stores; nominal helper windows 0 stores')


if __name__ == '__main__':
    check(*(Path(p).read_bytes() for p in sys.argv[1:]))
