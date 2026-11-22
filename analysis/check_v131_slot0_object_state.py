"""V1.31 reference BIN; bounded projections, not a hardware callback binding."""
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('object state evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p,n=4):return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def field(p): # conditional Xwchc byte load/store
    x=w(p,2);return (x&0xe003,8+(x>>7&7),8+(x>>2&7),(x>>12&1)|((x>>5&3)<<1)|((x>>10&3)<<3))
ck(field(0x554c0)==(0x2000,8,15,11) and field(0x53dae)==(0xa000,10,15,11))
lo=0x53d98;h=bytes.fromhex('4111b737002022c406c69387873b238e0706930710f93cb5b737002003a4074e0dc0b737002003c5f7198545eff09ecc930710273305f50222832244b24041010283b240224441018280');ck(b[lo-0x40000:lo-0x40000+len(h)]==h)
x=w(0x53da6);fixed=(w(0x53d9a)&0xfffff000)+sx(w(0x53da2)>>20,12)+sx((x>>25<<5)|(x>>7&31),12)
state=sx(w(0x53daa)>>20,12)&255;slot=(w(0x53db0)&0xfffff000)+sx(w(0x53db4)>>20,12);task=(w(0x53dba)&0xfffff000)+sx(w(0x53dbe)>>20,12)
ck((fixed,state,slot,task)==(0x20003434,145,0x200034e0,0x2000319f));ck(slot==0x200033b8+296)
x=w(0x53dc4);d=(x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;ck(x&4095==0xef and 0x53dc4+sx(d,21)==0x43a8c)
# Same object on a later visit, no other writer. Check the default state's index.
for previous in range(256):
    obj=bytearray(12);obj[11]=previous;obj[field(0x53dae)[3]]=state
    ck(((obj[field(0x554c0)[3]]+110)&255)==255)
# The saved target, not the return from the helper, determines the tail destination.
for rv in (0,1,0xffff,0x1000000,0xffffffff):
    val=(rv*(w(0x53dc8)>>20))&0xffffffff;ck(val==(625*rv)%2**32)
print('PASS: 256 object-state replacements -> default index 255; null-return and nonnull call/tail bytes pinned; 5 RV32 product checks')
