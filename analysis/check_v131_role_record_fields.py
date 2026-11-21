"""V1.31 candidate/Xwchc, not a hardware trace. Pass the reference carrier path.
The three immediate selectors 4/5/6 are distinct from a0 (registration result).
This leaf writes ID at record+2, then the selector halfword at record+0.
Only these callers are bounded here: the gate narrows to 16 bits but the
address multiplication uses the full subtraction, not the narrowed value.
"""
from hashlib import sha256
from pathlib import Path
import sys


def check(ok):
    if not ok:
        raise ValueError('role record evidence mismatch')


def signed(x, n):
    return (x ^ (1 << (n-1))) - (1 << (n-1))


def main(data):
    check(sha256(data).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    def u(pc, n):
        return int.from_bytes(data[pc-0x40000:pc-0x40000+n], 'little')
    body = data[0xd9ec:0xda18]
    check(body.hex() == '9387c5ff93960701c1820d47636ed7003147b387e7023737002013070732ba97a8a38ea30145828009458280')
    for li, pc, rd, selector in [(0x4a7f2,0x4a7fc,1,4), (0x465ac,0x465b0,0,5), (0x50422,0x50428,1,6)]:
        check(u(li,2) == 0x4581 | selector << 2)
        x = u(pc,4)
        disp = (x>>31)<<20 | (x & 0xff000) | (x>>20 & 1)<<11 | (x>>21 & 1023)<<1
        check(x & 4095 == 111 | rd<<7 and pc + signed(disp,21) == 0x4d9ec)
        idx = selector + signed(u(0x4d9ec,4)>>20,12)
        check((idx & 65535) <= 3)
        base = (u(0x4da02,4) & 0xfffff000) + (u(0x4da06,4)>>20) + idx*(u(0x4d9fc,2)>>2 & 31)
        for task in range(256):
            regs = {10:task, 11:selector, 15:base}
            writes = []
            for site in (0x4da0c,0x4da0e):
                h = u(site,2)
                check(h>>13 == 5 and (h & 3) in (0,2))
                width = 1 + ((h & 3)>>1)
                off = ((h>>5 & 3)<<1) | ((h>>10 & 3)<<3) | ((h>>12 & 1) << (0 if width==1 else 5))
                addr = regs[8+(h>>7 & 7)] + off
                val = regs[8+(h>>2 & 7)] & ((1<<(8*width))-1)
                writes.append((addr,width,val))
            row = (0x20003320,0x2000332c,0x20003338)[selector-4]
            check(writes == [(row+2,1,task),(row,2,selector)])
            check(all(not addr <= p < addr+w for addr,w,_ in writes for p in (0x2000319d,0x200035f5)))
    print('PASS: 3 call edges; 768 ID/selector cases; ordered SB/SH; count and shared ID untouched')


if __name__ == '__main__':
    main(Path(sys.argv[1]).read_bytes())
