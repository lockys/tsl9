"""V1.31 reference only. Local CFG under Xwchc; calls summarized as normal fallthrough.
Enumerates both sides of each conditional, not a proof of runtime feasibility.
"""
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('unexpected reference/control flow')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def word(p):return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def jal(w):return sx((w>>31<<20)|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1,21)
w=word(0x534a6);ck(w&4095==0x6f and 0x534a6+jal(w)==0x6a626)
paths=[]
def walk(p,seen):
    ck(0x6a626<=p<0x6a700 and p not in seen);seen=seen+(p,);w=word(p);h=w&65535;q=h&3;f=h>>13
    if h==0x8082: paths.append(seen);return
    if q==3 and w&127==99:
        off=sx(w>>31<<12|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1,13);walk(p+off,seen)
    elif q==1 and f in (6,7):
        off=sx((h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1,9);walk(p+off,seen)
    elif q==1 and f==5:
        off=sx((h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5,12);walk(p+off,seen);return
    elif q==3 and w&127==111:ck((w>>7&31)==1)
    elif q==2 and f==4 and not h&0x7c:ck(h==0x9782)
    walk(p+(4 if q==3 else 2),seen)
walk(0x6a626,())
counts={};ep=(0x6a652,0x6a654,0x6a656,0x6a658,0x6a65a,0x6a65c,0x6a65e,0x6a660)
for path in paths:
    e=path.index(ep[0]);ck(path[e:]==ep);i=e-1
    if word(path[i])&0xe003==0xa001:i-=1
    h=word(path[i])&65535;ck(h&0xef83==0x4501);ret=sx((h>>12&1)<<5|(h>>2&31),6)
    queued=0x6a6b4 in path;ck(not queued or (ret==0 and path.index(0x6a6b4)<path.index(0x6a6c6)));key=(ret,queued);counts[key]=counts.get(key,0)+1
ck(counts=={(0,False):1,(0,True):4,(7,False):4,(2,False):1});ck(word(0x6a6a4)&65535==0x14f9 and word(0x6a6b4)&65535==0xc144)
print('PASS: 10 local paths; return values 0/2/7 only; four queue paths store incoming a3 minus 2 in node+4 (assuming preserved s1)')
