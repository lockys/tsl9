"""Replay the caller's status and time branches on the pinned APP. No device IO."""
from check_v4160_poll_sample import B, run as transfer


def need(ok):
    if not ok:
        raise ValueError('caller trace mismatch')


def sx(x, bits):
    return (x ^ (1 << (bits-1))) - (1 << (bits-1))


def gate(pc, a0, base=0):
    r = [0]*32
    r[10], r[9], r[18], r[19] = a0, 2, base, 128
    for _ in range(5):
        if pc in (0x16e58, 0x16e66, 0x16e74): return pc, r[10]
        w = int.from_bytes(B[pc-0x8000:pc-0x8000+4], 'little')
        d, a, b = w >> 7 & 31, w >> 15 & 31, w >> 20 & 31
        if w & 0xfe00707f == 0x40000033: r[d] = (r[a]-r[b]) & 0xffffffff
        elif w & 0x707f == 0x7013: r[d] = r[a] & sx(w >> 20, 12)
        elif w & 0x707f in (0x1063,0x7063):
            off = (w>>31)<<12 | (w>>7&1)<<11 | (w>>25&63)<<5 | (w>>8&15)<<1
            taken = r[a]!=r[b] if w & 0x7000 == 0x1000 else r[a]>=r[b]
            pc += sx(off,13) if taken else 4
            continue
        elif w & 65535 in (0x4501,0x4505): r[10]=(w>>2)&1; pc+=2; continue
        elif w & 65535 == 0xb7c5: return 0x16e66, r[10]  # pinned c.j -32
        else: raise ValueError(hex(pc))
        pc += 4
    raise ValueError('slice budget')


def main():
    for pc, raw in [(0x169c6,'0145 eff0ffec f240 b7170140 4547 23a8e780 0561 8280'),
                    (0x16e4c,'ef104fb6 2a89 8944 93090008 ef108fb5'),
                    (0x16e74,'b945 2285 eff0dfb1'), (0x16e92,'eff0bff7 aa84 31ed'),
                    (0x16ef4,'b240 2244 2685 9244 4101 8280')]:
        fixed = bytes.fromhex(raw)
        need(B[pc-0x8000:pc-0x8000+len(fixed)] == fixed)
    for b in range(256):
        stop, value = gate(0x16e7c,b)
        need((stop,value)==((0x16e66,0) if 128<=b<=159 else (0x16e58,b&224)))
    for tx,rx,data in [(256,1,255),(1,256,255),(1,1,0)]:
        result, *_ = transfer(tx,rx,data)
        need(result==0 and gate(0x16e7c,result)==(0x16e58,0))
    for base in (0,1,0xfffffffe,0xffffffff):
        for diff in (0,1,2,3,0xffffffff):
            stop, value = gate(0x16e5c,(base+diff)&0xffffffff,base)
            need((stop,value)==((0x16e74,diff) if diff<=2 else (0x16e66,1)))
    print('PASS: 256 status bytes; 3 zero origins retry; 20 unsigned time gates')

if __name__=='__main__': main()
