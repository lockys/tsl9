"""固定映像的局部 byte windows 與表格位址算術；不執行 target。"""
from hashlib import sha256
from pathlib import Path

BASE = 0x8000
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS = {
    0x155d0: bytes.fromhex('411126c2938441059c4006c622c483c747004ac0a18b81cb9307650093f7f70f0947636df71883c7611691cb2244b240924402492383011641016f2070301309f5ff1377f90f9d472a8463ebe70081465146814517050000130565f0ef309faf1379f90f9307c00f63ea2715175700001307870b0a093a9983270900ba978287'),
    0x1a9f4: bytes.fromhex('72bbffff82bbffff92bbffff'),
    0x16266: bytes.fromhex('2244b24092440249054541016f40ffe32244b24092440249094541016f40ffe22244b24092440249114541016f40ffe1'),
}


def check_windows(data):
    for pc, expected in WINDOWS.items():
        off = pc - BASE
        if off < 0 or off + len(expected) > len(data) or data[off:off + len(expected)] != expected:
            raise ValueError(f'window mismatch or truncated: {pc:#x}')


def check_math(data):
    # Decode the specific AUIPC a4 / ADDI a4,a4 pair, including signed immediates.
    off = 0x1563c - BASE
    auipc = int.from_bytes(data[off:off + 4], 'little')
    addi = int.from_bytes(data[off + 4:off + 8], 'little')
    if auipc & 0xfff != 0x717 or addi & 0xfffff != 0x70713:
        raise ValueError('unexpected table-base instructions')
    upper = auipc >> 12
    upper = upper - (1 << 20) if upper & (1 << 19) else upper
    low = addi >> 20
    low = low - 4096 if low & 0x800 else low
    base = (0x1563c + (upper << 12) + low) & 0xffffffff
    if base != 0x1a6f4:
        raise ValueError('unexpected table base')
    for value, target in ((0xc1, 0x16266), (0xc2, 0x16276), (0xc3, 0x16286)):
        index = (value - 1) & 0xff
        address = base + 4 * index
        off = address - BASE
        raw = data[off:off + 4]
        if len(raw) != 4:
            raise ValueError('truncated table')
        displacement = int.from_bytes(raw, 'little', signed=True)
        if (base + displacement) & 0xfffffffe != target:
            raise ValueError(f'wrong dispatch for {value:#x}')


def verify(data):
    if len(data) != 0x12c00 or sha256(data).hexdigest() != SHA:
        raise ValueError('image length or SHA-256 mismatch')
    check_windows(data)
    check_math(data)


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
    print('fixed image, dispatch windows and table arithmetic verified')
