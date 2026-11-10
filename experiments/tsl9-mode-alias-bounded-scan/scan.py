"""Raw halfword-aligned syntactic candidates, not a dataflow or reachability analysis."""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE, END, MODE = 0x8000, 0x1ac00, 0x2000bf39
RANGES = ((0x8000, 0x14056), (0x14c8a, 0x1a69c), (0x1a6a0, END))


def signed(x, bits):
    return x - (1 << bits) if x & (1 << (bits - 1)) else x


def scan(data):
    """LUI/AUIPC + optional adjacent ADDI + store within 16 bytes of producer.

    Also report ADDI-produced pointers within 3 bytes below mode. No claim is
    made about intervening instructions, control flow, or valid boundaries.
    """
    if len(data) != END - BASE:
        raise ValueError('image length')
    pointers, stores = [], []
    for lo, hi in RANGES:
        for pc in range(lo, hi - 3, 2):
            w = int.from_bytes(data[pc-BASE:pc-BASE+4], 'little')
            op, rd = w & 127, (w >> 7) & 31
            if op not in (0x17, 0x37) or rd == 0:
                continue
            value = ((pc if op == 0x17 else 0) + (w & 0xfffff000)) & 0xffffffff
            origins = [(pc, value)]
            if pc + 8 <= hi:
                a = int.from_bytes(data[pc-BASE+4:pc-BASE+8], 'little')
                if a & 0x707f == 0x13 and (a >> 15) & 31 == rd and (a >> 7) & 31 == rd:
                    v = (value + signed(a >> 20, 12)) & 0xffffffff
                    origins.append((pc + 4, v))
                    if MODE - 3 <= v <= MODE:
                        pointers.append((pc, pc + 4, rd, v))
            for origin, v in origins:
                for pos in range(origin + 4, min(origin + 17, hi - 1), 2):
                    h = int.from_bytes(data[pos-BASE:pos-BASE+2], 'little')
                    size = offset = base = None
                    if h & 3 == 3 and pos + 4 <= hi:
                        s = int.from_bytes(data[pos-BASE:pos-BASE+4], 'little')
                        f = (s >> 12) & 7
                        if s & 127 == 0x23 and f in (0, 1, 2):
                            size, base = 1 << f, (s >> 15) & 31
                            offset = signed(((s >> 25) << 5) | ((s >> 7) & 31), 12)
                    elif h & 3 == 0 and h >> 13 == 6:  # C.SW
                        size, base = 4, 8 + ((h >> 7) & 7)
                        offset = ((h >> 10) & 7) * 8 + ((h >> 6) & 1) * 4 + ((h >> 5) & 1) * 64
                    if base == rd and ((v + offset) & 0xffffffff) <= MODE < ((v + offset) & 0xffffffff) + size:
                        stores.append((pc, origin, pos, rd, (v + offset) & 0xffffffff, size))
    return sorted(set(pointers)), sorted(set(stores))


def verified(data):
    if len(data) != END - BASE or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('firmware size or SHA-256 mismatch')
    return scan(data)


if __name__ == '__main__':
    p, s = verified(IMAGE.read_bytes())
    print('pointer candidates:', *(tuple(hex(x) for x in row) for row in p), sep='\n')
    print('overlapping store candidates:', *(tuple(hex(x) for x in row) for row in s), sep='\n')
    print('Raw syntactic pairs only; no code boundary or dataflow claim.')
