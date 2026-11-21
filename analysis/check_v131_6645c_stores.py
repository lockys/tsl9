"""Audit store encodings in two V1.31 slices (explicit Xwchc profile)."""
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path


def audit(b):
    def need(ok, label):
        if not ok: raise ValueError(label)
    need(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'identity')
    def w(pc): return int.from_bytes(b[pc-0x40000:pc-0x40000+4], 'little')
    calls = []
    for pc in (0x664f8,0x6653a,0x66586):
        u,i = w(pc),w(pc+4)
        need(u&4095 == 0x97 and i&0xfffff == 0x80e7, 'call form')
        calls.append((pc+(u&~4095)+((i>>20 ^ 2048)-2048)) & 0xfffffffe)
    need(calls == [0x20002df2]*3, 'targets')
    for pc, base, off in [(0x66552,13,1429),(0x66564,13,1420),(0x6659a,19,1428),(0x665ac,14,1412),(0x67190,13,1416)]:
        v=w(pc); need((v&0x707f,v>>15&31,(v>>25)*32+(v>>7&31)) == (0x2023 if pc==0x67190 else 0x23,base,off),'store')
    need(w(0x6650e)&65535 == 0xa098 and w(0x6651a)&65535 == 0xa298,'byte stores')
    pc=0x665b0; stores=Counter()
    while pc<0x67190:
        v=w(pc); q=v&3; f=v>>13&7
        if q==3:
            op=v&127
            need(op in (3,0x13,0x33,0x37,0x23),hex(pc))
            if op==0x23:
                need(v>>12&7==2,'width'); stores[v>>15&31,(v>>25)*32+(v>>7&31)]+=1
            pc+=4
        else:
            if q==0 and f==6: stores[8+(v>>7&7),((v>>10&7)<<3)+((v>>6&1)<<2)+((v>>5&1)<<6)]+=1
            elif q==2 and f==6: stores[2,((v>>9&15)<<2)+((v>>7&3)<<6)]+=1
            else: need(not(q in (0,2) and f in (5,7)),hex(pc))
            pc+=2
    expected={(15,n):8 for n in range(160,208,4)}
    expected.update({(15,208):7,(15,4):2,(15,40):1,(15,44):1,(15,56):2,(2,8):1})
    need(pc==0x67190 and stores==expected,'common stores')
    print('PASS: 3 calls to same helper; 6 branch byte stores; common 109 a5 word stores + 1 stack store')


if __name__=='__main__': audit(Path(sys.argv[1]).read_bytes())
