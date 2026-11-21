"""V1.31 reference only: follow direct branches to the first a0 touch or transfer."""
from hashlib import sha256
from pathlib import Path
import sys


def ck(ok):
    if not ok:
        raise ValueError('slot 3/4 evidence mismatch')


def sx(x, n):
    return (x ^ (1 << (n-1))) - (1 << (n-1))


def walk(b, start, end):
    todo, seen, out = [start], set(), set()
    while todo:
        p = todo.pop()
        if p in seen: continue
        ck(start <= p < end); seen.add(p)
        x = int.from_bytes(b[p-0x40000:p-0x40000+4], 'little'); h = x & 65535
        rd, r, s = x>>7&31, x>>15&31, x>>20&31
        op = x&127; n = p+4; reads = []; writes = []; stop = ''
        if h&3 != 3:
            n = p+2; q = h&3; f = h>>13; u = 8+(h>>7&7); v = 8+(h>>2&7); z = h>>2&31
            if q == 0 and f in (1,2): reads=[u]; writes=[v]
            elif q == 0 and f in (5,6): reads=[u,v]
            elif q == 2 and f == 6: reads=[2,z]
            elif q == 2 and f == 2: reads=[2]; writes=[rd]
            elif q == 1 and f in (0,2,3): reads=[rd] if f==0 or rd==2 else []; writes=[rd]
            elif q == 1 and f == 4: reads=[u]+([v] if h>>10&3==3 else []); writes=[u]
            elif q == 2 and f == 4 and z: reads=[z]+([rd] if h&4096 else []); writes=[rd]
            elif q == 2 and f == 4: reads=[rd]; stop='ret' if h==0x8082 else 'transfer'
            elif q == 1 and f in (6,7):
                reads=[u];d=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5;todo.append(p+sx(d,9))
            elif q == 1 and f in (1,5):
                d=sum((h>>k&1)<<j for k,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)));n=p+sx(d,12)
                if f==1 or not start<=n<end: stop='transfer'
            else: raise ValueError(hex(p))
        elif op in (55,23): writes=[rd]
        elif op in (3,19): reads=[r]; writes=[rd]
        elif op==51: reads=[r,s]; writes=[rd]
        elif op==35: reads=[r,s]
        elif op==99:
            reads=[r,s];d=x>>31<<12|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1;todo.append(p+sx(d,13))
        elif op==111: stop='transfer' # classify all JAL at boundary; no assumption about callees
        elif op==103: reads=[r];stop='transfer'
        elif x==0x100f: pass
        else: raise ValueError(hex(p))
        if 10 in reads: stop='read'
        elif 10 in writes: stop='overwrite'
        if stop: out.add((p,stop))
        else: todo.append(n)
    return sorted(out)


if __name__=='__main__':
    b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    for p,h in [(0x60886,'b70706003737002093876751232cf74e'),(0x58f02,'b797050037370020938727c52328f74e'),(0x5e92e,'b737002083c7072481ebb737002003a5874f8d45ef506e9e'),(0x57d36,'b737002083c7072481ebb737002003a5074f9145efb0fedd'),(0x43b28,'914763e9b700b73700208a059387871cbe9588c18280')]:
        v=bytes.fromhex(h);ck(b[p-0x40000:p-0x40000+len(v)]==v)
    for lo,hi,ow,tr,ret in [(0x60516,0x60856,[0x6061a,0x60734],[0x60596,0x605e0,0x60678,0x606ec,0x60708],0x60752),(0x58c52,0x58ef2,[0x58ca2,0x58cca,0x58dd8],[0x58d3c,0x58d8c,0x58e0a,0x58e4a],0x58e78)]:
        want={(ret,'ret')}|{(p,'overwrite') for p in ow}|{(p,'transfer') for p in tr};ck(set(walk(b,lo,hi))==want)
        m=bytearray(b);m[lo-0x40000:lo-0x40000+2]=bytes.fromhex('aa87') # mv a5,a0
        ck(walk(m,lo,hi)==[(lo,'read')]);print(hex(lo),'PASS:',len(want),'endpoints; incoming-a0 read mutant detected')
