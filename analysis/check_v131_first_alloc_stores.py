"""First 16-byte timer allocation: CPU store destinations before return.
Run with the V1.31 reference carrier. This is a store projection, not a CPU:
assume the nominal first free header (504 bytes), Xwchc, intact pointers,
and scheduler entry SP E. Only the successful first-header split is selected.
MMIO side effects and installed ROM are unknown. Addresses below use the
low offset of the copied routine at 0x20000000 (carrier file offset 0x270).
"""
import hashlib
import sys
from pathlib import Path


def ck(v):
    if not v: raise ValueError('first allocation store projection mismatch')


def store(x, n):
    # (base register, offset, width); standard SW/SH and compressed forms.
    if n == 4 and x & 127 == 35:
        k = x >> 12 & 7; ck(k in (1, 2))
        d = (x >> 25 << 5) | (x >> 7 & 31)
        return (x >> 15 & 31, (d ^ 2048)-2048, 1 << k)
    k = x & 0xe003
    if n == 2 and k == 0xc002: return (2, 4*(x>>9&15)+64*(x>>7&3), 4)
    if n == 2 and k == 0xc000: return (8+(x>>7&7), 8*(x>>10&7)+4*(x>>6&1)+64*(x>>5&1), 4)
    if n == 2 and k == 0xa002: return (8+(x>>7&7), 8*(x>>10&7)+2*(x>>5&3), 2)
    return None


def verify(b):
    ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    e,h=0x2000ffc0,0x200043ac
    p=h+8; tail=p+16; g=0x2000319c; mm=0x40024000
    bases={2:e-48-16,10:h,12:tail,13:g,15:mm}
    trace=[]
    for lo,hi in ((0x40,0x5a),(0x66,0x90),(0xae,0x10c)):
        pc=lo
        while pc<hi:
            i=0x270+pc; n=4 if b[i]&3==3 else 2
            s=store(int.from_bytes(b[i:i+n],'little'),n)
            if s:
                reg,d,w=s; trace.append((pc,bases[reg]+d,w))
            pc+=n
        ck(pc==hi)
    ck(trace==[(0x42,e-56,4),(0x48,e-52,4),(0x4e,mm+524,4),(0xdc,tail+4,2),(0xde,tail,4),(0xe2,tail+6,2),(0xe6,h,4),(0xe8,h+4,2),(0xee,g+6,2),(0xf0,h+6,2),(0xfa,g+6,2),(0x100,mm+524,4)])
    for _,a,w in trace:
        ck(all(a+w<=l or r<=a for l,r in ((p,tail),(e-8,e))))
    ck(b[0x270+0x104:0x270+0x10c].hex()=='b240224441018280')
    print('PASS: 12 stores = 6 header + 2 accounting + 2 frame + 2 MMIO; payload and caller s0/ra untouched; frame-slot gap 40 bytes')


if __name__=='__main__': verify(Path(sys.argv[1]).read_bytes())
