"""Check V1.31 type-3 workspace call sites; no device access."""
from hashlib import sha256
from pathlib import Path
import sys


def check(b):
    def need(ok, msg):
        if not ok:
            raise ValueError(msg)
    need(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'carrier identity')
    def u(pc, n):
        return int.from_bytes(b[pc-0x40000:pc-0x40000+n], 'little')
    def sx(v, bits):
        return (v ^ (1 << (bits-1))) - (1 << (bits-1))
    for pc, dst in [(0x51f92,0x20000040),(0x51fa4,0x2000039c),(0x51fb2,0x2000048a),(0x51fc2,0x2000048a),(0x51fe2,0x2000048a),(0x51fec,0x20000110),(0x638b6,0x200022be)]:
        a,j = u(pc,4),u(pc+4,4)
        need(a&4095 == 0x97 and j&0xfffff == 0x80e7 and ((pc+(a&0xfffff000)+sx(j>>20,12))&0xfffffffe) == dst, hex(pc))
    pc=0x51fd4; w=u(pc,4)
    off=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    need(w&4095 == 0xef and pc+sx(off,21)==0x63890, 'transform call')
    # Copied comparator-adjacent routine: conditional Xwchc byte load.
    h=u(0x40722,2)
    need((h>>13,h&3,8+(h>>7&7),8+(h>>2&7),((h>>12&1)|((h>>10&3)<<3)|((h>>5&3)<<1)))==(1,0,11,15,1),'lbu a5,1(a1)')
    need(u(0x40720,2)==0x15fd and u(0x40724,2)==0x0505 and u(0x40726,4)==0xfef50fa3,'reverse copy loop')
    need(u(0x52004,2)==0x44cd and u(0x638c2,2)==0x4501 and u(0x51ff8,2)==0x8526,'status literals and forwarding')
    print('PASS: 8 transfer targets; reverse byte loop; 19/0 status instructions')


if __name__ == '__main__':
    check(Path(sys.argv[1]).read_bytes())
