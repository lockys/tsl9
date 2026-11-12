"""Pinned offline RV32 guard evidence; no target execution."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[2]
IMAGES = (
    ('reference', 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
     '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'),
    ('candidate', 'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin',
     '28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89'),
)
BASE = 0x8000
PREFIX = bytes.fromhex('03d761092a893684b284ae89')
WINDOW = {'reference': bytes.fromhex('6310a702c167f917630cf700'),
          'candidate': bytes.fromhex('6310a702c167f917638ca700')}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def branch(raw, pc):
    require(len(raw) == 4, 'branch length')
    w = int.from_bytes(raw, 'little')
    require(w & 127 == 0x63, 'branch opcode')
    imm = (((w >> 31) & 1) << 12 | ((w >> 7) & 1) << 11 |
           ((w >> 25) & 63) << 5 | ((w >> 8) & 15) << 1)
    imm = signed(imm, 13)
    return (w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, imm, pc + imm)


def check_branch(raw, pc, expected):
    require(branch(raw, pc) == expected, 'branch fields or displacement')


def check_window(prefix, window, kind):
    require(kind in WINDOW, 'unknown image')
    require(len(prefix) == 12 and len(window) == 12, 'window length')
    w = int.from_bytes(prefix[:4], 'little')
    require((w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31,
             signed(w >> 20, 12)) == (3, 14, 5, 3, 150), 'LHU fields')
    check_branch(window[:4], 0x8a76, (1, 14, 10, 32, 0x8a96))
    expected = (0, 14, 15, 24, 0x8a96) if kind == 'reference' else (0, 15, 10, 24, 0x8a96)
    check_branch(window[8:], 0x8a7e, expected)
    lui = int.from_bytes(window[4:6], 'little')
    addi = int.from_bytes(window[6:8], 'little')
    lui_imm = signed(((lui >> 12 & 1) << 5) | (lui >> 2 & 31), 6)
    addi_imm = signed(((addi >> 12 & 1) << 5) | (addi >> 2 & 31), 6)
    require((lui & 3, lui >> 13, lui >> 7 & 31, lui_imm) == (1, 3, 15, 16), 'C.LUI')
    require((addi & 3, addi >> 13, addi >> 7 & 31, addi_imm) == (1, 0, 15, -2), 'C.ADDI')
    require(((lui_imm << 12) + addi_imm) & 0xffffffff == 0xfffe, 'a5 constant')
    require(prefix == PREFIX and window == WINDOW[kind], 'physical bytes')


def check_image(data, kind, digest):
    require(len(data) == 76800 and hashlib.sha256(data).hexdigest() == digest, 'image identity')
    check_window(data[0x8a6a-BASE:0x8a76-BASE], data[0x8a76-BASE:0x8a82-BASE], kind)


def check_domain(a4, a0, fallthrough):
    for v in (a4, a0):
        require(type(v) is int and 0 <= v <= 0xffffffff, 'not a 32-bit value')
    require(fallthrough is True and a4 == a0, 'fallthrough premise absent')
    return True


def main():
    for kind, path, digest in IMAGES:
        check_image((ROOT / path).read_bytes(), kind, digest)
        print(kind + ': SHA-256, prefix and branch decoding verified')


if __name__ == '__main__':
    main()
