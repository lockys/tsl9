"""Check entry register moves and three direct call destinations in pinned BIN.

This deliberately does not interpret intervening control flow or callees.
"""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def read_at(data, pc, size):
    return int.from_bytes(data[pc - 0x8000:pc - 0x8000 + size], 'little')


def decode_mv(h):
    if (h & 3, h >> 13, (h >> 12) & 1) != (2, 4, 0):
        raise ValueError('expected C.MV')
    rd, rs2 = (h >> 7) & 31, (h >> 2) & 31
    if not rd or not rs2:
        raise ValueError('invalid C.MV operands')
    return rd, rs2


def jal_target(pc, w):
    if (w & 127, (w >> 7) & 31) != (0x6f, 1):
        raise ValueError('expected JAL ra')
    imm = ((w >> 31 & 1) << 20 | (w >> 21 & 1023) << 1 |
           (w >> 20 & 1) << 11 | (w >> 12 & 255) << 12)
    if imm & (1 << 20):
        imm -= 1 << 21
    return (pc + imm) & 0xffffffff


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    for pc, expected in ((0x14066, (9, 10)), (0x14068, (8, 12)), (0x1406a, (18, 13))):
        if decode_mv(read_at(image, pc, 2)) != expected:
            raise ValueError(f'entry move mismatch at {pc:#x}')
    for pc, target in ((0x14240, 0x81aa), (0x147f8, 0x13ba6), (0x147fc, 0x1070a)):
        if jal_target(pc, read_at(image, pc, 4)) != target:
            raise ValueError(f'direct call mismatch at {pc:#x}')
    if decode_mv(read_at(image, 0x1406a, 2) ^ (1 << 2)) == (18, 13):
        raise ValueError('move mutation not detected')
    if jal_target(0x14240, read_at(image, 0x14240, 4) ^ (1 << 21)) == 0x81aa:
        raise ValueError('call mutation not detected')
    print('PASS: entry s1=a0, s0=a2, s2=a3 and three direct call targets decoded; intervening path/callees not executed')


if __name__ == '__main__':
    main()
