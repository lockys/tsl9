"""Check the first config-copy arguments and the four-byte guard in the APP."""
from hashlib import sha256
from pathlib import Path
import sys


def run(b):
    if sha256(b).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('APP identity')
    def word(pc):
        return int.from_bytes(b[pc-0x8000:pc-0x8000+4], 'little')
    def pair(pc, reg, relative):
        h, l = word(pc), word(pc+4)
        if h & 4095 != (reg<<7 | (0x17 if relative else 0x37)) or l & 0xfffff != (reg<<15 | reg<<7 | 0x13):
            raise ValueError('address pair')
        return ((pc if relative else 0)+(h & 0xfffff000)+(l>>20)-(4096 if l>>31 else 0)) & 0xffffffff
    dest, first, end = [pair(pc,r,True) for pc,r in ((0x131d8,10),(0x131e2,14),(0x131ea,13))]
    if (dest,first,end)!=(0x2000c29c,0x2000c29c,0x2000c2a0) or word(0x131ce)!=0x07000613:
        raise ValueError('copy or scan range')
    def raw(pc, text):
        x=bytes.fromhex(text)
        if b[pc-0x8000:pc-0x8000+len(x)]!=x: raise ValueError(hex(pc))
    raw(0x131f2,'1306e0058347c700811793f7f70f637ef60e'); raw(0x132fc,'0507e39ce6ee19b7')
    tests=0
    for pos in range(end-first):
        for byte in range(256):
            data=[32]*4; data[pos]=byte
            bad=next((i for i,x in enumerate(data) if ((x-32)&255)>94),None)
            if bad!=(None if 32<=byte<=126 else pos): raise ValueError('guard')
            tests+=1
    print(f'PASS dst={dest:#x} length=112 guard=+12..+15 cases={tests}')

if __name__=='__main__': run(Path(sys.argv[1]).read_bytes())
