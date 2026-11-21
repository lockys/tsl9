"""APP-only inventory of selected direct transfers to the receive callback."""
import hashlib
import sys
from pathlib import Path


def sx(x, bits):
    return (x ^ (1 << (bits - 1))) - (1 << (bits - 1))


def dest(pc, w):
    if w & 127 == 0x6f:
        d = ((w >> 31) << 20 | (w >> 12 & 255) << 12 | (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1)
        return pc + sx(d, 21)
    h = w & 65535
    if h & 0xe003 in (0x2001, 0xa001):
        d = ((h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 | (h >> 9 & 3) << 8 | (h >> 8 & 1) << 10 | (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 | (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5)
        return pc + sx(d, 12)
    return None


def check(ok):
    if not ok:
        raise ValueError('unexpected APP evidence')


b = Path(sys.argv[1]).read_bytes()
check(hashlib.sha256(b).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
base = 0x8000
check(b[0x19dfc-base:0x19e08-base] == bytes.fromhex('000000008c88000000000000'))
check(b[0xfb8:0xfce] == bytes.fromhex('8327041397160100938606e441469145138501008297'))
check(0x8fbc + (0x11 << 12) - 448 == 0x19dfc)
check(dest(0x8a48, 0x60e0b0ef) == 0x14056 and dest(0x8906, 0x306d) == 0x81b0)
hits = []
for off in range(0, len(b), 2):
    s = b[off:off+4]; w = int.from_bytes(s, 'little')
    if len(s) == 2 and w & 3 == 3:
        continue
    if dest(base + off, w) == 0x888c:
        hits.append(hex(base + off))
check(not hits)
print('halfword positions:', len(b)//2, 'JAL/C.J/C.JAL encodings to 0x888c:', hits)
print('APP registration passes table address; its second word is 0x888c. Registration SP is not callback SP evidence.')
