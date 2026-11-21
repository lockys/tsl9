"""Offline encoding census, not a whole-program points-to analysis."""
from pathlib import Path
import hashlib
import sys

GP = 0x20004000
BASE = 0x8000


def signed12(n):
    return (n ^ 2048) - 2048


def census(data):
    hits, refs = [], []
    for i in range(0,len(data)-3,2):
        w = int.from_bytes(data[i:i+4],'little')
        op, rd, rs, f = w&127, (w>>7)&31, (w>>15)&31, (w>>12)&7
        if op == 0x13 and rs == 3 and f == 0 and rd and w>>20 in (96,100,104):
            refs.append(BASE+i)
        if op != 0x23 or f > 2: continue
        off = signed12((w>>25)<<5 | rd)
        if rs == 3:
            addr = GP+off
        elif i >= 4 and rs:
            hi = int.from_bytes(data[i-4:i],'little')
            if (hi>>7)&31 != rs or hi&127 not in (0x17,0x37): continue
            addr = (hi&0xfffff000) + (BASE+i-4 if hi&127 == 0x17 else 0) + off
        else: continue
        if any(GP+96 <= (addr+j)&0xffffffff < GP+108 for j in range(1<<f)):
            hits.append(BASE+i)
    return hits, refs


def controls():
    def sw(base,off,f):
        return ((off&0xfe0)<<20 | base<<15 | f<<12 | (off&31)<<7 | 0x23).to_bytes(4,'little')
    for f in range(3):
        for off in range(90,112):
            if bool(census(sw(3,off,f))[0]) != (off<108 and off+(1<<f)>96):
                raise ValueError('overlap boundary')
    for op,hi in ((0x37,GP),(0x17,GP-BASE)):
        pair = (hi|5<<7|op).to_bytes(4,'little')
        if census(pair+sw(5,100,2))[0] != [BASE+4] or census(pair+sw(6,100,2))[0]:
            raise ValueError('producer register')


if __name__ == '__main__':
    controls()
    b = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(b).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('unexpected APP')
    h,r = census(b)
    print('windows:',(len(b)-2)//2,'store hits:',[hex(pc) for pc in h],'slot ADDI:',[hex(pc) for pc in r])
