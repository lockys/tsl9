"""Role initialization destinations before the 4daf6 count read. Input: V1.31 carrier."""
from hashlib import sha256
from pathlib import Path
import sys

A=0x20003350; FILL=0x2000039c

def ck(ok):
    if not ok:raise ValueError('role fill footprint mismatch')

def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))

def window(b,lo,hi,r):
    pc=lo; r=dict(r); stores=[]
    while pc<hi:
        i=pc-0x40000;w=int.from_bytes(b[i:i+4],'little');op=w&127;d=w>>7&31;s=w>>15&31;t=w>>20&31
        n=4 if w&3==3 else 2
        if n==2:
            h=w&65535;imm=sx(((h>>2)&31)|((h>>7)&32),6)
            if h&0xe003==0x4001:r[d]=imm
            elif h==0x0141:pass # c.addi sp,16; SP unused by the traced arguments
            else:raise ValueError(hex(pc))
        elif op==55:r[d]=w&0xfffff000
        elif op==23:r[d]=pc+(w&0xfffff000)
        elif op==19 and w>>12&7==0:r[d]=r[s]+sx(w>>20,12)
        elif (w&0xfe00707f)==0x02000033:r[d]=(r[s]*r[t])&0xffffffff
        elif op==35 and w>>12&7==2:stores.append((r[s]+sx((w>>25<<5)|d,12),4,r[t]))
        elif (w&0x707f)==0x67:
            ck(pc+n==hi);return ((r[s]+sx(w>>20,12))&0xfffffffe,d,r[10],r[11],r[12],stores)
        else:raise ValueError(hex(pc))
        pc+=n
    raise ValueError('missing transfer')

def overlap(p,n):return n>0 and p<A+2 and A<p+n  # nonwrapping intervals only

if __name__=='__main__':
    b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    ck(b[0xdad8:0xdae0]==bytes.fromhex('13060003238aa730')) # li a2,48; sb a0,788(a5)
    ck(b[0xee04:0xee08]==bytes.fromhex('b7340020')) # s1 page before allocator; assume s1 preserved on return
    ck(b[0xee10:0xee12]==bytes.fromhex('1024')) # conditional Xwchc byte load to a2
    ck(window(b,0x4dae0,0x4daf2,{0:0,12:48})==(FILL,1,A-48,0,48,[]))
    ck(window(b,0x4ee3e,0x4ee56,{0:0})==(FILL,0,A+8,0,48,[]))
    ck(not overlap(A-48,48) and not overlap(A+8,48) and overlap(A-48,49))
    # a2 here is the *fresh* record count, not the earlier allocation request.
    for count in range(256):
        p=0x200048ac
        ck(window(b,0x4ee12,0x4ee28,{0:0,9:0x20003000,10:p,12:count})==(FILL,1,p,0,60*count,[(A+4,4,p)]))
        ck(not overlap(p,60*count))
    print('PASS: two fixed 48-byte fill destinations flank the count pair; dynamic pointer stored at +4, length 60*N checked for 256 reloaded byte values (separate example heap)')
