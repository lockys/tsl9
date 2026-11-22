"""Offline post-call scalar projection; input is the V1.31 reference ROM, not a device.
Start at 4e766 after a normal 534a6 return (identifier != fffe). Stop at
4e752, whose epilogue moves a5 to a0. No buffer lifetime or send is modeled.
"""
from hashlib import sha256
from pathlib import Path
import sys
rom = Path(sys.argv[1]).read_bytes()
if sha256(rom).hexdigest() != '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22':
    raise ValueError('wrong ROM')
def sx(x,n): return (x ^ (1 << (n-1))) - (1 << (n-1))
def trace(status, flag):
    pc=0x4e766; r=[0]*32; r[10]=status; events=[]
    for _ in range(20):
        if pc==0x4e752: return r[15],events
        i=pc-0x40000; w=int.from_bytes(rom[i:i+4],'little'); h=w&65535; at=pc
        pc+=4 if h&3==3 else 2
        d=h>>7&31; s=w>>15&31; t=w>>20&31; f=h>>13
        if h==0x87aa: r[15]=r[10]
        elif h&3==1 and f in (0,2): r[d]=(r[d] if f==0 else 0)+sx((h>>12&1)<<5|(h>>2&31),6)
        elif h&3==1 and f in (6,7):
            off=(h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1
            if (r[8+(h>>7&7)]!=0)==(f==7): pc=at+sx(off,9)
        elif h&3==1 and f==5:
            off=(h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5
            pc=at+sx(off,12)
        elif w&127==99 and w>>12&7 in (0,1):
            off=w>>31<<12|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1
            if (r[s]!=r[t])==bool(w>>12&1): pc=at+sx(off,13)
        elif w&127==55: r[d]=w&0xfffff000
        elif w&0x707f==0x4003:
            addr=r[s]+sx(w>>20,12); events.append(('r',addr,flag)); r[d]=flag
        elif w&0x707f==0x23:
            addr=r[s]+sx((w>>25<<5)|(w>>7&31),12); events.append(('w',addr,r[t]&255))
        else: raise ValueError(hex(at))
    raise ValueError('step bound')
if rom[0xe752:0xe75e]!=bytes.fromhex('f2406244d2443e8505618280'): raise ValueError('epilogue')
for s in (*range(256),256,0xffffffff):
    for f in range(256):
        e=[('r',0x20002fa2,f)] if s in (0,31) else []
        if e and f: e.append(('w',0x20002fa2,f-1))
        if trace(s,f)!=({31:0,2:20,7:4,18:2}.get(s,s),e): raise ValueError((s,f))
print('PASS: 66048 status/flag pairs; 0 and 31 yield 0, both decrement only a nonzero byte')
