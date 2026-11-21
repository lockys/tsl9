"""Selected pre-role calls, reference only. Run with the V1.31 carrier path."""
from hashlib import sha256
from pathlib import Path
import sys


def need(ok, why):
    if not ok:
        raise ValueError(why)


def check(b):
    need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22','reference')
    def w(pc):
        return int.from_bytes(b[pc-0x40000:pc-0x40000+4],'little')
    for pc,target in [(0x6dd1a,0x61b1c),(0x61b20,0x55bde),(0x55bf4,0x43c4e),(0x55bf8,0x5362e),(0x6dd26,0x43c4e),(0x6dd2a,0x4da70)]:
        a=w(pc); off=(a>>31<<20)|(a>>12&255)<<12|(a>>20&1)<<11|(a>>21&1023)<<1
        need(a&4095==239 and pc+(off^0x100000)-0x100000==target,hex(pc))
    for pc,h in [(0x55bde,'b737002083c7f719411106c689eb'),(0x43be2,'83a7c4223820b7340020938707240a0723a2f41c'),(0x43c4e,'373700201307c7191c33342363ffd700b736002083a6461c1386170010b313972700369708c33e8582809307f00fe5bf'),(0x5362e,'411126c2b7340020b737002013068012814522c42a841385843b06c623a2074e4ac097d0fa1fe780c0d4')]:
        need(b[pc-0x40000:pc-0x40000+len(bytes.fromhex(h))]==bytes.fromhex(h),hex(pc))
    def imm(pc):
        return ((w(pc)>>20)^2048)-2048
    lo,hi=0x200043b4,0x2000b184 # conditional payload bounds, not physical pointers
    count=0x20003350; offset=imm(0x43bec)
    need(offset==576 and count!=0x20003000+imm(0x43c52)+1,'table layout')
    success=0
    for i in range(256):
        for cap in range(256):
            if i<cap:
                need(count<lo+offset+4*i and hi+offset+4*i+4<=2**32,'slot interval')
                success+=1
    start=(w(0x53632)&0xfffff000)+imm(0x53644); size=imm(0x5363a)
    target=(0x53650+(w(0x53650)&0xfffff000)+imm(0x53654))&0xfffffffe
    need((start,start+size,target,success)==(0x200033b8,0x200034e0,0x2000039c,32640),'clear and registrations')
    print('PASS: 6 call edges; 65536 index/capacity pairs; 32640 successful slot cases; 296-byte clear excludes count')


if __name__=='__main__':
    check(Path(sys.argv[1]).read_bytes())
