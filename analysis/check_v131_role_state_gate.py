"""Check selected V1.31 gate fields, not a device execution."""
from hashlib import sha256
from pathlib import Path
import sys


def fields(b):
    def word(pc, n=4):
        return int.from_bytes(b[pc-0x40000:pc-0x40000+n], 'little')
    def need(ok, pc):
        if not ok: raise ValueError(hex(pc))
    for pc, opcode, base, reg in [(0x642ea,5,15,14),(0x641bc,1,8,14),(0x641d0,1,8,14),(0x63f0a,1,15,15)]:
        h = word(pc,2)
        off = (h>>12&1) + 2*(h>>5&3) + 8*(h>>10&3)
        need((h&3,h>>13,8+(h>>7&7),8+(h>>2&7),off)==(0,opcode,base,reg,7),pc)
    for pc in (0x642e4,0x641b8,0x63f06):
        need(word(pc)>>20 == 1300,pc)
    for pc, raw in [(0x642e8,0x4705),(0x63efe,0x8b8d),(0x63f00,0xcbb9),(0x63f0c,0x470d),(0x63f26,0x9782),(0x63eb6,0xcb99)]:
        need(word(pc,2)==raw,pc)
    w = word(0x63f14)
    imm = (w>>31<<12) | (w>>7&1)<<11 | (w>>25&63)<<5 | (w>>8&15)<<1
    need((w&0x707f,w>>15&31,w>>20&31,0x63f14+(imm^4096)-4096)==(0x1063,14,15,0x63f28),0x63f14)
    need(word(0x642a4)==0x5007a623 and word(0x63eb2)==0x50c7a783,0x642a4)


def check(b):
    if sha256(b).hexdigest() != '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22': raise ValueError('reference identity')
    fields(b)
    bad = bytearray(b); bad[0x63f0c-0x40000] ^= 8  # li a4,3 -> li a4,1
    try: fields(bad)
    except ValueError as e:
        if str(e) != '0x63f0c': raise
    else: raise ValueError('accepted changed comparison')
    print('PASS: shared +7 field; init=1 vs callback gate=3; descriptor clear/load; comparison mutation rejected')


if __name__ == '__main__': check(Path(sys.argv[1]).read_bytes())
