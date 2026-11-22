"""Command 6 response owner's return paths; synthetic normal helper returns, not a heap replay."""
import sys
from hashlib import sha256
from pathlib import Path

rom = Path(sys.argv[1]).read_bytes()
def check(ok):
    if not ok: raise ValueError('unexpected response-owner trace')
check(sha256(rom).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def sx(v,n): return (v^(1<<(n-1)))-(1<<(n-1))
def word(pc): return int.from_bytes(rom[pc-0x40000:pc-0x40000+4], 'little')
def walk(pc, flag, status, d):
    r=[0]*32; r[8]=d; r[15]=flag; r[10]=0; calls=[]
    for _ in range(28):
        w=word(pc); h=w&65535; at=pc; pc+=4 if h&3==3 else 2
        if h==0x8082: return r[10], calls
        if h in (0x50f2,0x5462,0x5942,0x54d2,0x59b2,0x6121): continue # frame restore; saved s1 reload is after result move
        if h in (0x84aa,0x8522,0x8526): r[h>>7&31]=r[h>>2&31]
        elif h==0x44cd: r[9]=19
        elif h&0xe003==0xc001:
            off=(h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1
            if not r[8+(h>>7&7)]: pc=at+sx(off,9)
        elif h&0xe003==0xa001:
            off=(h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5
            pc=at+sx(off,12)
        elif w&4095==0xef:
            off=(w>>31<<20)|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1
            calls.append((at+sx(off,21),None)); r[10]=status
        elif w&4095==0x97:
            j=word(pc); check(j&0xfffff==0x80e7); pc+=4
            calls.append(((at+(w&0xfffff000)+sx(j>>20,12))&0xfffffffe,r[10])); r[10]=0xabcdef01
        else: raise ValueError(hex(at))
    raise ValueError('step bound')
check(word(0x4eaae)&65535==0x842a) # s0=D at successful allocation
for flag in (0,1):
    for status in range(256):
        d=0x2000480e
        expected=[(0x4e6ca if flag else 0x4e4cc,None)]+([(0x20000110,d)] if status else [])
        check(walk(0x4eae4,flag,status,d)==(status,expected))
check(walk(0x4eaaa,0,0,0)==(19,[]))
print('PASS: 512 post-dispatch paths and 1 null allocation; nonzero status releases saved D once here and survives release return')
