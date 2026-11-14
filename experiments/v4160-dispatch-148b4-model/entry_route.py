"""Bounded original-byte interpreter for command classification at 0x14062.

Stops before connection-state selection or any call; it does not execute firmware.
"""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
EXITS = {0x1408e, 0x140ba, 0x140ec, 0x14122, 0x1417a}


def signed(value, width):
    return value - (1 << width) if value & (1 << (width - 1)) else value


def run(image, command, context, payload, length):
    if not 0 <= command <= 255 or any(not 0 <= x <= MASK for x in (context, payload, length)):
        raise ValueError('invalid synthetic input')
    r = [0] * 32
    r[10], r[11], r[12], r[13] = context, command, payload, length
    pc, trace = 0x14062, []
    for _ in range(30):
        if pc in EXITS:
            return pc, r, trace
        if pc < 0x14062 or pc >= 0x140ec or pc & 1:
            raise ValueError(f'unexpected PC {pc:#x}')
        trace.append(pc)
        off = pc - 0x8000
        h = int.from_bytes(image[off:off + 2], 'little')
        if h & 3 != 3:
            rd, rs2 = (h >> 7) & 31, (h >> 2) & 31
            if (h & 3, h >> 13, (h >> 12) & 1) != (2, 4, 0) or not rd or not rs2:
                raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
            r[rd] = r[rs2]
            pc += 2
        else:
            w = int.from_bytes(image[off:off + 4], 'little')
            op, rd, f3, rs1 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31
            if op == 0x13 and f3 == 0:
                r[rd] = (r[rs1] + signed(w >> 20, 12)) & MASK
                pc += 4
            elif op == 0x63 and f3 in (0, 1, 6):
                rs2 = w >> 20 & 31
                imm = (w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1
                taken = (r[rs1] == r[rs2]) if f3 == 0 else (r[rs1] != r[rs2]) if f3 == 1 else (r[rs1] < r[rs2])
                pc = (pc + signed(imm, 13)) & MASK if taken else pc + 4
            else:
                raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        r[0] = 0
    raise ValueError('instruction budget exceeded')


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    expected_trace = [0x14062, 0x14066, 0x14068, 0x1406a, 0x1406c, 0x14070,
                      0x140a6, 0x140aa, 0x140ae, 0x140dc, 0x140e0, 0x140e4, 0x140e8]
    for length in (0, 1, 20, 514, 1040, MASK):
        pc, r, trace = run(image, 0xc0, 0x87654321, 0x2000b9d8, length)
        if pc != 0x140ba or trace != expected_trace or (r[9], r[8], r[18]) != (0x87654321, 0x2000b9d8, length):
            raise ValueError(f'c0 entry route mismatch for length {length}')
    mutant = bytearray(image)
    mutant[0x14070 - 0x8000] ^= 0x10  # unsigned branch funct3 changes
    try:
        pc, _, trace = run(mutant, 0xc0, 0, 0, 20)
    except ValueError:
        pass
    else:
        if pc == 0x140ba and trace == expected_trace:
            raise ValueError('branch mutation not detected')
    print('PASS: decoded c0 entry route reaches 0x140ba with s1/s0/s2 preserved for six lengths; no calls executed')


if __name__ == '__main__':
    main()
