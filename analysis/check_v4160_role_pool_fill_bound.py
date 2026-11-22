"""Conditional role fill bound, not a heap-list integrity proof. Args: decoded APP, V1.31 carrier."""
from hashlib import sha256
from pathlib import Path
import sys

def ck(ok):
    if not ok:raise ValueError('pool or fill evidence mismatch')

def bound(app,ref):
    pc=0x19a3a;cfg=app[pc-0x8000:pc-0x8000+16]
    ck(cfg==bytes.fromhex('97a7fe1f938727753ec89d67231af100'))
    u=int.from_bytes(cfg[:4],'little');k=int.from_bytes(cfg[4:8],'little',signed=True)>>20
    lo=(pc+(u&0xfffff000)+k)&0xffffffff
    size=((int.from_bytes(cfg[10:12],'little')>>2)&31)<<12
    end=lo+size;ck((lo,size,end)==(0x2000418c,0x7000,0x2000b18c))
    def ram(pc,n):i=pc-0x20000000+0x270;return ref[i:i+n]
    ck(ram(0x200000f4,2)==bytes.fromhex('2105')) # success: a0 = header + 8
    ck(ram(0x2000010c,4)==bytes.fromhex('0841bdbf')) # occupied/too small: follow next pointer, not arena arithmetic
    ck(ram(0x200003ac,24)==bytes.fromhex('01c53307c50011e6374702402326f72082800505a30fb5fe'))
    ck(ram(0x200003c4,6)==bytes.fromhex('e31de5fef5b7'))
    ck(ref[0xee10:0xee20]==bytes.fromhex('10249307c00381453306f60223aaa434'))
    target=0x20003350; maxlen=60*255
    for h in range(lo,end-7): # all 8-byte header placements, even unaligned; not all are realizable
        p=h+8
        ck(p>=target+2 and p+maxlen<1<<32)
    ck(all(0<=60*n<=maxlen for n in range(256)))
    # Also verify the interval predicate on adjacent half-open boundaries.
    def hit(p,n):return n>0 and p<target+2 and target<p+n
    ck(not hit(target-60,60) and hit(target-59,60) and hit(target+1,60) and not hit(target+2,60))
    print(f'PASS: pool [{lo:#x},{end:#x}); {size-7} header placements x 256 fill counts bounded; min P={lo+8:#x}, max length={maxlen}; null bypasses data loop')

if __name__=='__main__':
    a,b=(Path(s).read_bytes() for s in sys.argv[1:]);ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22']);bound(a,b)
