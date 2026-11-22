"""Offline V1.31 handler. Stop on message branch; inject retry/post returns, no scheduler or device."""
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('retry event gate mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
def chunk(p,n): return b[p-0x40000:p-0x40000+n]
ck(chunk(0x4dbf2,22).hex()=='41119397050126c206c622c44ac0c187ae8463de0708')
ck(chunk(0x4dca0,44).hex()=='93f715000145e9d7ef00305209cdb737002083c727fa81cbb737002003c547318545ef509f8813c514005db7')
# Predecode the two fixed windows; unsupported opcodes fail closed.
def w(p): return int.from_bytes(chunk(p,4),'little')
def cb(p):
    h=w(p)&65535; ck(h&0xe003==0xc001)
    return p+sx((h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1,9)
def jal(p):
    v=w(p);ck(v&4095==0xef);return p+sx(v>>31<<20|(v&0xff000)|(v>>20&1)<<11|(v>>21&1023)<<1,21)
v=w(0x4dc04);ck(v&0x1fff07f==0x7d063 and 0x4dc04+sx(v>>31<<12|(v>>7&1)<<11|(v>>25&63)<<5|(v>>8&15)<<1,13)==0x4dca0)
ck([cb(p) for p in (0x4dca6,0x4dcac,0x4dcb6)]==[0x4dc70,0x4dcc6,0x4dcc6])
retry,post=jal(0x4dca8),jal(0x4dcc2);ck((retry,post)==(0x4e9ca,0x4354a))
def trace(mask,rc,flag,task):
    if sx((mask<<16 & 0xffffffff)>>16,16)<0:return 'message',[]
    if not mask&1:return 0,[]
    log=[retry]
    if rc:
        log.append(('r',0x20003000+sx(w(0x4dcb2)>>20,12)))
        if flag:log.extend([('r',0x20003000+sx(w(0x4dcbc)>>20,12)),(post,task,1)])
    return mask^1,log
counts=[0,0,0]
for mask in range(65536):
    i=0 if mask>=32768 else 1 if mask%2==0 else 2;counts[i]+=1
    for rc,flag,task in ((0,1,7),(1,0,9),(1,2,255)):
        events=[] if i<2 else [0x4e9ca]+([('r',0x20002fa2)] if rc else [])+([('r',0x20003314),(0x4354a,task,1)] if rc and flag else [])
        ck(trace(mask,rc,flag,task)==(('message',0,mask-1)[i],events))
ck(counts==[32768,16384,16384]);print('PASS: 196608 projections; 32768 masks take message branch, 16384 skip retry, 16384 call retry; fresh flag gates repost')
