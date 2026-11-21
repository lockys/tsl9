"""v4.1.60: trace the live a0 returned by 0xad94, stopping at its first overwrite.
Usage: python check_v4160_ad94_first_use.py <decoded APP.bin>
Only the normal path prefix is interpreted. RAM samples at successive loads are
independent; stacks are separate, accesses succeed and calls return normally.
The two helpers' early RETs preserve a0, but the caller never consumes it.
"""
from hashlib import sha256
from pathlib import Path
import sys


def check(ok, msg):
    if not ok:
        raise ValueError(msg)


def sign(x, n):
    return (x ^ (1 << (n-1))) - (1 << (n-1))


def trace(b, f, flag, g):
    pc, ra, r = 0xad98, None, {2: 0x2000ff00, 3: 0x20004000}
    # a0 intentionally has no value: reading it before overwrite fails.
    for _ in range(40):
        i = pc - 0x8000
        x = int.from_bytes(b[i:i+4], 'little'); h = x & 65535
        if pc in (0xa688, 0x8440, 0xad9e):
            expected = {0xa688: (4, 0x00000517), 0x8440: (4, 0x16c1c503), 0xad9e: (2, 0x4501)}
            n, v = expected[pc]; check((x if n == 4 else h) == v, 'not the claimed overwrite'); return pc
        if x & 4095 == 0xef:
            d = x>>31<<20 | (x&0xff000) | (x>>20&1)<<11 | (x>>21&1023)<<1
            ra, pc = pc+4, pc+sign(d, 21); continue
        if h & 0xe003 == 0x2001:
            d = sum((h>>k&1)<<j for k,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)))
            ra, pc = pc+2, pc+sign(d,12); continue
        if h == 0x8082:
            pc = ra; continue
        if h & 0xe003 in (0xc001,0xe001):
            d=sum((h>>k&1)<<j for k,j in zip((2,3,4,5,6,10,11,12),(5,1,2,6,7,3,4,8)))
            nz=r[8+(h>>7&7)] != 0; pc += sign(d,9) if nz == bool(h&0x2000) else 2; continue
        if h in (0x439c,0x8bc1,0x8fd9,0x1141,0x4785,0xc606):
            if h==0x439c: check(r[15]==r[3]+84,'pointer slot'); r[15]=0x20008000
            elif h==0x8bc1: r[15] &= 16
            elif h==0x8fd9: r[15] |= r[14]
            elif h==0x1141: r[2]-=16
            elif h==0x4785: r[15]=1
            # c606 saves ra in the separate frame; no reload before stop.
            pc+=2; continue
        op=x&127; rd=x>>7&31; rs=x>>15&31; imm=sign(x>>20,12); fn=x>>12&7
        if op==19 and fn in (0,7): r[rd]=r[rs]+imm if fn==0 else r[rs]&imm
        elif op==23: r[rd]=(pc+(x&0xfffff000))&0xffffffff
        elif op==3 and fn==4:
            addr=r[rs]+imm
            if pc in (0xa66a,0xaa66): check(addr==0x20008004,'record byte');r[rd]=f if pc==0xa66a else g
            elif pc==0xa67c: check(addr==0x2000bed1,'flag address');r[rd]=flag
            else: raise ValueError(hex(pc))
        else: raise ValueError(hex(pc))
        pc+=4
    raise ValueError('prefix did not stop')


def main():
    b=Path(sys.argv[1]).read_bytes();check(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','image')
    check(b[0x2d94:0x2d98]==bytes.fromhex('efe0cfb1'),'cancel call')
    counts={}
    for f in range(256):
        for flag in (0,1,255):
            for g in (0,16):
                pc=trace(b,f,flag,g)
                want=0xa688 if f&6 and not f&32 and flag==0 else (0x8440 if g&16 else 0xad9e)
                check(pc==want,'wrong first use'); counts[pc]=counts.get(pc,0)+1
    print('PASS: 1536 synthetic prefixes; first a0 overwrites:',{hex(k):v for k,v in sorted(counts.items())})

if __name__=='__main__': main()
