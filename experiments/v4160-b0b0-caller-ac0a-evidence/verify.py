#!/usr/bin/env python3
"""Bounded static instruction checks; never execute the firmware."""
import hashlib
from pathlib import Path
import sys

BASE = 0x8000
SIZE = 76800
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
IMAGE = (Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
# Half-open, disjoint ranges. Instructions outside these windows are unknown.
RAW = {
    0x102bc: '83c77700918ba1c79307900863ff870283c7711389ef8547a38bf112ef70bff219c50145efa0bf921145efa0bfdc83c75113',
    0xac0a: '83c7211689e721e50545854591a8',
    0xac6a: '01466f20003f',
    0xd05c: '97f7ff1f9387c7ed05473306c0402380e700a380a7002381c700a381b7008280',
    0xb0b0: '97170020a38da7e28280',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sext(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n


def decode(buf, pc):
    """Decode only the RV32I/C subset used in these selected windows."""
    require(len(buf) >= 2, f'{pc:#x}: truncated halfword')
    h = int.from_bytes(buf[:2], 'little')
    if h & 3 != 3:
        q, f = h & 3, h >> 13
        r, rs = (h >> 7) & 31, 8 + ((h >> 7) & 7)
        imm = sext(((h >> 2) & 31) | ((h >> 12) & 1) << 5, 6)
        if q == 1 and f == 2 and r:
            return 2, ('li', r, imm)
        if q == 1 and f == 4 and ((h >> 10) & 3) == 2:
            return 2, ('andi', rs, rs, imm)
        if q == 1 and f in (6, 7):
            off = (((h >> 12) & 1) << 8 | ((h >> 10) & 3) << 3 |
                   ((h >> 5) & 3) << 6 | ((h >> 3) & 3) << 1 | ((h >> 2) & 1) << 5)
            return 2, ('beq' if f == 6 else 'bne', rs, 0, pc + sext(off, 9))
        if q == 1 and f == 5:
            off = (((h >> 12) & 1) << 11 | ((h >> 11) & 1) << 4 |
                   ((h >> 9) & 3) << 8 | ((h >> 8) & 1) << 10 |
                   ((h >> 7) & 1) << 6 | ((h >> 6) & 1) << 7 |
                   ((h >> 3) & 7) << 1 | ((h >> 2) & 1) << 5)
            return 2, ('jal', 0, pc + sext(off, 12))
        if q == 2 and f == 4 and not (h & 0x1000) and r and ((h >> 2) & 31) == 0:
            return 2, ('jalr', 0, r, 0)
        raise ValueError(f'{pc:#x}: unsupported compressed opcode {h:04x}')
    require(len(buf) >= 4, f'{pc:#x}: truncated word')
    w = int.from_bytes(buf[:4], 'little')
    op, rd, f3, rs1, rs2, f7 = w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, w >> 25
    imm = sext(w >> 20, 12)
    if op == 3 and f3 == 4:
        return 4, ('lbu', rd, rs1, imm)
    if op == 0x23 and f3 == 0:
        return 4, ('sb', rs2, rs1, sext((w >> 25) << 5 | (w >> 7 & 31), 12))
    if op == 0x13 and f3 == 0:
        return 4, ('addi', rd, rs1, imm)
    if op == 0x17:
        return 4, ('auipc', rd, sext(w >> 12, 20) << 12)
    if op == 0x33 and f3 == 0 and f7 == 0x20:
        return 4, ('sub', rd, rs1, rs2)
    if op == 0x63 and f3 in (0, 1, 6, 7):
        off = ((w >> 31) << 12 | ((w >> 7) & 1) << 11 |
               ((w >> 25) & 63) << 5 | ((w >> 8) & 15) << 1)
        return 4, ({0:'beq', 1:'bne', 6:'bltu', 7:'bgeu'}[f3], rs1, rs2, pc + sext(off, 13))
    if op == 0x6f:
        off = ((w >> 31) << 20 | ((w >> 12) & 255) << 12 |
               ((w >> 20) & 1) << 11 | ((w >> 21) & 1023) << 1)
        return 4, ('jal', rd, pc + sext(off, 21))
    raise ValueError(f'{pc:#x}: unsupported opcode {w:08x}')


# Register numbers: zero=0, ra=1, gp=3, s0=8, a0..a5=10..15.
EXPECTED = {
    0x102bc: [
        ('lbu',15,15,7), ('andi',15,15,4), ('beq',15,0,0x1030a),
        ('addi',15,0,137), ('bgeu',15,8,0x10306), ('lbu',15,3,311),
        ('bne',15,0,0x102ea), ('li',15,1), ('sb',15,3,311),
        ('jal',1,0x8202), ('beq',10,0,0x102ea), ('li',10,0),
        ('jal',1,0xac0a), ('li',10,4), ('jal',1,0xb0b0), ('lbu',15,3,309)],
    0xac0a: [('lbu',15,3,354), ('bne',15,0,0xac18), ('bne',10,0,0xac58),
             ('li',10,1), ('li',11,1), ('jal',0,0xac6a)],
    0xac6a: [('li',12,0), ('jal',0,0xd05c)],
    0xd05c: [('auipc',15,0x1ffff000), ('addi',15,15,-292), ('li',14,1),
             ('sub',12,0,12), ('sb',14,15,0), ('sb',10,15,1),
             ('sb',12,15,2), ('sb',11,15,3), ('jalr',0,1,0)],
    0xb0b0: [('auipc',15,0x20001000), ('sb',10,15,-453), ('jalr',0,1,0)],
}


def check_semantics(windows):
    """Check all decoded instructions and exact boundaries without any hash/raw pin."""
    require(set(windows) == set(EXPECTED), 'missing or extra window')
    for start, instructions in EXPECTED.items():
        data = windows[start]
        pos = 0
        for expected in instructions:
            size, actual = decode(data[pos:], start + pos)
            require(actual == expected, f'{start + pos:#x}: {actual!r} != {expected!r}')
            pos += size
        require(pos == len(data), f'{start:#x}: extra or missing bytes')


def extract(image):
    windows = {}
    for start, hexbytes in RAW.items():
        length = len(bytes.fromhex(hexbytes))
        off = start - BASE
        require(off >= 0 and off + length <= len(image), f'{start:#x}: truncated image')
        windows[start] = image[off:off + length]
    return windows


def verify(image):
    require(len(image) == SIZE, 'wrong image length')
    require(hashlib.sha256(image).hexdigest() == SHA256, 'wrong image SHA-256')
    windows = extract(image)
    check_semantics(windows)
    for start, hexbytes in RAW.items():
        require(windows[start] == bytes.fromhex(hexbytes), f'{start:#x}: raw mismatch')
    return windows


def main():
    try:
        verify(IMAGE.read_bytes())
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    print('OK: pinned image and bounded decoded instructions')
    return 0


if __name__ == '__main__':
    sys.exit(main())
