"""First a0 use after each normal poll return (V1.31/Xwchc; no hardware)."""
from hashlib import sha256
from pathlib import Path
import sys


def ck(x):
    if not x: raise ValueError('poll continuation mismatch')


def sx(x,n): return (x ^ (1 << (n-1))) - (1 << (n-1))


def trace(b,start):
    todo=[start]; seen=set(); out=set()
    while todo:
        p=todo.pop()
        if p in seen: continue
        seen.add(p)
        if p==0x60548: out.add((p,'redispatch')); continue
        ck(0x60516<=p<0x60754 or 0x58c52<=p<0x58e7a)
        x=int.from_bytes(b[p-0x40000:p-0x40000+4],'little');h=x&65535
        r=x>>15&31;s=x>>20&31;d=x>>7&31;reads=[];writes=[];n=p+4
        if h&3!=3:
            n=p+2;q=h&3;f=h>>13;u=8+(h>>7&7);v=8+(h>>2&7);z=h>>2&31
            if h==0x8082: out.add((p,'return'));continue
            if q==1 and f==5:
                j=sum((h>>k&1)<<i for k,i in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)));n=p+sx(j,12)
            elif q==1 and f in (6,7):
                reads=[u];j=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5;todo.append(p+sx(j,9))
            elif q==0 and f==1: reads=[u];writes=[v] # vendor compressed load
            elif q==0 and f==5: reads=[u,v] # vendor compressed store
            elif q==1 and f==4 and h>>10&3==2: reads=[u];writes=[u]
            elif q==1 and f==3 and d==2:reads=[2];writes=[2] # c.addi16sp
            elif q==1 and f in (0,2): reads=[d] if f==0 else [];writes=[d]
            elif q==2 and f==0: reads=[d];writes=[d]
            elif q==2 and f==2: reads=[2];writes=[d]
            elif q==2 and f==4 and not h&4096 and z: reads=[z];writes=[d]
            else: raise ValueError(hex(p))
        elif x&127==111:
            j=(x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;t=p+sx(j,21)
            if d==0 and t in (0x6020a,0x57dae): out.add((p,'tail'));continue
            if d==1 and t==0x5f0d2:out.add((p,'callee-overwrite'));continue
            ck(d==1 and t==0x63e58) # prior verified summary: normal return leaves a0 intact
        elif x&127==99:
            reads=[r,s];j=x>>31<<12|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1;todo.append(p+sx(j,13))
        elif x&127 in (3,19):reads=[r];writes=[d]
        elif x&127==35:reads=[r,s]
        elif x&127==55:writes=[d]
        else:raise ValueError(hex(p))
        if 10 in reads:out.add((p,'read'))
        elif 10 in writes:out.add((p,'overwrite'))
        else:todo.append(n)
    return out


if __name__=='__main__':
    b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    routes={0x6059a: [(0x605aa,'overwrite'),(0x605e0,'tail'),(0x60734,'overwrite'),(0x60752,'return')],0x6067c:[(0x6068c,'overwrite'),(0x606a2,'overwrite')],0x606f0:[(0x606f8,'overwrite'),(0x60708,'callee-overwrite'),(0x60548,'redispatch'),(0x605e0,'tail'),(0x60734,'overwrite'),(0x60752,'return')],0x58d90:[(0x58da0,'overwrite'),(0x58d3c,'tail'),(0x58e78,'return')]}
    for p,want in routes.items():
        ck(trace(b,p)==set(want));m=bytearray(b);i=p-0x40000;m[i:i+2]=bytes.fromhex('aa87');ck(trace(m,p)=={(p,'read')});print(hex(p),'PASS',len(want),'endpoints; injected read detected')
