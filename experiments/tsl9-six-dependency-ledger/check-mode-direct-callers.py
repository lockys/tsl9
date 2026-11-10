"""Bounded RV32 direct-transfer encoding scan; no target execution."""
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
BASE = 0x8000
RANGES = ((0x8000, 0x14056), (0x14c8a, 0x1a69c), (0x1a6a0, 0x1ac00))
WINDOWS = {
    0xd05c: '97f7ff1f9387c7ed05473306c0402380e700a380a7002381c700a381b7008280',
    0xa21c: '014685450d4541016f209063',
    0xac60: 'a183858b0d458945d5d701466f20003f',
    0xd51c: '81ebb2400546a945154541016ff05fb3',
    0xe1de: 'f5406379f7000546bd450d45efe03fe7',
    0xe6dc: 'efc00fd211c9014685450d45efe05f97',
}
EXPECTED = (0xa224, 0xac6c, 0xd528, 0xe1ea, 0xe6e8)


def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n


def target(data, pc):
    h = int.from_bytes(data[:2], 'little')
    if h & 3 != 3:
        if h & 3 != 1 or h >> 13 not in (1, 5):
            return None
        imm = ((h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 | (h >> 9 & 3) << 8 | (h >> 8 & 1) << 10 | (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 | (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5)
        return (pc + signed(imm, 12)) & 0xffffffff
    if len(data) < 4:
        return None
    w = int.from_bytes(data[:4], 'little')
    if w & 127 != 0x6f:
        return None
    imm = ((w >> 31 & 1) << 20 | (w >> 21 & 1023) << 1 | (w >> 20 & 1) << 11 | (w >> 12 & 255) << 12)
    return (pc + signed(imm, 21)) & 0xffffffff


def verify(read):
    for addr, text in WINDOWS.items():
        if read(addr, len(bytes.fromhex(text))) != bytes.fromhex(text):
            raise ValueError(f'window changed at {addr:#x}')
    hits = []
    for lo, hi in RANGES:
        data = read(lo, hi-lo)
        if len(data) != hi-lo:
            raise ValueError('short read')
        for off in range(0, len(data)-1, 2):
            if target(data[off:off+4], lo+off) == 0xd05c:
                hits.append(lo+off)
    if tuple(hits) != EXPECTED:
        raise ValueError(f'transfer candidates changed: {hits!r}')
    return hits


def main():
    if IMAGE.stat().st_size != 0x12c00:
        raise ValueError('image size changed')
    with IMAGE.open('rb') as f:
        def read(addr, size):
            if not any(lo <= addr and addr+size <= hi for lo, hi in RANGES):
                raise ValueError('excluded read')
            f.seek(addr-BASE)
            return f.read(size)
        print('direct encoding candidates:', ', '.join(hex(x) for x in verify(read)))
    print('No instruction-boundary or reachability claim; target not executed.')


if __name__ == '__main__':
    main()
