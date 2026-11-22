"""First role wrapper, V1.31 reference only. CLI: python SCRIPT carrier.bin
Decode its six handler loads and call pairs. Project the checked registrar under
Xwchc byte loads/store; all other callees are assumed to return without changing
task state or the saved link. Stop at the tail jump, not at the APP return.
"""
from hashlib import sha256
from pathlib import Path
import sys

PAIRS = ((0x4dbf2,0x4da70),(0x465b4,0x46570),(0x4a808,0x4a7d6),
         (0x502b4,0x50412),(0x6cc4c,0x6c300),(0x4d1b0,0x4d172))

def check(ok, label):
    if not ok: raise ValueError(label)

def signed(x, bits): return x-(1<<bits) if x>>(bits-1) else x

def jump(w, pc, rd):
    check(w&4095 == (rd<<7)|0x6f, 'jump destination register')
    imm=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    return pc+signed(imm,21)

def decode(b):
    def data(p,n): return b[p-0x40000:p-0x40000+n]
    def word(p): return int.from_bytes(data(p,4),'little')
    check(data(0x6dd16,4).hex()=='411106c6' and jump(word(0x6dd1a),0x6dd1a,1)==0x61b1c,'prefix')
    pairs=[]
    for p in range(0x6dd1e,0x6dd7e,16):
        hi,lo=word(p),word(p+4)
        check(hi&4095==0x537 and lo&0xfffff==0x50513,'a0 handler load')
        h=(hi&0xfffff000)+signed(lo>>20,12)
        check(jump(word(p+8),p+8,1)==0x43c4e,'registration')
        pairs.append((h,jump(word(p+12),p+12,1)))
    check(data(0x6dd7e,4).hex()=='b2404101' and jump(word(0x6dd82),0x6dd82,0)==0x6d572,'restore and tail')
    check(data(0x43c4e,48).hex()=='373700201307c7191c33342363ffd700b736002083a6461c1386170010b313972700369708c33e8582809307f00fe5bf','registrar body')
    return tuple(pairs)

def project(pairs,n,capacity):
    stores=[]; forwarded=[]
    for handler,consumer in pairs:
        if n<capacity:
            result=n; n+=1; stores.append((result,handler))
        else: result=255
        forwarded.append((consumer,result))
    return n,stores,forwarded

if __name__=='__main__':
    b=Path(sys.argv[1]).read_bytes();check(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22','reference identity')
    pairs=decode(b);check(pairs==PAIRS,'handler/consumer ledger')
    for n in range(256):
        for cap in range(256):
            end,stores,fw=project(pairs,n,cap); k=min(6,max(0,cap-n))
            check(end==n+k and stores==[(n+i,h) for i,(h,_) in enumerate(PAIRS[:k])],'stored slots')
            check(fw==[(c,n+i if i<k else 255) for i,(_,c) in enumerate(PAIRS)],'forwarded IDs')
    mutant=bytearray(b);mutant[0x2dd24]^=0x10
    check(decode(mutant)[0]==(PAIRS[0][0]+1,PAIRS[0][1]),'handler immediate substitution')
    print('PASS: six decoded handler/consumer pairs; 65536 count/capacity projections; nominal IDs 5..10; tail 6d572; substitution distinguished')
