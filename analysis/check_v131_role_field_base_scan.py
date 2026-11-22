"""Bounded store census rooted at the LUI page used by 4daf6. APP, V131 arguments."""
from hashlib import sha256
from pathlib import Path
import sys

A=0x20003350;PAGE=A&~4095

def ck(ok):
    if not ok:raise ValueError('role field census mismatch')

def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))

def scan(b,va,target):
    hits=set()
    for i in range(0,len(b)-3,2):
        u=int.from_bytes(b[i:i+4],'little');rd=u>>7&31
        if u&0xfffff07f!=PAGE|55 or not rd:continue
        regs={rd:PAGE};j=i+4
        for _ in range(32):
            w=int.from_bytes(b[j:j+4],'little');n=4 if w&3==3 else 2
            if j+n>len(b):break
            rd=w>>7&31;rs=w>>15&31;op=w&127;f=w>>12&7
            c=w&0xe003;store=None
            if n==4 and op==35 and f<=2:
                store=rs,sx((w>>25<<5)|rd,12),1<<f
            elif n==2 and c in (0xa000,0xc000):
                d=((w>>10&3)*8+(w>>12&1)+(w>>5&3)*2 if c==0xa000 else (w>>10&7)*8+(w>>6&1)*4+(w>>5&1)*64)
                store=8+(w>>7&7),d,1 if c==0xa000 else 4
            elif n==4 and op in (3,19,23,51,55):
                q=None
                if op==19 and f==0 and rs in regs:q=(regs[rs]+sx(w>>20,12))&0xffffffff
                if op==55:q=w&0xfffff000
                regs.pop(rd,None)
                if rd and q is not None:regs[rd]=q
            elif n==2 and c in (0x0001,0x4001,0x4000,0x2000):
                if c==1 and rd in regs:regs[rd]=(regs[rd]+sx((w>>2&31)|(w>>7&32),6))&0xffffffff
                elif c!=1:regs.pop(rd if c==0x4001 else 8+(w>>2&7),None)
            else:break  # unknown instruction or control transfer
            if store:
                r,d,width=store
                if r in regs:
                    p=(regs[r]+d)&0xffffffff
                    if p<target+2 and target<p+width:hits.add((va+j,p,width))
            j+=n
    return sorted(hits)

if __name__=='__main__':
    a,b=(Path(p).read_bytes() for p in sys.argv[1:]);ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
    ck(b[0xdaf2:0xdafa]==bytes.fromhex('373a002003450a35')) # LUI s4,page; LBU a0,848(s4)
    # Positive fixtures: derive A in a5, then store at A+1 or A. Branch ends a window.
    prefix=bytes.fromhex('b737002093870735');sb=bytes.fromhex('9cb3');sw=bytes.fromhex('9cc3')
    ck(scan(prefix+sb,0,A)==[(8,A+1,1)] and scan(prefix+sw,0,A)==[(8,A,4)])
    ck(not scan(prefix+bytes.fromhex('01a0')+sw,0,A))
    for label,img,va in [('APP',a,0x8000),('reference',b,0x40000)]:
        hits=scan(img,va,A);ck(not hits);print(label,'target pair:',hits)
    ck((0x4dadc,0x20003314,1) in scan(b,0x40000,0x20003314))
    print('PASS: bounded derived-base search; neighboring real SB and compressed SB/SW positive controls')
