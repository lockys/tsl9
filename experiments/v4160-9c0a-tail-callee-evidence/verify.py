#!/usr/bin/env python3
"""Offline byte pins and independent RV32 JAL immediate decoding."""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
START = 0x9c0a
WINDOW = bytes.fromhex(
    '011122cc26ca06ceaa842ec61304800873300480eff0a027'
    '13051003eff0a0262685eff08029b2452685eff0e02b'
    'eff0e02773200480f2406244d24405618280')
CALLS = {0x9c1e: 0x18e98, 0x9c26: 0x18e90, 0x9c2c: 0x18ec4,
         0x9c34: 0x18ef2, 0x9c38: 0x18eb6}


def decode_jal(pc, raw):
    if len(raw) != 4:
        raise ValueError('truncated JAL')
    word = int.from_bytes(raw, 'little')
    if word & 0x7f != 0x6f or (word >> 7) & 31 != 1:
        raise ValueError('not JAL ra')
    imm = (((word >> 31) & 1) << 20 | ((word >> 21) & 0x3ff) << 1 |
           ((word >> 20) & 1) << 11 | ((word >> 12) & 0xff) << 12)
    if imm & (1 << 20):
        imm -= 1 << 21
    return (pc + imm) & 0xffffffff


def check_window(image):
    offset = START - BASE
    if image[offset:offset + len(WINDOW)] != WINDOW:
        raise ValueError('window mismatch or truncated image')
    for pc, target in CALLS.items():
        off = pc - BASE
        if decode_jal(pc, image[off:off + 4]) != target:
            raise ValueError(f'JAL target mismatch at {pc:#x}')


def verify(image):
    if len(image) != 76800:
        raise ValueError('image length mismatch')
    if hashlib.sha256(image).hexdigest() != SHA256:
        raise ValueError('image SHA-256 mismatch')
    check_window(image)


def main():
    try:
        verify((pathlib.Path(sys.argv[1]) if len(sys.argv) == 2 else IMAGE).read_bytes())
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    print('OK: image, 0x9c0a..0x9c4a window, five JAL targets')
    return 0


if __name__ == '__main__':
    sys.exit(main())
