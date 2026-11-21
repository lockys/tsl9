"""Bounded address proof for a successful in-arena allocation, not a heap integrity test."""
from hashlib import sha256
from pathlib import Path
import sys


def need(ok, why):
    if not ok:
        raise ValueError(why)


def check(b):
    need(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'carrier')
    # File offsets. Relocated low RAM code at offset 0x270 + RAM offset.
    for i,h in [(0x3140,'3307d600373500202328e51823a0e522'),(0x314,'3737002003250719e1bf'),(0x37c,'0841bdbf'),(0x364,'2105'),(0xee10,'10249307c00381453306f60223aaa4349710fb1fe780c05783a744351424014789077d566341d702'),(0xee56,'92a32381070023a5070205079387c703f9b7')]:
        need(b[i:i+len(bytes.fromhex(h))]==bytes.fromhex(h),hex(i))
    # Nominal APP base/length from the arena-init report, not measured RAM.
    base,length=0x2000418c,0x7000
    first,stop=base+544,base+length-8
    count=0x20003350
    need((first,stop)==(0x200043ac,0x2000b184),'arena')
    # Deliberately overapproximate: even allow P=stop as inclusive upper bound.
    lo,hi=first+8,stop
    need(count<lo and hi+60*255 < 2**32,'ordered range, no RV32 wrap')
    for n in range(256):
        # Two independent fresh unsigned-byte reads: apply each bound separately.
        size=60*n
        need(hi+size<=2**32 and count<lo,'fill')
        if n:
            # cursor=P+2+60*i; SH cursor+0; SB cursor+2; SW cursor+42
            for off,width in ((2,2),(4,1),(44,4)):
                need(count<lo+off and hi+60*(n-1)+off+width<=hi+size,'records')
    for c in range(256):
        k=(c&3)+(c>>2)
        need(k<=66 and (not k or 52<60*k<=3960),'original request')
    print('PASS: 256 request inputs; independent 0..255 fill and record counts; in-arena payload writes exclude 0x20003350')


if __name__=='__main__':
    check(Path(sys.argv[1]).read_bytes())
