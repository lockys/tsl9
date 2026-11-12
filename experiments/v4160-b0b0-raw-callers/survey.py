#!/usr/bin/env python3
"""Raw, overlapping RISC-V jump bit patterns; not a disassembler."""
import hashlib
from pathlib import Path

BASE = 0x8000
TARGET = 0xB0B0
SIZE = 0x12C00
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOW = bytes.fromhex('97170020a38da7e28280')  # [0xb0b0, 0xb0ba)
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def decode_jal(word):
    if word & 0x7f != 0x6f:
        return None
    imm = ((word >> 31) << 20 | ((word >> 12) & 0xff) << 12 |
           ((word >> 20) & 1) << 11 | ((word >> 21) & 0x3ff) << 1)
    return (word >> 7) & 31, signed(imm, 21)


def decode_c(half):
    subtype = half >> 13
    if half & 3 != 1 or subtype not in (1, 5):
        return None
    imm = (((half >> 12) & 1) << 11 | ((half >> 11) & 1) << 4 |
           ((half >> 9) & 3) << 8 | ((half >> 8) & 1) << 10 |
           ((half >> 7) & 1) << 6 | ((half >> 6) & 1) << 7 |
           ((half >> 3) & 7) << 1 | ((half >> 2) & 1) << 5)
    return ('C.JAL' if subtype == 1 else 'C.J'), signed(imm, 12)


def scan(data, base=BASE, target=TARGET):
    if base & 1:
        raise ValueError('base must be 2-byte aligned')
    for off in range(0, len(data) - 1, 2):
        pc = base + off
        half = int.from_bytes(data[off:off + 2], 'little')
        c = decode_c(half)
        if c is not None and pc + c[1] == target:
            yield pc, data[off:off + 2].hex(), c[0], c[1]
        if off + 4 <= len(data):
            j = decode_jal(int.from_bytes(data[off:off + 4], 'little'))
            if j is not None and pc + j[1] == target:
                yield pc, data[off:off + 4].hex(), f'JAL rd=x{j[0]}', j[1]


def validate(data):
    if len(data) != SIZE:
        raise ValueError('image length mismatch')
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('image SHA-256 mismatch')
    if data[TARGET - BASE:TARGET - BASE + len(WINDOW)] != WINDOW:
        raise ValueError('b0b0 window mismatch')


def main():
    data = IMAGE.read_bytes()
    validate(data)
    print(f'image sha256={SHA256} range=[0x{BASE:x},0x{BASE + len(data):x})')
    print(f'window [0xb0b0,0xb0ba)={WINDOW.hex()}')
    for pc, raw, kind, displacement in scan(data):
        print(f'0x{pc:05x}  {raw}  {kind}  displacement={displacement:+d}  target=0x{TARGET:x}')


if __name__ == '__main__':
    main()
