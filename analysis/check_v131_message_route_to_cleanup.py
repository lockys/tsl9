"""Args: V1.31 main segment. Trace from dequeue return, not through dequeue or callbacks."""
import sys
from hashlib import sha256
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x:raise ValueError('message route mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def route(m,p):
    pc=0x4dc18;r={10:p};reads=[]
    for _ in range(11):
        if pc in (0x4dc6c,0x4dc66,0x4dc2e,0x4e1ae):return pc,reads,r
        i=pc-0x40000;h=int.from_bytes(b[i:i+2],'little');at=pc;pc+=2
        if h==0x842a:r[8]=r[10]
        elif h==0xc929:
            off=((h>>12&1)<<8)|((h>>5&3)<<6)|((h>>2&1)<<5)|((h>>10&3)<<3)|((h>>3&3)<<1)
            if r[8+(h>>7&7)]==0:pc=at+sx(off,9)
        elif h&0xe003==0x2000: # QK.C.LBU
            addr=r[8+(h>>7&7)]+((h>>12&1)+8*(h>>10&3)+2*(h>>5&3));reads.append(addr);r[8+(h>>2&7)]=m[addr]
        elif h==0x47cd:r[15]=19
        elif h&3==3:
            w=int.from_bytes(b[i:i+4],'little');pc+=2
            if w&0xfffff==0x793:r[15]=sx(w>>20,12) # ADDI a5,x0,imm
            elif w&0x707f==0x1063:
                off=(w>>31<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
                if r[w>>15&31]!=r[w>>20&31]:pc=at+sx(off,13)
            else:raise ValueError(hex(at))
        elif h&0xe003==0x2001: # RV32 C.JAL
            off=(h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5
            r[1]=pc;pc=at+sx(off,12)
        else:raise ValueError(hex(at))
    raise ValueError('step limit')
ck(route({},0)[:2]==(0x4dc6c,[]));p=0x20005700;counts={}
for a in range(256):
    for c in range(256):
        pc,reads,r=route({p:a,p+1:c},p);exp=0x4dc66 if a!=144 else 0x4dc2e if c==19 else 0x4e1ae
        ck(pc==exp and reads==([p] if a!=144 else [p,p+1]) and r[8]==p)
        if pc==0x4e1ae:ck(r[1]==0x4dc9e and r[10]==p)
        counts[pc]=counts.get(pc,0)+1
ck(counts=={0x4dc66:65280,0x4dc2e:1,0x4e1ae:255})
print('PASS: null/no read; 65280 bypass, 1 separate update path, 255 cleanup-parser calls; no store in traced prefix')
