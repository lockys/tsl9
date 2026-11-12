"""固定原始 BIN 的有界窗口與表格算術；不執行 target。"""
from hashlib import sha256
from pathlib import Path

BASE = 0x8000
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
LENGTH = 0x12c00
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'

# 已存證的原始 bytes；不從輸入產生預期值。
WINDOWS = {
    0x155d0: bytes.fromhex(
        '411126c2938441059c4006c622c483c747004ac0a18b81cb93076500'
        '93f7f70f0947636df71883c7611691cb2244b2409244024923830116'
        '41016f2070301309f5ff1377f90f9d472a8463ebe700814651468145'
        '17050000130565f0ef309faf1379f90f9307c00f63ea271517570000'
        '1307870b0a093a9983270900ba978287'),
    0x16266: bytes.fromhex(
        '2244b24092440249054541016f40ffe3'
        '2244b24092440249094541016f40ffe2'
        '2244b24092440249114541016f40ffe1'),
    0xb0b0: bytes.fromhex('97170020a38da7e28280'),
    0x1a9f4: bytes.fromhex('72bbffff82bbffff92bbffff'),
}


def read_at(data, pc, size):
    off = pc - BASE
    if off < 0 or size < 0 or off + size > len(data):
        raise ValueError(f'address out of image: {pc:#x} size {size}')
    return data[off:off + size]


def check_window(data, pc, expected):
    if read_at(data, pc, len(expected)) != expected:
        raise ValueError(f'window mismatch: {pc:#x}')


def check_windows(data):
    for pc, expected in WINDOWS.items():
        check_window(data, pc, expected)


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def table_base(data, pc=0x1563c):
    """Decode only AUIPC a4 and ADDI a4,a4; AUIPC uses its own PC."""
    auipc = int.from_bytes(read_at(data, pc, 4), 'little')
    addi = int.from_bytes(read_at(data, pc + 4, 4), 'little')
    if auipc & 0xfff != 0x717 or addi & 0xfffff != 0x70713:
        raise ValueError('unexpected AUIPC/ADDI opcode or registers')
    upper = signed(auipc >> 12, 20)
    lower = signed(addi >> 20, 12)
    result = (pc + (upper << 12) + lower) & 0xffffffff
    if pc != 0x1563c or upper != 5 or lower != 184 or result != 0x1a6f4:
        raise ValueError('unexpected AUIPC/ADDI address or immediate')
    return result


def check_math(data, pc=0x1563c):
    base = table_base(data, pc)
    for selector, entry, displacement, target in (
        (0xc1, 0x1a9f4, -0x448e, 0x16266),
        (0xc2, 0x1a9f8, -0x447e, 0x16276),
        (0xc3, 0x1a9fc, -0x446e, 0x16286),
    ):
        address = base + 4 * ((selector - 1) & 0xff)
        if address != entry:
            raise ValueError('unexpected table entry address')
        value = int.from_bytes(read_at(data, address, 4), 'little', signed=True)
        if value != displacement or ((base + value) & 0xfffffffe) != target:
            raise ValueError(f'unexpected dispatch for {selector:#x}')


def verify(data):
    if len(data) != LENGTH or sha256(data).hexdigest() != SHA:
        raise ValueError('image length or SHA-256 mismatch')
    check_windows(data)
    check_math(data)


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
    print('fixed image, register evidence windows and table arithmetic verified')
