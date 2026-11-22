"""Check the explicit setter and encoded references, not a universal writer census.
Usage: python check_v131_slot0_object_setter.py APP.bin V131.bin
"""
from hashlib import sha256
from pathlib import Path
import sys
A,R=(Path(s).read_bytes() for s in sys.argv[1:])
def ck(ok):
    if not ok: raise ValueError('setter evidence mismatch')
def sx(v,n):return (v^(1<<(n-1)))-(1<<(n-1))
ck(sha256(A).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(sha256(R).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
T=0x55bd4
ck(R[T-0x40000:T-0x40000+10]==bytes.fromhex('b737002023a0a74e8280'))
ck(R[0x13658:0x1365e]==bytes.fromhex('0145ef20a057'))
ck(R[0x13db0:0x13dba]==bytes.fromhex('b737002003a4074e0dc0'))
ck(0x200033b8+296==0x200034e0 and R[0x250:0x254]==T.to_bytes(4,'little'))
def edges(data,base):
    hits=[]
    for i in range(0,len(data)-1,2):
        p=base+i;x=int.from_bytes(data[i:i+4],'little');h=x&65535
        if h&0xe003 in (0x2001,0xa001):
            d=sum(((h>>k)&1)<<j for k,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)))
        elif i+4<=len(data) and x&127==111:
            d=((x>>31)<<20)|(x&0xff000)|((x>>20&1)<<11)|((x>>21&1023)<<1);d=sx(d,21)
            if p+d==T:hits.append(p)
            continue
        else:continue
        if p+sx(d,12)==T:hits.append(p)
    return hits
# Scan halfword alignments, including data. Does not resolve register-based transfers.
ck(edges(R,0x40000)==[0x5365a]);ck(not edges(A,0x8000))
ck(not edges(R[0x2b0:0x2b0+2957*4],0x20000040))
# Direct LW with imm=0x250 from a register holding 0x40000 would load this slot.
ck(not any(int.from_bytes(A[i:i+4],'little')&0xfff0707f==0x25002003 for i in range(0,len(A)-3,2)))
print('PASS: zero-setting direct edge 0x5365a; table word 0x40250 points to setter; no APP direct J/CJ or LW imm=0x250 match')
