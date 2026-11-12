"""Offline byte pins and direct JAL/address arithmetic; no disassembler required."""
from hashlib import sha256
from pathlib import Path

BASE = 0x8000
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS = {
    0x102bc: bytes.fromhex('83 c7 77 00 91 8b a1 c7 93 07 90 08 63 ff 87 02 83 c7 71 13 89 ef 85 47 a3 8b f1 12 ef 70 bf f2 19 c5 01 45 ef a0 bf 92 11 45 ef a0 bf dc 83 c7 51 13 8d e7 85 47 a3 8a f1 12 ef c0 df d5 91 47 63 1e f5 00'),
    0x16266: bytes.fromhex('22 44 b2 40 92 44 02 49 05 45 41 01 6f 40 ff e3'),
    0x16276: bytes.fromhex('22 44 b2 40 92 44 02 49 09 45 41 01 6f 40 ff e2'),
    0x16286: bytes.fromhex('22 44 b2 40 92 44 02 49 11 45 41 01 6f 40 ff e1'),
    0xb0b0: bytes.fromhex('97 17 00 20 a3 8d a7 e2 82 80'),
}
EDGES = ((0x102e6, 1, -21046), (0x16272, 0, -45506),
         (0x16282, 0, -45522), (0x16292, 0, -45538))


def signed(value, bits):
    if bits < 1 or not 0 <= value < (1 << bits):
        raise ValueError('invalid signed field')
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def check_window(data, start, expected, base=BASE):
    offset = start - base
    if offset < 0 or offset + len(expected) > len(data) or data[offset:offset + len(expected)] != expected:
        raise ValueError(f'window mismatch or truncated at {start:#x}')


def decode_jal(raw):
    if len(raw) != 4:
        raise ValueError('truncated JAL')
    w = int.from_bytes(raw, 'little')
    if w & 0x7f != 0x6f:
        raise ValueError('not JAL')
    imm = ((w >> 31) << 20 | ((w >> 12) & 0xff) << 12 |
           ((w >> 20) & 1) << 11 | ((w >> 21) & 0x3ff) << 1)
    return (w >> 7) & 31, signed(imm, 21)


def store_address(pc, raw):
    if len(raw) != 8:
        raise ValueError('invalid AUIPC/SB length')
    auipc = int.from_bytes(raw[:4], 'little')
    sb = int.from_bytes(raw[4:], 'little')
    if auipc & 0xfff != 0x797 or sb & 0x1fff07f != 0xa78023:
        raise ValueError('unexpected AUIPC/SB registers or opcode')
    upper = signed(auipc >> 12, 20) << 12
    displacement = signed(((sb >> 25) << 5) | ((sb >> 7) & 31), 12)
    return (pc + upper + displacement) & 0xffffffff


def verify(data):
    if len(data) != 0x12c00 or sha256(data).hexdigest() != SHA:
        raise ValueError('image length or SHA-256 mismatch')
    for start, expected in WINDOWS.items():
        check_window(data, start, expected)
    for pc, rd, offset in EDGES:
        actual = decode_jal(data[pc - BASE:pc - BASE + 4])
        if actual != (rd, offset) or pc + actual[1] != 0xb0b0:
            raise ValueError(f'edge mismatch at {pc:#x}')
    if store_address(0xb0b0, WINDOWS[0xb0b0][:8]) != 0x2000beeb:
        raise ValueError('store address mismatch')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
    print('image, five windows, four JAL edges and store address verified')
