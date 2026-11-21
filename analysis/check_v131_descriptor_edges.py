"""Bounded static encoding census, not an executable-code or reachability map."""
from hashlib import sha256
from pathlib import Path
import sys


def sx(x,n): return (x ^ (1 << (n-1))) - (1 << (n-1))


def edges(b,base,target):
    out=[]
    for i in range(0,len(b)-1,2):
        pc=base+i
        h=int.from_bytes(b[i:i+2],'little')
        if h&3==1 and h>>13 in (1,5):
            d=((h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|
               (h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5)
            if (pc+sx(d,12))&0xffffffff==target: out.append((hex(pc),'CJ',int(h>>13==1)))
        if i+4>len(b): continue
        w=int.from_bytes(b[i:i+4],'little'); rd=w>>7&31
        if w&127==111:
            d=w>>31<<20|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
            if (pc+sx(d,21))&0xffffffff==target: out.append((hex(pc),'JAL',rd))
        if w&127==23 and rd and i+8<=len(b):
            j=int.from_bytes(b[i+4:i+8],'little')
            if j&0x707f==0x67 and j>>15&31==rd and (pc+(w&0xfffff000)+sx(j>>20,12))&0xfffffffe==target:
                out.append((hex(pc),'AUIPC/JALR',j>>7&31))
    return out


if __name__=='__main__':
    b=Path(sys.argv[1]).read_bytes(); t=0x640b8
    if sha256(b).hexdigest()!='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22': raise ValueError('carrier identity')
    for base,code,dst,kind,link in [(0x638ae,b[0x238ae:0x238b0],0x63eda,'CJ',1),(0x51fd4,b[0x11fd4:0x11fd8],0x63890,'JAL',1),(0x638b6,b[0x238b6:0x238be],0x200022be,'AUIPC/JALR',1),(0x640b6,b[0x240b6:0x240b8],0x64030,'CJ',0)]:
        if edges(code,base,dst)!=[(hex(base),kind,link)] or edges(code,base,dst+2): raise ValueError('control at '+hex(base))
    for base,code in [(0x40000,b),(0x20000000,b[0x270:0x2b0+2957*4])]:
        print(hex(base),len(code),'bytes; candidates:',edges(code,base,t))
