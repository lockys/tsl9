"""V1.31 nominal successful allocation; placement and heap chain are synthetic."""
import sys
from hashlib import sha256
from pathlib import Path
b = Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('unexpected buffer origin')
ck(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n):
    i = p-0x40000 if p<0x20000000 else p-0x20000000+0x270
    return b[i:i+n]
def win(p,h):
    v=bytes.fromhex(h); ck(raw(p,len(v))==v)
def sx(v,k): return (v^(1<<(k-1)))-(1<<(k-1))
def pair(p,rd):
    w=int.from_bytes(raw(p,4),'little'); j=int.from_bytes(raw(p+4,4),'little')
    ck(w&127==23 and j&0x707f==103 and (w>>7&31)==(j>>15&31) and (j>>7&31)==rd)
    return (p+(w&0xfffff000)+sx(j>>20,12))&0xfffffffe
win(0x4ea96,'5d458945');win(0x4eaa6,'efe0dff935c1')
win(0x4da42,'1905956542054111938535c0418106c6');ck(pair(0x4da52,1)==0x20000040)
win(0x20000066,'93073500c207c183f19bc207c183');win(0x200000f4,'2105')
win(0x4da5a,'01c9b240e9554101');ck(pair(0x4da62,0)==0x200001e4)
win(0x4e6e6,'4840914506ce');ck(pair(0x4e6ec,1)==0x200001e4)
win(0x200001f4,'2a87b305b540');win(0x20000202,'938687009c43e369d7fee377f7fe2e85e3e4d5fee3f2f5fe8280')
# Apply the helper's four actual unsigned comparisons to a valid selected block.
def shift(p,delta,h,limit):
    r={14:p,13:h+8,15:limit,11:p-delta}
    for pc in (0x20000208,0x2000020c,0x20000212,0x20000216):
        w=int.from_bytes(raw(pc,4),'little'); a=r[w>>15&31]; c=r[w>>20&31]
        if {6:a<c,7:a>=c}[w>>12&7]: return p
    return r[11]
for size in (32,36,40): # exact/split or larger unsplit block
    for h in range(0x20005000,0x20005200,4):
        base=h+8; limit=base+size; d=shift(base,-6,h,limit); start=shift(d,4,h,limit)
        ck((d,start,start-2,start+12)==(base+6,base+2,base,base+14))
        ck(base<start+12<limit)
print('PASS: 384 nominal placements; request 23+6=29 (aligned 32), D=P+6, queue input=P+2, completed cursor=P+14')
