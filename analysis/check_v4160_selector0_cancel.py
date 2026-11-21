"""Run the selected APP branches, with synchronous helper returns supplied by the test."""
import hashlib, itertools, sys
from pathlib import Path

B = Path(sys.argv[1]).read_bytes()
M = 0xffffffff

def check(ok):
    if not ok: raise ValueError('selector 0 evidence mismatch')

def rom(p, n):
    check(0x8000 <= p <= 0x8000 + len(B) - n)
    return int.from_bytes(B[p-0x8000:p-0x8000+n], 'little')

def sx(x,n): return (x ^ (1 << (n-1))) - (1 << (n-1))

def run(sel, first, second, old, flags):
    r=[0]*32; gp=0x20004000; rec=0x2000c694
    r[3],r[8],r[9]=gp,sel,1
    mem={gp+263:old, gp+84:rec, rec:flags}; calls=[]; pc=0xe246
    for _ in range(150):
        if pc in (0xe66c,0xe568):return pc,calls,mem[gp+263],r[10]
        h=rom(pc,2); q=h&3; f=h>>13; nxt=pc+2; d=h>>7&31; a=8+(h>>7&7); c=8+(h>>2&7); z=h>>2&31; imm=(h>>12&1)<<5|z
        if q==3:
            w=rom(pc,4); nxt=pc+4; op=w&127; d=w>>7&31; a=w>>15&31; c=w>>20&31; f=w>>12&7; k=sx(w>>20,12)
            if op==0x63:
                off=sx((w>>31)<<12|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1,13)
                if {0:r[a]==r[c],1:r[a]!=r[c],6:r[a]<r[c],7:r[a]>=r[c]}[f]:nxt=pc+off
            elif op==0x6f:
                off=sx(w>>31<<20|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1,21); target=pc+off
                check(d==1 and target in (0x8202,0xb664,0xb6a8,0xd052,0xbd00,0xda36,0x167a6));calls.append((target,r[10]));r[1]=nxt
                r[10]={0xb664:first,0xb6a8:second}.get(target,0)
            elif op==0x13 and f in (0,7):r[d]=(r[a]+k if f==0 else r[a]&k)&M
            elif op in (0x17,0x37):r[d]=((pc if op==0x17 else 0)+(w&0xfffff000))&M
            elif op==0x33 and f==1:r[d]=(r[a]<<(r[c]&31))&M
            elif op==3 and f==4:r[d]=mem[r[a]+k]&255
            elif op==0x23 and f==0:mem[r[a]+sx((w>>25)<<5|d,12)]=r[c]&255
            else:raise ValueError(hex(pc))
        elif (q,f)==(1,2):r[d]=sx(imm,6)&M
        elif (q,f)==(1,5):nxt=pc+sx(sum((h>>i&1)<<j for i,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11))),12)
        elif q==1 and f in (6,7):
            off=sx((h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5,9)
            if bool(r[a])==(f==7):nxt=pc+off
        elif (q,f)==(0,2):
            p=r[a]+((h>>5&1)<<6|(h>>10&7)<<3|(h>>6&1)<<2);r[c]=rom(p,4) if p<0x20000000 else mem[p]
        elif (q,f)==(2,0):r[d]=(r[d]<<imm)&M
        elif h==0x8782:nxt=r[15]&~1
        elif h&0xf003==0x9002 and z:r[d]=(r[d]+r[z])&M
        elif h==0x8f7d:r[14]&=r[15]
        elif h==0x8bc1:r[15]&=16
        else:raise ValueError(hex(pc))
        pc=nxt
    raise ValueError('step limit')

check(hashlib.sha256(B).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
check((0x1a13c+rom(0x1a13c,4))&M==0xe246)
count=hits=0
for s,f,g,old,flag in itertools.product((64,65,66),(0,1),(0,1),(0,1,255),range(256)):
    end,log,state,arg=run(s,f,g,old,flag); yes=bool(flag&16)
    check(end==(0xe66c if yes else 0xe568) and (not yes or arg==0))
    check([a for a,v in log]==[0x8202,0xb664,0xb6a8]+([0xd052] if s!=66 else [])+([0xbd00] if s==64 or old else [])+[0xda36,0x167a6])
    check(log[-2:]==[(0xda36,int(s==64)),(0x167a6,s+47)] and state==int(s==64));count+=1;hits+=yes
print(f'PASS: {count} selector-0 cases; {hits} reach cancellation; notification arguments 111/112/113')
