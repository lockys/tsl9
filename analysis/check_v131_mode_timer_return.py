"""Offline V1.31 reference; pass the reference carrier BIN as argv[1]."""
from hashlib import sha256
from pathlib import Path
import sys


def run(b):
    def need(c, msg):
        if not c:
            raise ValueError(msg)

    need(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'carrier identity')
    def fixed(pc, h):
        data = bytes.fromhex(h)
        need(b[pc-0x40000:pc-0x40000+len(data)] == data, hex(pc))

    # Only the instruction windows visited for divisor 1600 and the specified numerator.
    fixed(0x6df1a, 'b687 b288 2a83 2e88 639b0614 63f8c50a 4167 636be61a')
    fixed(0x6e0e2, '1307f00f b286 e37bc7e4 93568600 a147 b1b5')
    fixed(0x6df3e, '17170000 1307e7a1 3697 1823 ba97 13070002 1d8f 19cb 3398e500 b357f500 b318e600 33e80701 3313e500 13d60801 3355c802 93960801 c182 93570301 3377c802 b385a602 4207 3368f700 637ab800')
    fixed(0x6df9c, '3308b840 3357c802 4203 13530301 3378c802 b386e602 4208 33686800 637bd800')
    fixed(0x6dfce, '4205 598d 8145 8280')
    h = int.from_bytes(b[0x2df48:0x2df4a], 'little')
    offset = ((h>>12)&1) | (((h>>10)&3)<<3) | (((h>>5)&3)<<1)
    need((h&3, h>>13, 8+((h>>7)&7), 8+((h>>2)&7), offset) == (0,1,14,14,0), 'conditional Xwchc LBU')
    d = 1600
    address = 0x6df3e + 4096 - 1506 + (d >> 8) + offset
    width = 8 + b[address-0x40000]
    need((address,width) == (0x6e962,11), 'table lookup')
    shift = 32-width
    mask = 0xffffffff
    divisor = (d << shift) & mask
    for u in range(65536):
        n = d*u + 800
        high, low = n >> width, (n << shift) & mask
        q1,r1 = divmod(high, divisor >> 16)
        partial = (r1 << 16) | (low >> 16)
        corr1 = (divisor & 65535)*q1
        need(corr1 <= partial, 'first correction branch')
        q2,r2 = divmod(partial-corr1, divisor >> 16)
        corr2 = (divisor & 65535)*q2
        need(corr2 <= ((r2 << 16) | (low & 65535)), 'second correction branch')
        need(q1 == 0 and ((q1 << 16) | q2) == u, 'return value')
    print('PASS: 5 instruction windows; Xwchc lookup 0x6e962=3; 65536 projections return a1:a0=0:u')


if __name__ == '__main__':
    run(Path(sys.argv[1]).read_bytes())
