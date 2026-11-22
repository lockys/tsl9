"""0x1083c calls incoming predicate(arg); zero skips registration. Nonzero calls
0x820c(0) then requests 0x9124(0x107c0,0,2000,0), returning the predicate
word, not the registration result (normal returns, intact s0 and stack).
0x10936 tail path: predicate 0x1059c accepts iff record bytes +3..+10
are all zero. Readable stable record; not evidence of delivery or live data.
Run from repo root with Python 3. Scope of caller census: 32-bit JAL only.
"""
from hashlib import sha256
from pathlib import Path
b = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('1083c evidence mismatch')
def u(p,n): return int.from_bytes(b[p-32768:p-32768+n], 'little')
def sx(x,k): return (x^(1<<(k-1)))-(1<<(k-1))
def jal(p):
    w=u(p,4); ck(w&127==111)
    return p+sx((w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1,21)
def pair(p):
    a,c=u(p,4),u(p+4,4); ck(a&4095==0x517 and c&0xfffff==0x50513)
    return (p+(a&0xfffff000)+sx(c>>20,12))&0xffffffff
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
sites=[p for p in range(32768,32768+len(b)-3,2) if u(p,4)&127==111 and jal(p)==0x1083c]
ck(sites==[0x108ea,0x10940,0x10956,0x109d6,0x10a28,0x1518c,0x15242])
entries=[pair(p) for p in (0x108e0,0x10938,0x1094c,0x109cc,0x10a1e,0x15184,0x1523a)]
ck(entries==[0x1056e,0x1059c,0x105c4,0x105d0,0x105ec,0x1069e,0x1069e])
for p,h in [(0x1083c,'4111aa872e8522c406c682972a8411cd0145'),(0x10852,'81461306007d8145'),(0x10866,'2285b240224441018280'),(0x10936,'aa85'),(0x820c,'894763e7a7009387010caa97a38007008280')]:
    v=bytes.fromhex(h); ck(b[p-32768:p-32768+len(v)]==v)
ck(jal(0x1084e)==0x820c and pair(0x1085a)==0x107c0 and jal(0x10862)==0x9124)

def run(rec):
    pc=0x1059c; regs=[0]*32; reads=[]
    for _ in range(20):
        h=u(pc,2); w=u(pc,4); rd=w>>7&31
        if w&0x707f in (0x4003,0x5003):
            ck((w>>15&31)==10); off=w>>20; n=1 if w&0x7000==0x4000 else 2
            reads.extend(range(off,off+n)); regs[rd]=int.from_bytes(rec[off:off+n],'little'); pc+=4
        elif h&0xe003==0xe001:
            d=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5
            pc+=sx(d,9) if regs[8+(h>>7&7)] else 2
        elif w==0x0017b793: regs[15]=int(regs[15]==0); pc+=4
        elif h==0x4781: regs[15]=0; pc+=2
        elif h==0xbfed: pc=0x105bc
        elif h==0x853e: regs[10]=regs[15]; pc+=2
        elif h==0x8082: return regs[10],reads
        else: raise ValueError(hex(pc))
    raise ValueError('no return')
rec=bytearray([255]*3+[0]*8)
ck(run(rec)==(1,list(range(3,11))))
for i in range(3,11):
    end=next(k for k in (3,5,7,9,10) if k>=i)
    for value in range(1,256):
        rec[i]=value; ck(run(rec)==(0,list(range(3,end+1))))
    rec[i]=0
print('PASS: seven JAL sites, six distinct predicates; 2041 record cases with short-circuit read order')
