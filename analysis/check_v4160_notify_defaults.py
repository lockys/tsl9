"""Replay the three straight-line post-fill APP slices, stopping before the tail wrappers."""
import hashlib
from pathlib import Path
import sys


def signed(x, n):
    return (x ^ (1 << (n-1))) - (1 << (n-1))


def replay(image, pc, end, base):
    r = [None]*32
    r[0], r[8], r[2] = 0, base, 0x1000
    page = bytearray(256)  # injected successful fill
    def access(addr, n, value=None):
        if addr in (0x1008, 0x100c) and n == 4 and value is None:
            return 0  # synthetic saved words; execution stops before tail
        i = addr-base
        if not 0 <= i <= 256-n:
            raise ValueError('outside table')
        if value is None:
            return int.from_bytes(page[i:i+n], 'little')
        page[i:i+n] = (value % (1 << (8*n))).to_bytes(n, 'little')
    while pc < end:
        pos = pc-0x8000
        w = int.from_bytes(image[pos:pos+4], 'little')
        d, a, b = (w>>7)&31, (w>>15)&31, (w>>20)&31
        if w & 3 == 3:
            op, f = w&127, (w>>12)&7
            if op == 55:
                r[d] = w & 0xfffff000
            elif op == 19 and f in (0,7):
                k = signed(w>>20,12)
                r[d] = (r[a]+k if f == 0 else r[a]&k) & 0xffffffff
            elif op == 35 and f in (0,1):
                access(r[a]+signed(((w>>25)<<5)|d,12),1<<f,r[b])
            else:
                raise ValueError(hex(pc))
            pc += 4
        else:
            h = w&65535
            d, s = 8+((h>>2)&7), 8+((h>>7)&7)
            k = signed(((h>>2)&31)|((h>>7)&32),6)
            if h&0xe003 in (0x4000,0xc000):
                addr = r[s]+((h>>10)&7)*8+((h>>6)&1)*4+((h>>5)&1)*64
                if h&0x8000: access(addr,4,r[d])
                else: r[d] = access(addr,4)
            elif h&0xec03 == 0x8801: r[s] &= k
            elif h&0xfc63 == 0x8c41: r[s] |= r[d]
            elif h&0xfc63 == 0x8c61: r[s] &= r[d]
            elif h&0xe003 == 1: r[(h>>7)&31] = (r[(h>>7)&31]+k)&0xffffffff
            elif h&0xe003 == 0x6001 and ((h>>7)&31)!=2: r[(h>>7)&31] = (k<<12)&0xffffffff
            elif h&0xe003 == 0x4001: r[(h>>7)&31] = k & 0xffffffff
            elif h&0xe003 == 0x4002:
                r[(h>>7)&31] = access(r[2]+((h>>2)&3)*64+((h>>4)&7)*4+((h>>12)&1)*32,4)
            elif h==0x0141: r[2]+=16
            else: raise ValueError(hex(pc))
            pc += 2
    if pc != end or page[255] != 90: raise ValueError('end or marker')
    return page


def main():
    image = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(image).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('wrong APP')
    for t,(start,end,base) in enumerate(((0x12ea4,0x12ee2,0x2000c494),(0x12f98,0x1304e,0x2000c594),(0x130a2,0x130d2,0x2000c694))):
        p = replay(image,start,end,base)
        keys = list(p[:254:2]) if not t else [p[i]|((p[i+1]&1)<<8) for i in range(7,252,7) if p[i+1]&2]
        hits = [keys.count(n) for n in (111,112,113)]
        print(f'table {t}: hits {hits}')
        if any(hits): raise ValueError('unexpected default match')


if __name__ == '__main__': main()
