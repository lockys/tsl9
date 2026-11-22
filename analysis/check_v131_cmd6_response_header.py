"""Offline V1.31 / Xwchc: from serializer return to the next call (no provider execution)."""
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok:raise ValueError('response header mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def trace(n,flag,tag):
    sp=0x2000fe80;d=0x20004828;ident=0x217;r=[0]*32;r[2]=sp;r[8:11]=[d,ident,n];r[18:20]=[tag,7];events=[];pc=0x4eabe
    def store(a,w,v):events.append(('W',a,w,v&((1<<(8*w))-1)))
    for _ in range(30):
        at=pc;i=at-0x40000;h=int.from_bytes(b[i:i+2],'little');q=h&3;f=h>>13;rd=h>>7&31;c=8+(h>>2&7);a=8+(h>>7&7);pc+=2
        if q==3:
            w=int.from_bytes(b[i:i+4],'little');pc+=2;op=w&127;k=w>>12&7;i1=w>>15&31;i2=w>>20&31
            if op==19 and k==5:r[rd]=r[i1]>>(w>>20)
            elif op==35 and k==0:store(r[i1]+sx((w>>25<<5)|(w>>7&31),12),1,r[i2])
            elif op==55:r[rd]=w&0xfffff000
            elif op==3 and k==4:
                addr=r[i1]+sx(w>>20,12);ck(addr==0x20002fa2);events.append(('R',addr,1,flag));r[rd]=flag
            elif op==111:
                ck(rd==1);dest=at+sx((w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1,21);break
            else:raise ValueError(hex(at))
        elif q==0 and f==5:store(r[a]+8*(h>>10&3)+2*(h>>5&3)+(h>>12&1),1,r[c])
        elif h&0xf863==0x8060:store(sp+2*(h>>8&7)+16*(h>>7&1),2,r[c])
        elif q==2 and f==6:store(sp+4*(h>>9&15)+64*(h>>7&3),4,r[h>>2&31])
        elif q==1 and f in (0,2):r[rd]=((r[rd] if f==0 else 0)+sx((h>>12&1)<<5|(h>>2&31),6))&0xffffffff
        elif q==0 and f==0:r[c]=sp+64*(h>>7&15)+16*(h>>11&3)+8*(h>>5&1)+4*(h>>6&1)
        elif h==0x8526:r[10]=r[9]
        elif q==1 and f==6:
            off=(h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1
            if not r[a]:pc=at+sx(off,9)
        else:raise ValueError(hex(at))
    else:raise ValueError('step bound')
    ck(events==[('W',d,1,7),('W',d+1,1,tag),('W',d+3,1,n>>8&255),('W',sp+24,2,5),('R',0x20002fa2,1,flag),('W',d+2,1,n&255),('W',sp+26,2,(n+4)&65535),('W',sp+28,4,d)])
    ck(r[10:12]==[ident,sp+24] and dest==(0x4e6ca if flag else 0x4e4cc))
for f in range(256):
    for n in (4,0,0x1234,0xffff,0xffffffff):trace(n,f,f^0x95)
print('PASS: 256 length-4 cases and 1024 synthetic length controls; ordered header writes, descriptor and both call targets')
