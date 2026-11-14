"""Decode post-match state-byte selection; memory reads are synthetic."""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
BASE = 0x2000c794


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def run(image, start, first, second):
    if start not in (0x141ac, 0x140d8) or not 0 <= first <= 255 or not 0 <= second <= 255:
        raise ValueError('invalid input')
    r = [0] * 32
    r[14] = BASE
    memory = {BASE + 4: first, BASE + 8: second}
    pc, reads = start, []
    for _ in range(12):
        if pc in (0x141bc, 0x141d6):
            return pc, reads
        off = pc - 0x8000
        if off < 0 or off + 2 > len(image) or pc & 1:
            raise ValueError(f'invalid PC {pc:#x}')
        h = int.from_bytes(image[off:off+2], 'little')
        if h & 3 != 3:
            q, f3, rd, rs2 = h & 3, h >> 13, h >> 7 & 31, h >> 2 & 31
            if q == 1 and f3 == 2 and rd:  # C.LI
                r[rd] = signed((h >> 2 & 31) | (h >> 12 & 1) << 5, 6) & MASK
                pc += 2
            elif q == 2 and f3 == 0 and rd and not (h >> 12 & 1):  # RV32 C.SLLI
                r[rd] = (r[rd] << (h >> 2 & 31)) & MASK
                pc += 2
            elif q == 2 and f3 == 4 and (h >> 12 & 1) and rd and rs2:  # C.ADD
                r[rd] = (r[rd] + r[rs2]) & MASK
                pc += 2
            elif q == 1 and f3 == 5:  # C.J
                imm = ((h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 | (h >> 9 & 3) << 8 |
                       (h >> 8 & 1) << 10 | (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 |
                       (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5)
                pc = (pc + signed(imm, 12)) & MASK
            elif q == 1 and f3 in (6, 7):  # C.BEQZ/C.BNEZ
                reg = 8 + (h >> 7 & 7)
                imm = ((h >> 12 & 1) << 8 | (h >> 10 & 3) << 3 | (h >> 5 & 3) << 6 |
                       (h >> 3 & 3) << 1 | (h >> 2 & 1) << 5)
                taken = (r[reg] == 0) if f3 == 6 else (r[reg] != 0)
                pc = (pc + signed(imm, 9)) & MASK if taken else pc + 2
            else:
                raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
        else:
            w = int.from_bytes(image[off:off+4], 'little')
            op, rd, f3, rs1 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31
            imm = signed(w >> 20, 12)
            if op == 3 and f3 == 4:  # LBU
                address = (r[rs1] + imm) & MASK
                if address not in memory:
                    raise ValueError(f'unexpected read address {address:#x}')
                reads.append(address)
                r[rd] = memory[address]
            elif op == 0x13 and f3 == 7:  # ANDI
                r[rd] = r[rs1] & (imm & MASK)
            else:
                raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
            pc += 4
        r[0] = 0
    raise ValueError('instruction budget exceeded')


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    for value in range(256):
        for start, first, second, address in ((0x141ac, value, value ^ 255, BASE + 4),
                                              (0x140d8, value ^ 255, value, BASE + 8)):
            expected = 0x141d6 if value else 0x141bc
            if run(image, start, first, second) != (expected, [address]):
                raise ValueError(f'state test mismatch at {start:#x}, value={value}')
    mutant = bytearray(image)
    mutant[0x141ba - 0x8000 + 1] ^= 0x20  # C.BNEZ -> C.BEQZ
    if run(mutant, 0x141ac, 1, 0) == run(image, 0x141ac, 1, 0):
        raise ValueError('branch mutation was not detected')
    print('PASS: 512 synthetic state bytes; selected slot +4 byte chooses 0x141d6 iff nonzero')


if __name__ == '__main__':
    main()
