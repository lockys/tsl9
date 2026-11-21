"""Check the two fixed gate writers and the branch on the current gate byte."""
from hashlib import sha256
from pathlib import Path
import sys


def check(ok):
    if not ok:
        raise ValueError('option-8 gate evidence mismatch')


def run(b):
    check(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
    def raw(pc, n):
        return b[pc-0x40000:pc-0x40000+n]
    def u(pc, n=4):
        return int.from_bytes(raw(pc, n), 'little')
    def sx(x, n):
        return (x ^ (1 << (n-1))) - (1 << (n-1))
    def jal(pc, rd):
        x = u(pc)
        check(x & 4095 == (rd << 7 | 111))
        return pc + sx((x >> 31 << 20) | (x & 0xff000) | ((x >> 20 & 1) << 11) | ((x >> 21 & 1023) << 1), 21)
    def bnz(pc):
        h = u(pc, 2)
        check(h & 0xe383 == 0xe381)  # c.bnez a5
        return pc + sx((h >> 12 & 1) << 8 | (h >> 10 & 3) << 3 | (h >> 5 & 3) << 6 | (h >> 3 & 3) << 1 | (h >> 2 & 1) << 5, 9)
    def sb(pc, rs):
        x = u(pc)
        check((x & 0x707f, x >> 15 & 31, x >> 20 & 31) == (35, 15, rs))
        return 0x20003000 + sx(x >> 25 << 5 | (x >> 7 & 31), 12)
    check(jal(0x46582, 1) == 0x6d682 and jal(0x6dd3a, 1) == 0x46570)
    check(u(0x6d6ca) == 0x200037b7 and sb(0x6d6ce, 0) == 0x200035ab)
    check(jal(0x6aece, 1) == 0x6ae4e)
    check(raw(0x6ae56, 16).hex() == 'b737002003c7575f9307f00f630cf700')
    check(raw(0x6ae66, 6).hex() == 'b73700200547' and sb(0x6ae6c, 14) == 0x200035ab)
    check(raw(0x6ae70, 6).hex() == 'b73700203147' and sb(0x6ae76, 14) == 0x200035f4)
    check(u(0x6ae7a, 2) == 0x8082)
    check(raw(0x6aed2, 8) == raw(0x6adb0, 8) == bytes.fromhex('b737002083c7b75a'))
    check(bnz(0x6aedc) == 0x6ae96 and bnz(0x6adb8) == 0x6adec)
    check(raw(0x6ade4, 4).hex() == 'a1450561' and jal(0x6ade8, 0) == 0x49b92)
    check(raw(0x6adec, 8).hex() == 'f240014505618280')
    print('PASS: clear, conditional set, two distinct nonzero exits, option-8 tail')


if __name__ == '__main__':
    run(Path(sys.argv[1]).read_bytes())
