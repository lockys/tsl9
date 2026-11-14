"""Bounded static proof of two public WCH resident comparison candidates.

These are candidate carriers, not a dump of the TSL9 installed resident ROM.
The Xwchc halfword is checked as bytes, not executed or validated against a
hardware ISA. Branch decoder covers only the six recorded branch instructions.
"""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RAM=0x20000442
RAW=bytes.fromhex('b747024003a7c72023a607200f10000001c599c1814711eab747024023a6e720054582808507e309f6fe3308f500b386f500034808009422e306d8feb747024023a6e72001458280')
SLICE_SHA='a9dbd2b47ccefe55ab45f0b4e5a073d7aeb00f42dbe503191a75b6b66efff3aa'
CARRIERS=(('analysis/wch-resident-candidate-2026-10-21/carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EC56.bin',191574,'b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941',0x6f2),('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin',191078,'133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22',0x6b2))
# offset, encoded length, raw instruction bytes; separate from decoder and slice hash.
LEDGER=((0,4,'b7470240'),(4,4,'03a7c720'),(8,4,'23a60720'),(12,4,'0f100000'),(16,2,'01c5'),(18,2,'99c1'),(20,2,'8147'),(22,2,'11ea'),(24,4,'b7470240'),(28,4,'23a6e720'),(32,2,'0545'),(34,2,'8280'),(36,2,'8507'),(38,4,'e309f6fe'),(42,4,'3308f500'),(46,4,'b386f500'),(50,4,'03480800'),(54,2,'9422'),(56,4,'e306d8fe'),(60,4,'b7470240'),(64,4,'23a6e720'),(68,2,'0145'),(70,2,'8280'))

def sx(x,n): return x-(1<<n) if x&(1<<(n-1)) else x

def branch(code,offset):
    h=int.from_bytes(code[offset:offset+2],'little'); pc=RAM+offset
    if h&3!=3:
        funct=h>>13
        if h&3!=1 or funct not in (6,7): raise ValueError('not compressed branch')
        imm=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
        return ('beq' if funct==6 else 'bne',8+(h>>7&7),0,pc+sx(imm,9))
    word=int.from_bytes(code[offset:offset+4],'little')
    if word&0x7f!=0x63 or (word>>12&7) not in (0,1): raise ValueError('not branch')
    imm=((word>>31&1)<<12)|((word>>7&1)<<11)|((word>>25&63)<<5)|((word>>8&15)<<1)
    return ('beq' if (word>>12&7)==0 else 'bne',(word>>15)&31,(word>>20)&31,pc+sx(imm,13))

BRANCHES={16:('beq',10,0,RAM+24),18:('beq',11,0,RAM+24),22:('bne',12,0,RAM+42),38:('beq',12,15,RAM+24),56:('beq',16,13,RAM+36)}

def verify(code):
    if len(code)!=72: raise ValueError('slice size')
    for offset,expected in BRANCHES.items():
        if branch(code,offset)!=expected: raise ValueError(f'branch mismatch at {offset}')
    cursor=0
    for offset,size,raw in LEDGER:
        if offset!=cursor or code[offset:offset+size]!=bytes.fromhex(raw): raise ValueError(f'ledger mismatch at {offset}')
        cursor+=size
    if cursor!=len(code): raise ValueError('ledger coverage')


def main():
    if hashlib.sha256(RAW).hexdigest()!=SLICE_SHA: raise ValueError('reference hash')
    verify(RAW)
    for path,size,sha,offset in CARRIERS:
        if not (ROOT/path).is_file():
            print(f'SKIP: optional local candidate carrier not available: {path}')
            continue
        data=(ROOT/path).read_bytes()
        if len(data)!=size or hashlib.sha256(data).hexdigest()!=sha: raise ValueError(f'carrier mismatch: {path}')
        chunk=data[offset:offset+72]
        if hashlib.sha256(chunk).hexdigest()!=SLICE_SHA or chunk!=RAW: raise ValueError(f'slice mismatch: {path}')
        verify(chunk)
        print(f'PASS: {path}, offset {offset:#x}, identical 72-byte candidate')
    for offset,_,_ in LEDGER:
        bad=bytearray(RAW); bad[offset]^=1
        try: verify(bad)
        except ValueError: pass
        else: raise ValueError(f'mutation missed {offset}')
    for offset in BRANCHES:
        for bit in (2,7,10):
            bad=bytearray(RAW); bad[offset+bit//8]^=1<<(bit%8)
            try: verify(bad)
            except ValueError: pass
            else: raise ValueError(f'branch mutation missed {offset}/{bit}')
    print(f'PASS: {len(LEDGER)} contiguous instructions; {len(BRANCHES)} decoded branch targets; all mutations rejected')
    print('Candidate carrier bytes only: Xwchc, installed ROM, ABI, concurrency and hardware not proved.')

if __name__=='__main__': main()
