"""Check selected V1.31 post-clear calls. No device or MMIO execution."""
from hashlib import sha256
from pathlib import Path
import sys


def need(ok,label):
    if not ok:
        raise ValueError(label)


def check(b):
    need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22','reference')
    def w(pc):
        return int.from_bytes(b[pc-0x40000:pc-0x40000+4],'little')
    for pc,dst,rd in [(0x5365a,0x55bd4,1),(0x53660,0x55c48,1),(0x536fe,0x43e24,1),(0x537b2,0x64298,1),(0x537b6,0x57ac4,1),(0x537ba,0x63704,1),(0x537c8,0x5e758,0),(0x5e768,0x53868,0)]:
        a=w(pc); off=(a>>31<<20)|(a>>12&255)<<12|(a>>20&1)<<11|(a>>21&1023)<<1
        need(a&4095==rd*128+111 and pc+(off^0x100000)-0x100000==dst,hex(pc))
    for pc,h in [(0x55bd4,'b737002023a0a74e8280'),(0x55c48,'b737002023a4a74e8280'),(0x43e24,'b737002083d7e72351471d45637cf702794719456378f7021307200315456373f7021307b0041145637ef700130740060d456379f7001307600909456374f70013b5b70f8280'),(0x57ac4,'3735002071468145130545451793fa1f6700c38c'),(0x63704,'b73700209387873b23a2070c2380070c8280'),(0x5e758,'b73700209387873b2384070c23a6070c6f500f90')]:
        need(b[pc-0x40000:pc-0x40000+len(bytes.fromhex(h))]==bytes.fromhex(h),hex(pc))
    def simm(pc):
        return ((w(pc)>>20)^2048)-2048
    stores=[]
    for pc,base in [(0x55bd8,0x20003000),(0x55c4c,0x20003000),(0x6370c,0x200033b8),(0x63710,0x200033b8),(0x5e760,0x200033b8),(0x5e764,0x200033b8)]:
        a=w(pc); stores.append((base+((a>>25)<<5)+(a>>7&31),1<<(a>>12&7)))
    need(stores==[(0x200034e0,4),(0x200034e8,4),(0x2000347c,4),(0x20003478,1),(0x20003480,1),(0x20003484,4)],'store destinations')
    start=(w(0x57ac4)&0xfffff000)+simm(0x57acc); size=(w(0x57ac8)>>2)&31
    target=(0x57ad0+(w(0x57ad0)&0xfffff000)+simm(0x57ad4))&0xfffffffe
    need((start,size,target)==(0x20003454,28,0x2000039c),'fill')
    need(all(0x20003350 not in range(p,p+n) for p,n in stores+[(start,size)]),'overlap')
    print('PASS: 8 call/tail edges, 6 code windows, 6 direct store ranges, 28-byte fill; classifier has no store')


if __name__=='__main__':
    check(Path(sys.argv[1]).read_bytes())
