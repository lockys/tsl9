"""Offline encoding census, not a proof of all possible APP stores."""
from hashlib import sha256
from pathlib import Path
import sys

IDS = (148, 152, 166, 363)

def need(x):
    if not x: raise ValueError('unexpected instruction evidence')

def sx(x): return (x ^ 2048) - 2048

def store(w):
    if w & 127 != 35 or (k := w >> 12 & 7) > 2: return None
    return w >> 15 & 31, sx(w >> 25 << 5 | w >> 7 & 31), 1 << k

def cover(d,n): return tuple(x for x in IDS if d <= x < d+n)

def check(b):
    need(sha256(b).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    base=0x8000
    def r(p,n): return int.from_bytes(b[p-base:p-base+n], 'little')
    direct=[]; setup=[]; pairs=[]
    for p in range(base,base+len(b)-3,2):
        w=r(p,4); s=store(w)
        if s and s[0]==3 and cover(*s[1:]): direct.append((p,*s[1:]))
        if w & 0xff07f != 0x18013: continue
        d=sx(w>>20); rd=w>>7&31
        if d in IDS and rd: setup.append((p,d))
        if not rd or p+6>base+len(b): continue
        h=r(p+4,2); s=store(r(p+4,4)) if p+8<=base+len(b) else None
        if h & 0xe003 == 0xc000: s=(8+(h>>7&7),(h>>7&56)|(h>>4&4)|(h<<1&64),4)
        if s and rd==s[0] and cover(d+s[1],s[2]): pairs.append(p)
    need(direct==[(0x8f8c,148,1),(0x8fa2,152,1),(0x90a8,166,1)])
    need(setup==[(0x85f0,148),(0x86a8,148),(0x8b3a,148),(0x8be8,148),(0x8c5e,148),(0x17066,363)])
    print('direct:',direct,'exact-address ADDI:',len(setup),'adjacent store pairs:',list(map(hex,pairs)))
    for p,rs in [(0x8bf2,8),(0x8c68,15)]: need(store(r(p,4))==(rs,2,2))
    need(not any(cover(148+i*4+2,2) for i in (0,1)))
    need(store(r(0x17070,4))==(18,0,1) and r(0x171a6,4)==0x00094503)
    # Positive controls for partial overlap, negative displacement, exact end exclusion.
    need(cover(146,4)==(148,) and cover(363,1)==(363,) and not cover(360,3) and sx(4095)==-1)

if __name__=='__main__': check(Path(sys.argv[1]).read_bytes())
