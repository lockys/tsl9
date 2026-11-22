"""V1.31 static slices only. Assumes Xwchc, same queue layout, normal calls.
Not a scheduler, a heap implementation, or evidence of a particular radio transfer.
Usage: python check_v131_cmd6_queue_pop.py REFERENCE.bin
"""
from pathlib import Path
from hashlib import sha256
import sys
rom=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('unexpected queue slice')
ck(sha256(rom).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n):return rom[p-0x40000:p-0x40000+n]
def u(p,n):return int.from_bytes(raw(p,n),'little')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def byteop(p,op):
    h=u(p,2);ck(h&3==0 and h>>13==op)
    return 8+(h>>7&7),8+(h>>2&7),(h>>12&1)|(h>>10&3)<<3|(h>>5&3)<<1
def branch(p):
    h=u(p,2);ck(h&3==1 and h>>13 in (6,7))
    off=(h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1
    return 8+(h>>7&7),h>>13==7,p+sx(off,9)
def target(p):
    a=u(p,4);j=u(p+4,4);ck(a&4095==0x97 and j&0xfffff==0x80e7)
    return (p+(a&0xfffff000)+sx(j>>20,12))&0xfffffffe
# Producer places low byte of -127 into node+9, then stores adjusted buffer pointer at +4.
ck(u(0x6a6a0,4)==0xf8100793 and byteop(0x6a6ae,5)==(10,15,9) and u(0x6a6b4,2)==0xc144)
for head,gate,call,pop,skip in [(0x59806,0x5980e,0x59824,0x59836,0x5984c),(0x615e6,0x615ea,0x61600,0x61612,0x6161c)]:
    ck(u(head,4)==0x11842783 and branch(gate)==(15,False,skip))
    ck(byteop(gate+2,1)==(8,14,27) and branch(gate+4)==(14,False,skip))
    ck(byteop(gate+6,1)==(15,14,9) and u(gate+8,2)==0x8b05 and branch(gate+10)==(14,True,skip))
    ck(u(call-8,2)==0x43c8 and target(call)==0x20000110)
    ck(raw(pop,10).hex()=='832784119c43232cf410') # reread head, load next, store at +280
# Third site traverses without those byte gates; skips release for a null payload.
ck(u(0x57756,4)==0x11842783 and branch(0x5775a)==(15,True,0x5780a))
ck(u(0x5780a,2)==0x43c8 and branch(0x5780c)==(10,False,0x57816) and target(0x5780e)==0x20000110)
ck(u(0x57816,4)==0x11842783 and raw(0x57822,6).hex()=='9c43232cf410')
print('PASS: 3 head advances, 3 calls targeting 0x20000110; both conditional consumers skip newly initialized node flag 0x81')
