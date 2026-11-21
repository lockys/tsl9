"""Census of literal LW/C.LW displacements, not a complete indirect-call graph."""
from hashlib import sha256
from pathlib import Path
import sys


def check(b):
    def need(x):
        if not x:
            raise ValueError('APP identity or instruction evidence mismatch')
    need(sha256(b).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    def r(p,n): return int.from_bytes(b[p-0x8000:p-0x8000+n], 'little')
    hits = {84: [], 92: []}
    for i in range(0,len(b)-1,2):
        p = 0x8000+i; h = r(p,2)
        if h & 0xe003 == 0x4000:
            d = (h>>7 & 56) | (h>>4 & 4) | (h<<1 & 64)
        elif i+4 <= len(b) and r(p,4) & 0x707f == 0x2003:
            d = r(p,4)>>20
        else: continue
        if d in hits: hits[d].append(p)
    need(hits[84] == [0xe014] and hits[92] == [0x9106,0xa76a,0xb51c,0xb7c4,0xe192,0x10fdc,0x11850,0x121ac,0x122be,0x1688c,0x17368,0x173f2])
    for p in [0xe014,0xa76a,0xb51c,0xb7c4,0xe192]: need(r(p-2,4)&127 == 111)
    for p,k in [(0x10fe0,16),(0x11854,16),(0x121ae,1),(0x122c0,2),(0x1736a,1),(0x173fc,2)]: need(r(p,2)==0x4581+(k<<2))
    need(r(0x90f2,4)==0x0a61c503 and r(0x90e8,4)==0x008595b3)
    need(r(0x1686c,4)==0x16b1c783 and r(0x16888,4)==0xff855583 and r(0x16890,2)==0x853e)
    need(r(0x1685a,4)==0x000207b7 and r(0x16860,2)==0x4791)
    print('PASS: clear 1 encoding inside JAL; stop 12 encodings: 4 inside JAL, 6 other masks, 2 conditional mask-4 sites (gp+166/+363)')


if __name__ == '__main__': check(Path(sys.argv[1]).read_bytes())
