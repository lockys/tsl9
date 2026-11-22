"""Check the first node-flag decision at 40d36, on distinct synthetic objects.
Usage: python check_v131_queue_flag_clear.py reference.bin (conditional Xwchc).
Stops at the first write of node+9 or the partial path that doesn't change it.
"""
import sys
from hashlib import sha256
from pathlib import Path
rom=Path(sys.argv[1]).read_bytes()
if sha256(rom).hexdigest()!='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22':raise ValueError('ROM')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def run(n,cap,flag,kind):
    obj=0x21000000;node=obj+0x400;r=[0]*32;r[10]=obj;r[2]=obj+0x800
    m={obj+280:node,obj+78:cap,node+9:flag,node+12:n,node+8:kind,obj+12:0x55};p=0x40d36
    for _ in range(48):
        at=p;i=p-0x40000;w=int.from_bytes(rom[i:i+4],'little');h=w&65535;q=h&3;f=h>>13;d=h>>7&31;s=w>>15&31;t=w>>20&31;imm=sx(w>>20,12);op=w&0x707f;p+=4 if q==3 else 2
        if at==0x40dc0:return at,m[node+9]
        if q==3:
            if op in (0x2003,0x4003):r[d]=m[r[s]+imm]
            elif op==0x7013:r[d]=r[s]&imm
            elif op==0x6013:r[d]=r[s]|imm
            elif op==0x1013:r[d]=(r[s]<<(t&31))&0xffffffff
            elif op==0x5013 and w>>25==32:r[d]=sx(r[s],32)>>t
            elif w&127==99:
                cond={7:r[s]>=r[t],5:r[s]>=r[t],1:r[s]!=r[t]}[w>>12&7]
                if cond:p=at+sx((w>>31<<12)|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1,13)
            elif op==35:
                addr=r[s]+sx((w>>25<<5)|(w>>7&31),12);m[addr]=r[t]&255
                if addr==node+9:return at,m[addr]
            else:raise ValueError(hex(at))
        elif q in (0,2) and f in (1,5):
            a=8+(h>>7&7);c=8+(h>>2&7);off=((h>>12&1)|(h>>10&3)<<3|(h>>5&3)<<1) if q==0 else (8*(h>>10&7)+2*(h>>5&3));addr=r[a]+off
            if f==1:r[c]=m[addr]
            else:
                m[addr]=r[c]&(255 if q==0 else 65535)
                if addr==node+9:return at,m[addr]
        elif h==0x8561:r[10]=sx(r[10],32)>>24
        elif q==1 and f in (0,2):r[d]=(r[d] if f==0 else 0)+sx((h>>12&1)<<5|(h>>2&31),6)
        elif q==2 and f==4:r[d]=r[h>>2&31]
        elif q==2 and f==6:pass # separate stack saves, no reload before cutoff
        elif at==0x40d3a and h==0xcb6d and m[obj+280]:pass
        else:raise ValueError(hex(at))
    raise ValueError('bound')
count=0
for f in range(256):
    for k in (1,2):
        for n,c in ((0,0),(12,0),(12,11),(12,12),(12,13),(255,255),(256,255),(65535,255)):
            expected=((0x40de4 if f&128 else 0x40e06),0) if n<=c else ((0x40d68,f&127) if f&128 else (0x40dc0,f))
            if run(n,c,f,k)!=expected:raise ValueError((n,c,f,k))
            count+=1
print('PASS:',count,'flag/length/capacity/type traces; full clears byte; partial 0x81 becomes 0x01')
