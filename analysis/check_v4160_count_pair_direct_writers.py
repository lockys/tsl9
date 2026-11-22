"""Search bounded address forms, not all writers. Usage: python check.py APP V131."""
from hashlib import sha256
from pathlib import Path
import sys

BASE=0x20003000; A=BASE+848

def check(x):
    if not x: raise ValueError('pair writer census mismatch')

def signed(i,n):return (i^(1<<(n-1)))-(1<<(n-1))

def scan(b,va):
    direct=[]; pairs=[]
    def u(i):return int.from_bytes(b[i:i+4],'little')
    for i in range(0,len(b)-3,2):
        w=u(i); op=w&127; f=w>>12&7; rd=w>>7&31
        if op==35 and f<3:
            d=signed(((w>>25)<<5)|rd,12); width=1<<f
            # Assuming the base register holds BASE. No such store encoding means
            # base provenance need not be guessed for this particular form.
            hits=tuple(t for t in (A,A+1) if BASE+d<=t<BASE+d+width)
            if hits:direct.append((va+i,width,hits))
        if op not in (23,55) or not rd or i+8>len(b):continue
        k=u(i+4)
        if k&0x707f!=0x13 or k>>15&31!=rd or not (k>>7&31):continue
        v=((va+i if op==23 else 0)+(w&0xfffff000)+signed(k>>20,12))&0xffffffff
        if v in (A,A+1):pairs.append((va+i,v))
    return direct,pairs

def control(d,w):
    ins=(d>>5)<<25|15<<15|w<<12|(d&31)<<7|35
    return ins.to_bytes(4,'little')

if __name__=='__main__':
    a,b=(Path(p).read_bytes() for p in sys.argv[1:]);check([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
    for d,w,h in [(848,0,(A,)),(849,0,(A+1,)),(848,1,(A,A+1)),(846,2,(A,A+1)),(844,2,())]:
        check(scan(control(d,w),0)[0]==([(0,1<<w,h)] if h else []))
    for op,pc,upper in [(55,0,BASE),(23,0x40000,BASE-0x40000)]:
        for d in (848,849):
            ins=(upper|15<<7|op).to_bytes(4,'little')+(d<<20|15<<15|10<<7|19).to_bytes(4,'little')
            check(scan(ins,pc)[1]==[(pc,BASE+d)])
    for name,img,pc in [('APP',a,0x8000),('carrier',b,0x40000),('copied RAM code prefix',b[0x270:0x2b0+2957*4],0x20000000)]:
        stores,pairs=scan(img,pc);print(name,'overlapping immediate stores:',stores,'adjacent materializations:',pairs);check(not stores and not pairs)
    print('PASS: 5 store-width controls and 4 address-pair controls; indirect, compressed, split and bulk stores not excluded')
