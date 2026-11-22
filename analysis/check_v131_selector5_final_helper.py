"""Usage: python check_v131_selector5_final_helper.py V131_REFERENCE.bin
Bounded instruction replay. Xwchc interpretation, ordinary disjoint RAM, no device.
"""
import hashlib, sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('final helper mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')

def sx(x,n):return x-(1<<n) if x>>(n-1) else x

def trace(flag,ident,count):
    S=0x2000ff80; end=0x4e1d0; pc=0x4d962;r=[0]*32;r[1]=end;r[2]=S;r[10:12]=[ident,count];m={0x20002f9c:flag};vis=[]
    def get(p,n):return sum(m[p+i]<<(8*i) for i in range(n))
    def put(p,n,v):m.update({p+i:v>>(8*i)&255 for i in range(n)})
    for _ in range(100):
        if pc in (end,0x671d2):break
        ck(0x4d962<=pc<0x4d98a or 0x5335e<=pc<0x5336e or 0x671c6<=pc<0x671d2 or pc==0x671f2)
        vis.append(pc);at=pc;i=at-0x40000;w=int.from_bytes(b[i:i+2],'little');q=w&3;f=w>>13;pc+=2
        d=w>>7&31;c=8+(w>>2&7);v=w>>2&31
        if q==3:
            w=int.from_bytes(b[i:i+4],'little');pc+=2;op=w&127;a=w>>15&31;k=w>>20;imm=sx(k,12)
            if op==55:r[d]=w&0xfffff000
            elif op==3 and w>>12&7==4:r[d]=get((r[a]+imm)&0xffffffff,1)
            elif op==19 and w>>12&7==0:r[d]=(r[a]+imm)&0xffffffff
            elif op==99 and w>>12&7==1:
                off=(w>>31<<12)|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1
                if r[a]!=r[k&31]:pc=at+sx(off,13)
            elif op==111:
                off=w>>31<<20|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1;r[d]=pc;pc=at+sx(off,21)
            else:raise ValueError(hex(at))
        elif w==0x8082:pc=r[1]&~1
        elif w==0x6105:r[2]+=32 # c.addi16sp sp,32
        elif w&0xf863==0x8060:put(r[2]+((w>>8&7)<<1)+((w>>7&1)<<4),2,r[c]) # Xwchc SHSP
        elif q==2 and f==1:r[c]=get(r[8+(w>>7&7)]+((w>>10&7)<<3)+((w>>5&3)<<1),2) # Xwchc LHU
        elif q==1 and f in (0,2):r[d]=((r[d] if f==0 else 0)+sx((w>>12&1)<<5|(w>>2&31),6))&0xffffffff
        elif q==2 and f==6:put(r[2]+((w>>7&3)<<6)+((w>>9&15)<<2),4,r[v])
        elif q==2 and f==2:r[d]=get(r[2]+((w>>2&3)<<6)+((w>>4&7)<<2)+((w>>12&1)<<5),4)
        elif q==0 and f==0:r[c]=r[2]+((w>>7&15)<<6)+((w>>11&3)<<4)+((w>>5&1)<<3)+((w>>6&1)<<2)
        elif q==1 and f in (6,7):
            off=((w>>12&1)<<8)|((w>>5&3)<<6)|((w>>2&1)<<5)|((w>>10&3)<<3)|((w>>3&3)<<1)
            if (r[8+(w>>7&7)]!=0)==(f==7):pc=at+sx(off,9)
        else:raise ValueError(hex(at))
        if at==0x4d980:ck(r[10:13]==[1,S-18,S-20])
    ck((0x5335e in vis)==(flag==1) and (0x671c6 in vis)==(flag==1))
    ck((get(S-18,2),get(S-20,2))==(ident&65535,count&65535))
    if flag==1 and not count&65535:ck(pc==0x671d2);return
    ck(pc==end and r[2]==S and r[10]==(0 if flag==1 else ident))

for f in range(256):
    for i in (0,255,0x1234,65535,0x12345678):trace(f,i,1)
trace(1,0x1234,0);trace(1,0x1234,65536)
print('PASS: 1275 skipped, 5 called and returned zero, 2 low-halfword-zero controls stop at 0x671d2')
