"""Bounded original-byte interpreter for leaf 0x13ba6; memory is synthetic."""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
FIRST, SECOND = 0x2000c796, 0x2000c79a


def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n


def run(image, handle, value, first, second):
    if not 0 <= handle <= MASK or not 0 <= value <= MASK or not 0 <= first <= 65535 or not 0 <= second <= 65535:
        raise ValueError('invalid input')
    r = [0] * 32
    r[1], r[2], r[10], r[11] = 0x12345678, 0x20001000, handle, value
    memory = {FIRST: first, SECOND: second}
    pc, reads, writes = 0x13ba6, [], []
    for _ in range(20):
        if pc == 0x12345678:
            return reads, writes, (r[1], r[2], r[10], r[11])
        if not 0x13ba6 <= pc < 0x13bd2 or pc & 1:
            raise ValueError(f'unexpected PC {pc:#x}')
        offset = pc - 0x8000
        h = int.from_bytes(image[offset:offset + 2], 'little')
        if h & 3 != 3:
            # Strictly bounded subset: exact compressed operations in this leaf.
            if h == 0x4705: r[14] = 1
            elif h == 0x4701: r[14] = 0
            elif h == 0x070a: r[14] = (r[14] << 2) & MASK
            elif h == 0x97ba: r[15] = (r[15] + r[14]) & MASK
            elif h == 0x8082:
                pc = r[1] & ~1
                continue
            elif h == 0xbfd5:
                pc = 0x13bc4
                continue
            else: raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
            pc += 2
        else:
            w = int.from_bytes(image[offset:offset + 4], 'little')
            op, rd, f3, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
            if op == 0x17:
                r[rd] = (pc + (w & 0xfffff000)) & MASK
                pc += 4
            elif op == 0x13 and f3 == 0:
                r[rd] = (r[rs1] + signed(w >> 20, 12)) & MASK
                pc += 4
            elif op == 3 and f3 == 5:
                address = (r[rs1] + signed(w >> 20, 12)) & MASK
                if address not in memory: raise ValueError(f'unexpected read {address:#x}')
                reads.append(address)
                r[rd] = memory[address]
                pc += 4
            elif op == 0x23 and f3 == 0:
                imm = (w >> 25 << 5) | (w >> 7 & 31)
                address = (r[rs1] + signed(imm, 12)) & MASK
                writes.append((address, r[rs2] & 255))
                pc += 4
            elif op == 0x63 and f3 in (0, 1):
                imm = (w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1
                eq = r[rs1] == r[rs2]
                pc = (pc + signed(imm, 13)) & MASK if (eq if f3 == 0 else not eq) else pc + 4
            else: raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        r[0] = 0
    raise ValueError('instruction budget exceeded')


def main():
    data = IMAGE.read_bytes()
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    count = 0
    for v in range(65536):
        for handle, first, second, reads, writes in (
            (v, v, v ^ 1, [FIRST], [(0x2000c799, 2)]),
            (v, v ^ 1, v, [FIRST, SECOND], [(0x2000c79d, 2)]),
            (v, v ^ 1, v ^ 1, [FIRST, SECOND], []),
            (v, v, v, [FIRST], [(0x2000c799, 2)]),
            (v | 0x10000, v, v, [FIRST, SECOND], []),
        ):
            if run(data, handle, 2, first, second) != (reads, writes, (0x12345678, 0x20001000, handle, 2)):
                raise ValueError(f'leaf mismatch {handle:#x}, {first:#x}, {second:#x}')
            count += 1
    for value in (0, 1, 255, 256, MASK):
        if run(data, 5, value, 5, 5)[1] != [(0x2000c799, value & 255)]:
            raise ValueError('store truncation mismatch')
    altered = bytearray(data)
    altered[0x13bb6 - 0x8000 + 1] ^= 0x10
    try: result = run(altered, 5, 2, 5, 5)
    except ValueError: pass
    else:
        if result[1] == [(0x2000c799, 2)]: raise ValueError('branch mutation missed')
    print(f'PASS: {count} synthetic leaf cases; match priority, byte store and a0/a1 preservation; no physical RAM')


if __name__ == '__main__': main()
