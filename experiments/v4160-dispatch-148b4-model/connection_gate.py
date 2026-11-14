"""Original-byte projection of the two connection comparisons at 0x140ba.

Loads are supplied halfwords, not physical RAM reads; no concurrency or faults.
"""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
FIRST = 0x2000c79a
SECOND = 0x2000c796


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def run(image, context, first, second):
    if not 0 <= context <= MASK or not 0 <= first <= 65535 or not 0 <= second <= 65535:
        raise ValueError('invalid projection input')
    regs = [0] * 32
    regs[9] = context
    memory = {FIRST: first, SECOND: second}
    pc, reads = 0x140ba, []
    for _ in range(16):
        if pc in (0x141ac, 0x140d8, 0x14c7e):
            return pc, reads
        if not 0x140ba <= pc < 0x140d8 or pc & 1:
            raise ValueError(f'unexpected PC {pc:#x}')
        offset = pc - 0x8000
        h = int.from_bytes(image[offset:offset+2], 'little')
        if h & 3 != 3:
            rd, rs2 = h >> 7 & 31, h >> 2 & 31
            if (h & 3, h >> 13, h >> 12 & 1) != (2, 4, 0) or not rd or not rs2:
                raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
            regs[rd] = regs[rs2]
            pc += 2
        else:
            w = int.from_bytes(image[offset:offset+4], 'little')
            op, rd, f3, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
            if op == 0x17:
                regs[rd] = (pc + (w & 0xfffff000)) & MASK
                pc += 4
            elif op == 0x13 and f3 == 0:
                regs[rd] = (regs[rs1] + signed(w >> 20, 12)) & MASK
                pc += 4
            elif op == 3 and f3 == 5:
                address = (regs[rs1] + signed(w >> 20, 12)) & MASK
                if address not in memory:
                    raise ValueError(f'unexpected read address {address:#x}')
                reads.append(address)
                regs[rd] = memory[address]
                pc += 4
            elif op == 0x63 and f3 in (0, 1):
                imm = (w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1
                equal = regs[rs1] == regs[rs2]
                pc = (pc + signed(imm, 13)) & MASK if (equal if f3 == 0 else not equal) else pc + 4
            else:
                raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        regs[0] = 0
    raise ValueError('instruction limit exceeded')


def main():
    data = IMAGE.read_bytes()
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    cases = 0
    for value in range(65536):
        other = value ^ 1
        for context, first, second, pc, reads in (
            (value, other, value, 0x141ac, [SECOND]),
            (value, value, other, 0x140d8, [SECOND, FIRST]),
            (value, other, other, 0x14c7e, [SECOND, FIRST]),
            (value, value, value, 0x141ac, [SECOND]),
            (value | 0x10000, value, value, 0x14c7e, [SECOND, FIRST]),
        ):
            if run(data, context, first, second) != (pc, reads):
                raise ValueError(f'connection comparison mismatch {context:#x}, {first:#x}, {second:#x}')
            cases += 1
    mutant = bytearray(data)
    mutant[0x140cc - 0x8000] ^= 0x10
    try:
        result = run(mutant, 42, 43, 42)
    except ValueError:
        pass
    else:
        if result == (0x141ac, [SECOND]):
            raise ValueError('first comparison mutation undetected')
    print(f'PASS: {cases} synthetic comparisons; branch 0x141ac tests halfword 0x2000c796 first; no physical RAM reads')


if __name__ == '__main__':
    main()
