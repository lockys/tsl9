"""Symbolic straight-line APP call arguments; opaque normal returns, not device execution."""
from pathlib import Path
from hashlib import sha256
import sys


def check(b):
    if sha256(b).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('APP identity')
    regs = {0:0, 2:0x20010000, 3:0x20004000, 8:0x40000}; calls=[]; stores=[]
    pc=0x8eb2
    def imm(v,n): return (v ^ (1<<(n-1))) - (1<<(n-1))
    while pc<0x8f2e:
        i=pc-0x8000; h=int.from_bytes(b[i:i+2],'little'); n=4 if h&3==3 else 2
        w=int.from_bytes(b[i:i+n],'little'); rd=w>>7&31; rs=w>>15&31; rt=w>>20&31
        if n==4 and w&0x707f==0x2003 and rs==8: regs[rd]=('slot',regs[8]+imm(w>>20,12))
        elif n==4 and w&127==23: regs[rd]=(pc+(w&0xfffff000))&0xffffffff
        elif n==4 and w&0x707f==19: regs[rd]=(regs[rs]+imm(w>>20,12))&0xffffffff
        elif n==4 and w&0x707f in (0x23,0x1023):
            stores.append((regs[rs]+imm(w>>25<<5|(w>>7&31),12),1+(w>>12&1),regs.get(rt)))
        elif n==2 and h&0xe003==0x4001: regs[rd]=imm((h>>2&31)|(h>>12&1)<<5,6)
        elif h==0x0070: regs[12]=regs[2]+12
        elif h==0x9782:
            calls.append((pc,regs[15],tuple(regs.get(x) for x in (10,11,12))))
            for x in (1,5,6,7,*range(10,18),28,29,30,31): regs.pop(x,None)
        else: raise ValueError(hex(pc))
        pc+=n
    slots=[(c[1][1]-0x40034)//4 for c in calls]; sp=regs[2]
    if slots!=[91,94,99,19,80,80,80,72,72] or calls[3][2][0]!=0x8614: raise ValueError(calls)
    if [c[2] for c in calls[4:]]!=[(774,13,0x19dec),(785,2,sp+12),(786,2,sp+14),(3,160,None),(4,160,None)]: raise ValueError(calls)
    if stores!=[(regs[3]+157,1,None),(sp+12,2,6),(sp+14,2,1000)]: raise ValueError(stores)
    if any(c[1][1]!=0x40034+4*s for c,s in zip(calls,slots)): raise ValueError('slot alignment')
    print('PASS: 9 calls, 3 direct stores; role slots 91/94/99; parameter lengths 13/2/2; no slot 109')


if __name__=='__main__': check(Path(sys.argv[1]).read_bytes())
