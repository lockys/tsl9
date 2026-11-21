"""Compare fixed role-initializer writes with the count byte (reference only)."""
from hashlib import sha256
from pathlib import Path
import sys


def check(b):
    def need(ok, why):
        if not ok:
            raise ValueError(why)
    need(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'carrier')
    def at(pc, n):
        i = pc-0x40000 if pc < 0x20000000 else pc-0x20000000+0x270
        return b[i:i+n]
    def w(pc):
        return int.from_bytes(at(pc,4),'little')
    def imm(pc):
        return int.from_bytes(at(pc,4),'little',signed=True)>>20
    def window(pc, h):
        need(at(pc,len(bytes.fromhex(h)))==bytes.fromhex(h),hex(pc))
    window(0x4dad2,'3245b737002013060003238aa730373500201305053281459730fb1fe780208b373a002003450a35')
    window(0x4ee38,'2244b2409244373500201306000381451305853541011713fb1f6700e354')
    window(0x4ee04,'b73400209710fb1fe780802310249307c00381453306f60223aaa4349710fb1fe780c057')
    window(0x2000039c,'374702408327c720232607200f10000001c53307c50011e6374702402326f72082800505a30fb5fee31de5fef5b7')
    for pc in (0x4daea,0x4ee4e,0x4ee20):
        need((pc+(w(pc)&0xfffff000)+imm(pc+4))&0xfffffffe == 0x2000039c,'fill target')
    count = (w(0x4daf2)&0xfffff000)+imm(0x4daf6)
    fixed = []
    for upper, low, length in ((0x4dae0,0x4dae4,0x4dad8),(0x4ee3e,0x4ee48,0x4ee42)):
        base=(w(upper)&0xfffff000)+imm(low)
        fixed.append(range(base,base+imm(length)))
    sw=w(0x4ee1c)
    ptr=(w(0x4ee04)&0xfffff000)+((sw>>25)<<5)+(sw>>7&31)
    mmio=(w(0x2000039c)&0xfffff000)+imm(0x200003a0)
    need((count,ptr,mmio)==(0x20003350,0x20003354,0x4002420c),'addresses')
    need([(r.start,r.stop) for r in fixed]==[(0x20003320,0x20003350),(0x20003358,0x20003388)],'fixed ranges')
    need(all(count not in r for r in [*fixed,range(ptr,ptr+4),range(mmio,mmio+4)]),'count overlap')
    print('PASS: 3 fill targets; 2 fixed 48-byte ranges, pointer store and MMIO exclude count; dynamic destination unresolved')


if __name__=='__main__':
    check(Path(sys.argv[1]).read_bytes())
