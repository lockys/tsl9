"""Scan allowed APP windows for possible direct RV32/RVC transfers into TX."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[2]
paths=(
 root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
 root/'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin')
regions=((0x8000,0x8a56),(0x8b6e,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,0x1ac00))
def signed(x,n): return x-(1<<n) if x&(1<<(n-1)) else x
def candidates(data,base):
    for off in range(0,len(data)-1,2):
        pc=base+off;h=int.from_bytes(data[off:off+2],'little')
        if h&3!=3:
            f=h>>13
            if h&3!=1: continue
            if f in (1,5):
                v=((h>>12)&1)<<11|((h>>11)&1)<<4|((h>>9)&3)<<8|((h>>8)&1)<<10|((h>>7)&1)<<6|((h>>6)&1)<<7|((h>>3)&7)<<1|((h>>2)&1)<<5
                yield pc,pc+signed(v,12),'cj'
            elif f in (6,7):
                v=((h>>12)&1)<<8|((h>>10)&3)<<3|((h>>5)&3)<<6|((h>>3)&3)<<1|((h>>2)&1)<<5
                yield pc,pc+signed(v,9),'cb'
        elif off+4<=len(data):
            w=int.from_bytes(data[off:off+4],'little');op=w&127
            if op==0x63:
                v=((w>>31)&1)<<12|((w>>7)&1)<<11|((w>>25)&63)<<5|((w>>8)&15)<<1
                yield pc,pc+signed(v,13),'b'
            elif op==0x6f:
                v=((w>>31)&1)<<20|((w>>12)&255)<<12|((w>>20)&1)<<11|((w>>21)&1023)<<1
                yield pc,pc+signed(v,21),'jal'
for path in paths:
    if path.stat().st_size!=76800: raise ValueError('unexpected image size')
    hits=[]
    with path.open('rb') as f:
        for lo,hi in regions:
            f.seek(lo-0x8000);data=f.read(hi-lo)
            if len(data)!=hi-lo: raise ValueError('short range')
            hits.extend((hex(pc),hex(dest),kind) for pc,dest,kind in candidates(data,lo) if 0x8a56<=dest<0x8b6e)
    expected=[('0x8368','0x8a56','cj'),('0x841c','0x8a56','cj'),('0x9be0','0x8a56','jal'),('0x135a8','0x8a56','jal'),('0x13b30','0x8a56','jal'),('0x13b80','0x8a56','jal'),('0x13c2e','0x8a56','jal'),('0x13eac','0x8a56','jal')]
    if hits!=expected: raise ValueError('direct-transfer candidate set changed')
    print(json.dumps({'image':'candidate' if 'NOT-FLASH' in path.name else 'official','hits':hits,
                      'limitation':'every two-byte offset including data, excluding prohibited ranges and indirect targets'}))
