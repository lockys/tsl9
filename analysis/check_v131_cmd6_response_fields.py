"""Usage: python check_v131_cmd6_response_fields.py V131.bin (offline, conditional Xwchc)."""
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x:raise ValueError('command 6 response mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def window(pc,h):ck(b[pc-0x40000:pc-0x40000+len(bytes.fromhex(h))]==bytes.fromhex(h))
# Save the pair pointer and serializer; request (23,2). On a nonzero result D,
# reload saved pointers and jalr serializer(D+4,pair). Zero takes the status-19 exit.
window(0x4ea96,'5d45 8945 4ad8 06de 22dc 3289 36c6 3ac4 efe0dff9 35c1 2247 2a84 0145 11c7 b246 13054400 b685 0297')
window(0x4eb0e,'cd44 e5b7')
window(0x4ec8a,'9e21 1ca1 9e21 a183 1cb1 be21 3ca1 be21 a183 3cb1 1145 8280')
def check(A,B):
    src=0x2000ff08;D=0x20004828;dst=D+4;r={10:dst,11:src};raw=A.to_bytes(2,'little')+B.to_bytes(2,'little');m={src+i:v for i,v in enumerate(raw)};events=[]
    for pc in range(0x4ec8a,0x4eca2,2):
        h=int.from_bytes(b[pc-0x40000:pc-0x40000+2],'little');base=8+(h>>7&7);reg=8+(h>>2&7)
        if h in (0x219e,0x21be):
            addr=r[base]+8*(h>>10&7)+2*(h>>5&3);r[reg]=m[addr]|(m[addr+1]<<8);events.append(('r',addr))
        elif h in (0xa11c,0xb11c,0xa13c,0xb13c):
            addr=r[base]+8*(h>>10&3)+2*(h>>5&3)+(h>>12&1);m[addr]=r[reg]&255;events.append(('w',addr))
        elif h==0x83a1:r[15]>>=8
        elif h==0x4511:r[10]=4
        elif h==0x8082:break
        else:raise ValueError(hex(pc))
    ck(r[10]==4 and bytes(m[dst+i] for i in range(4))==raw)
    ck(events==[e for i in range(4) for e in [('r',src+(i&~1)),('w',dst+i)]])
for a in range(65536):check(a,a^0x5aa5)
print('PASS: 65536 non-overlapping A/B pairs; 4 halfword reads, 4 byte writes, return 4; caller instruction windows pinned')
