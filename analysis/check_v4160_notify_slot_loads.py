"""Check selected producer / consumer operands, not interprocedural data flow."""
from pathlib import Path
import sys
import hashlib
from check_v4160_notify_slot_stores import census

# producer, GP offset, register holding slot address, [(load PC, destination)]
ROWS = (
    (0x1367e,96,15,[(0x13682,15)]),(0x1376c,104,15,[(0x13776,15)]),
    (0x13772,100,15,[(0x13776,15)]),(0x14b08,96,14,[(0x14b10,10)]),
    (0x14be4,104,14,[(0x14bee,10)]),(0x14c10,100,14,[(0x14c1a,10)]),
    (0x167ba,96,19,[(0x167c2,15)]),(0x167e2,100,19,[(0x167ee,14)]),
    (0x167e6,104,20,[(0x16814,14)]),(0x1778a,104,18,[(0x1778e,11),(0x177ba,11)]),
    (0x1799e,100,15,[(0x179a2,14)]),(0x17a00,100,18,[(0x17a04,14),(0x17b28,11),(0x17b70,11)]),
)


def load(w):
    if w&0x707f == 0x2003 and w>>20 == 0:
        return (w>>15)&31,(w>>7)&31
    if w&0xe003 == 0x4000 and w&0x1c60 == 0:
        return 8+((w>>7)&7),8+((w>>2)&7)
    return None


def check(b):
    def word(pc): return int.from_bytes(b[pc-0x8000:pc-0x8000+4],'little')
    if census(b)[1] != [p for p,*_ in ROWS]: raise ValueError('producer coverage')
    seen = set()
    for pc,off,reg,uses in ROWS:
        if word(pc) != (off<<20|3<<15|reg<<7|19): raise ValueError('producer operands')
        for at,dst in uses:
            w = word(at)
            if load(w) != (reg,dst): raise ValueError(hex(at))
            # A store cannot stand in for this load; neither can a nonzero offset.
            for mask in ((0x20,1<<20) if w&3==3 else (0x8000,1<<6)):
                if load(w^mask) == (reg,dst): raise ValueError('mutation accepted')
            seen.add(at)
    return len(seen)


if __name__ == '__main__':
    image = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(image).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('wrong APP')
    print(f'PASS: {len(ROWS)} slot producers; {check(image)} distinct zero-offset word loads; store/offset controls rejected')
