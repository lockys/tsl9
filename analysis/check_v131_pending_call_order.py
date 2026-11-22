"""Offline V1.31 retry caller: immediate-edge census and synthetic helper results."""
from pathlib import Path
from hashlib import sha256
from itertools import product
import sys
b=Path(sys.argv[1]).read_bytes(); base=0x40000

def ck(x):
    if not x: raise ValueError('retry caller mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
def word(pc): return int.from_bytes(b[pc-base:pc-base+4],'little')
def edge(pc,w):
    h=w&65535
    if w&127==111: return pc+sx((w>>31<<20)|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1,21)
    if h&0xe003 in (0x2001,0xa001):
        return pc+sx((h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5,12)
hits={0x4e7b2:[],0x4e9ca:[]}
for pc in range(base,base+len(b)-1,2):
    w=word(pc); dest=edge(pc,w)
    if dest in hits: hits[dest].append(pc); ck(w&4095==0xef)
ck(hits=={0x4e7b2:[0x4e9d0,0x4e9e0,0x4e9e8,0x4e9f0],0x4e9ca:[0x4dca8]})
def run(results,flag):
    pc=0x4e9ca;r=[0]*32;calls=[];reads=[]
    for _ in range(32):
        at=pc;w=word(pc);h=w&65535;pc+=4 if h&3==3 else 2
        if h in (0x1141,0xc606,0x40b2,0x0141): continue # assume distinct valid frame, normal returns
        if h==0x8082:return calls,reads,r[10]
        if h&0xe003==0x4001:r[h>>7&31]=sx((h>>12&1)<<5|(h>>2&31),6)
        elif w&4095==0xef:
            ck(edge(at,w)==0x4e7b2); calls.append(r[10]);r[10]=results[r[10]]
        elif h&0xe003 in (0xc001,0xe001):
            off=(h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1
            if bool(r[8+(h>>7&7)])==bool(h&0x2000):pc=at+sx(off,9)
        elif w&127==55:r[w>>7&31]=w&0xfffff000
        elif w&0x707f==0x4003:reads.append(r[w>>15&31]+sx(w>>20,12));r[w>>7&31]=flag
        elif w&4095==111:return calls,reads,('tail',edge(at,w))
        else:raise ValueError(hex(at))
    raise ValueError('step bound')
order=[5,6,4,7]
for vals in product((0,1),repeat=4):
    for f in (0,1,255):
        expected=(order[:vals.index(1)+1],[],1) if any(vals) else (order,[0x20002fa1],('tail',0x4e902) if f else 0)
        ck(run(dict(zip(order,vals)),f)==expected)
print('PASS: four immediate calls in priority order 5,6,4,7; one immediate caller of wrapper; 48 short-circuit/fallback traces')
