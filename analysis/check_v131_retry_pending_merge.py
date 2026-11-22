"""V1.31/Xwchc. Join selected post and scheduler slices with synthetic, separated RAM.
This tests a dispatch in progress, not when the outer scan will reach this task.
"""
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('pending merge mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def code(off,h):ck(b[off:off+len(bytes.fromhex(h))]==bytes.fromhex(h))
code(0x3566,'37360020131715000325461e3a951a21d98d0ea1')
code(0x270+0x8e4,'86073e970e23231007000345c419')
code(0x270+0x906,'239e0a1c829783d7ca1d0347c41993c7f7ff7d8d9317170003a7491e3e971e235d8d0aa3')
# Byte-checked halfword read/write projection. The halfword at +0x1dc masks
# returned handler bits, NOT pending bits posted to the table during the call.
P=0x20004800; Q=P+512; BASE=0x200031e4; CUR=0x2000319c; MASK=0x200031dc

def case(i,original,cleared,redirect):
    m={}
    def put(a,w,z):m.update({a+k:z>>(8*k)&255 for k in range(w)})
    def get(a,w):return sum(m[a+k]<<(8*k) for k in range(w))
    put(BASE,4,P);put(CUR,1,i);put(P+2*i,2,original)
    a=get(BASE,4)+2*get(CUR,1);arg=get(a,2);put(a,2,0);put(MASK,2,0)
    # Handler consumes bit 0. Assume retry succeeds in posting event 1 to i.
    a=get(BASE,4)+2*i;put(a,2,get(a,2)|1);result=arg^1
    put(MASK,2,cleared)
    if redirect:put(BASE,4,Q);put(Q+2*i,2,0x20) # controlled pointer change before return merge
    dst=get(BASE,4)+2*get(CUR,1);live=get(dst,2)
    put(dst,2,(result & ~get(MASK,2))|live)
    expected=((original-1)&(65535^cleared))|(0x20 if redirect else 1)
    ck(get(dst,2)==expected and (not redirect or get(P+2*i,2)==1))
for i in (0,5,254):
    for original in (1,3,0x4001,0x7fff):
        for cleared in (0,1,2,0x4000,65535):
            for redirect in (False,True):case(i,original,cleared,redirect)
print('PASS: 60 stable table merges retain reposted bit 0; 60 changed-table controls merge into reloaded table')
