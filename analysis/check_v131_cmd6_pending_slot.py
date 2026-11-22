"""python check_v131_cmd6_pending_slot.py V131.bin -- offline, conditional Xwchc."""
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x:raise ValueError('pending slot mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def sx(n,k):return (n^(1<<(k-1)))-(1<<(k-1))
def run(mem,desc,ident):
    r=[0]*32;r[10:12]=[ident,desc];pc=0x4e4cc;log=[]
    for _ in range(28):
        i=pc-0x40000;h=int.from_bytes(b[i:i+2],'little');q=h&3;f=h>>13;rd=h>>7&31;c=8+(h>>2&7);a=8+(h>>7&7);at=pc;pc+=2
        if q==3:
            w=int.from_bytes(b[i:i+4],'little');pc+=2
            if w&127==55:r[rd]=w&0xfffff000
            elif w==0x02d70733:r[14]*=r[13]
            elif w&0x707f==19:r[rd]=r[w>>15&31]+sx(w>>20,12)
            else:raise ValueError(hex(at))
        elif q==2 and f in (1,5) or q==0 and f in (2,6):
            size=2 if q==2 else 4;off=8*(h>>10&7)+(2*(h>>5&3) if size==2 else 4*(h>>6&1)+64*(h>>5&1));addr=r[a]+off
            if f in (1,2):r[c]=int.from_bytes(bytes(mem[addr+i] for i in range(size)),'little');log.append(('r',addr,size,r[c]))
            else:
                val=r[c]&((1<<(8*size))-1);mem.update({addr+i:v for i,v in enumerate(val.to_bytes(size,'little'))});log.append(('w',addr,size,val))
        elif q==1 and f in (0,2):r[rd]=(r[rd] if f==0 else 0)+sx((h>>12&1)<<5|(h>>2&31),6)
        elif h==0x97ba:r[15]+=r[14]
        elif q==1 and f==7:
            off=(h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1
            if r[a]:pc=at+sx(off,9)
        elif h==0x8082:return r[10],log
        else:raise ValueError(hex(at))
    raise ValueError('step bound')
row=0x2000332c;desc=0x2000fe98
for ident in (0,1,0xffff,0x12345678):
    for ptr in (0x20004828,0x20004c08):
        m={row+i:0xa5 for i in range(12)};m.update({row+i:0 for i in range(4,8)})
        d=b'\x05\x00\x08\x00'+ptr.to_bytes(4,'little');m.update({desc+i:v for i,v in enumerate(d)})
        first=[('r',desc,2,5),('r',row+4,4,0),('r',desc+4,4,ptr),('w',row+10,2,ident&65535),('w',row+4,4,ptr),('r',desc+2,2,8),('w',row+8,2,8)]
        ck(run(m,desc,ident)==(0,first));ck(bytes(m[row+i] for i in range(4))==bytes([0xa5])*4)
        # Reuse the live row, but do not make the second descriptor's pointer or length available.
        for i in range(2,8):del m[desc+i]
        old=m.copy();ck(run(m,desc,ident^0xff)==(22,[('r',desc,2,5),('r',row+4,4,ptr)]));ck(m==old)
print('PASS: 8 empty-to-occupied pairs; first stores identifier, pointer, length; second returns 22 with no writes; payload never mapped')
