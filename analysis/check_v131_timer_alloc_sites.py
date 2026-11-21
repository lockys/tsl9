"""Check selected V1.31 timer call sites in an external reference carrier."""
from hashlib import sha256
from pathlib import Path
import sys


def check(b):
    def require(ok, label):
        if not ok:
            raise ValueError(label)

    require(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'reference identity')

    def data(pc, n):
        return b[pc-0x40000:pc-0x40000+n]

    def fixed(pc, h):
        raw = bytes.fromhex(h)
        require(data(pc, len(raw)) == raw, hex(pc))

    for pc in (0x43492, 0x4382a):
        fixed(pc-2, '4145')  # c.li a0,16
        hi = int.from_bytes(data(pc, 4), 'little')
        lo = int.from_bytes(data(pc+4, 4), 'little')
        require(hi & 4095 == 0x97 and lo & 0xfffff == 0x080e7, 'auipc/jalr ra')
        disp = int.from_bytes(lo.to_bytes(4, 'little'), 'little', signed=True) >> 20
        require(((pc + (hi & 0xfffff000) + disp) & 0xfffffffe) == 0x20000040, 'target')
    fixed(0x4348a, 'c165938505f0')
    fixed(0x43820, '936504f0c205c181')
    fixed(0x402c6, '11c199e5')  # copied RAM +0x56
    fixed(0x402d6, '93073500c207c183f19bc207c183130740036366f7023737002003254719373700208326c7186391a602')
    for s in range(65536):
        require(((s | -256) & 65535) == 0xff00 + (s & 255), 'tag')
    print('PASS: both size-16 calls target 0x20000040; 65536 low-half tag projections; small-request cursor and sentinel loads pinned')


if __name__ == '__main__':
    check(Path(sys.argv[1]).read_bytes())
