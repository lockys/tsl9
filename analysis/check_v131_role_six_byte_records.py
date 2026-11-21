"""V1.31 reference, selected direct writes and call edges, no target execution."""
from hashlib import sha256
from pathlib import Path
import sys


def need(ok, why):
    if not ok:
        raise ValueError(why)


def check(b):
    need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22','carrier')
    def w(p):
        return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
    def imm(p):
        return ((w(p)>>20)^2048)-2048
    def upper(p):
        return w(p)&0xfffff000
    src=upper(0x53868)+imm(0x53874); dst=upper(0x5386c)+imm(0x53878)
    need((src,dst,(w(0x53872)>>2)&31,0x53888+upper(0x53888)+imm(0x5388c))==(0x20003204,0x200034a0,6,0x20000332),'copy')
    base=upper(0x538bc)+imm(0x538c0); need(base==0x200033b8 and imm(0x538da)==952,'record bases')
    p=0x53868; fixed=[]; saved=[]
    while p<0x5397c:
        a=w(p); h=a&65535
        if a&3==3:
            if a&127==35:
                reg=(a>>15)&31; width=1<<(a>>12&7); off=(a>>25)*32+(a>>7&31)
                need(reg in (14,8) and off<2048,'unexpected store base or offset'); fixed.extend(range(base+off,base+off+width))
            p+=4
        else:
            if h>>13 in (5,6,7):
                if h&3==2 and h>>13==6: saved.append(p)
                else: need(h&3==1,'unexpected compressed store') # branch or jump
            p+=2
    need(p==0x5397c and saved==[0x5387c,0x5387e,0x53880,0x53882,0x53886],'instruction boundaries/frame')
    need(sorted(fixed)==list(range(0x200034ac,0x200034b8)),'two 6-byte destinations')
    slots=[upper(p)+imm(p+4) for p in (0x433c0,0x433dc)]
    need(slots==[0x20003210,0x200031e0] and w(0x433d2)&65535==0x9782,'optional indirect call')
    for p,d,rd in [(0x43e98,0x433a8,1),(0x43ebc,0x433a8,1),(0x642fe,0x660ce,1),(0x64302,0x638ea,1),(0x6430a,0x641b0,0)]:
        a=w(p); off=(a>>31<<20)|(a>>12&255)<<12|(a>>20&1)<<11|(a>>21&1023)<<1
        need(a&4095==rd*128+111 and p+(off^0x100000)-0x100000==d,hex(p))
    print('PASS: copy arguments; 2 six-byte write sets; 5 frame saves; 2 optional callback slots; 5 JAL targets')


if __name__=='__main__':
    check(Path(sys.argv[1]).read_bytes())
