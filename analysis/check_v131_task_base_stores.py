"""Bounded literal-base store census; input files: decoded APP and V1.31 main segment."""
from hashlib import sha256
from pathlib import Path
import sys

TARGET = 0x200031c4


def ck(v):
    if not v: raise ValueError('task-base census mismatch')


def scan(b, va):
    hits = set()
    for i in range(0, len(b)-5, 2):
        u = int.from_bytes(b[i:i+4], 'little'); r = u >> 7 & 31
        if (u & 127) != 55 or not r or u & 0xfffff000 != 0x20003000: continue
        p = i+4
        for _ in range(16):
            w = int.from_bytes(b[p:p+4], 'little'); h = w & 65535
            n = 4 if h & 3 == 3 else 2
            if p+n > len(b): break
            if n == 4 and w & 127 == 35 and (w>>12&7) <= 2:
                disp = (w>>25<<5) | (w>>7&31); disp = (disp^2048)-2048
                a = 0x20003000 + disp; size = 1 << (w>>12&7)
                if w>>15&31 == r and a < TARGET+4 and a+size > TARGET:
                    hits.add((hex(va+i),hex(va+p),hex(a),size))
            elif n == 4 and (w&127) in (3,19,23,51,55):
                if w>>7&31 == r: break
            elif n == 2 and (h&0xe003) == 2 and (h>>7&31) not in (0,r): pass  # C.SLLI
            else: break
            p += n
    return sorted(hits)


if __name__ == '__main__':
    a,b=(Path(s).read_bytes() for s in sys.argv[1:])
    ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
    match=[('0x43be8','0x43bf2','0x200031c4',4)]
    code=b[0x3be8:0x3bf6]; ck(scan(code,0x43be8)==match)
    for replacement in [bytes.fromhex('93040400'),bytes.fromhex('63000000')]:
        ck(not scan(code[:4]+replacement+code[8:],0x43be8))  # clobber s1 / branch
    for label,base,data in [('APP',0x8000,a),('ROM',0x40000,b),('RAM copy',0x20000000,b[0x270:0x2b0+2957*4])]:
        hits=scan(data,base); ck(hits==(match if label=='ROM' else [])); print(label,hits)
