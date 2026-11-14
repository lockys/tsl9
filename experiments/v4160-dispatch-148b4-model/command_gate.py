"""Project c0 classification through the 0x81aa call boundary.

A returning callee result is supplied by the test, not executed or identified.
"""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def run(image, result, sp):
    if not 0 <= result <= MASK or not 0 <= sp <= MASK:
        raise ValueError('invalid input')
    r = [0] * 32
    r[2], r[11] = sp, 0xc0
    pc, trace, stores, call_count = 0x141d6, [], {}, 0
    for _ in range(30):
        if pc in (0x14248, 0x143ca):
            return pc, r, trace, stores, call_count
        off = pc - 0x8000
        if off < 0 or off + 2 > len(image) or pc & 1:
            raise ValueError(f'invalid PC {pc:#x}')
        trace.append(pc)
        h = int.from_bytes(image[off:off+2], 'little')
        if h & 3 != 3:
            q, f3, rd, rs2 = h & 3, h >> 13, h >> 7 & 31, h >> 2 & 31
            if q == 2 and f3 == 6:  # C.SWSP
                imm = ((h >> 9 & 15) << 2) | ((h >> 7 & 3) << 6)
                stores[(sp + imm) & MASK] = r[rs2]
                pc += 2
            elif q == 2 and f3 == 2 and rd:  # C.LWSP
                imm = ((h >> 12 & 1) << 5) | ((h >> 4 & 7) << 2) | ((h >> 2 & 3) << 6)
                addr = (sp + imm) & MASK
                if addr not in stores: raise ValueError('uninitialized synthetic stack read')
                r[rd] = stores[addr]
                pc += 2
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
            op, rd, f3, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
            if op == 0x13 and f3 == 0:
                r[rd] = (r[rs1] + signed(w >> 20, 12)) & MASK
                pc += 4
            elif op == 0x63 and f3 in (0, 1, 6, 7):
                imm = (w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1
                taken = ((r[rs1] == r[rs2]) if f3 == 0 else (r[rs1] != r[rs2]) if f3 == 1
                         else (r[rs1] < r[rs2]) if f3 == 6 else (r[rs1] >= r[rs2]))
                pc = (pc + signed(imm, 13)) & MASK if taken else pc + 4
            elif pc == 0x14240 and w == 0xf6bf30ef:
                # Provider stub: assumption of a normal return, with only a0 modified.
                call_count += 1
                r[10] = result
                pc += 4
            else:
                raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        r[0] = 0
    raise ValueError('instruction budget exceeded')


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    prefix = [0x141d6, 0x141da, 0x141de, 0x1425e, 0x14262, 0x14266,
              0x1426a, 0x1423e, 0x14240, 0x14244, 0x14246]
    for sp in (0, 0x20000000, 0xfffffff8):
        for result in (0, 1, 2, 0x80000000, MASK):
            pc, regs, trace, stores, count = run(image, result, sp)
            expected_trace = prefix + ([0x141fa, 0x141fe, 0x14202] if result else [])
            if (pc != (0x143ca if result else 0x14248) or trace != expected_trace or
                    stores != {((sp + 12) & MASK): 0xc0} or regs[11] != 0xc0 or count != 1):
                raise ValueError(f'conditional command gate mismatch for result={result:#x}, sp={sp:#x}')
    mutant = bytearray(image)
    mutant[0x14246 - 0x8000 + 1] ^= 0x20
    if run(mutant, 1, 0)[0] == 0x143ca:
        raise ValueError('return-value branch mutation was not detected')
    print('PASS: c0 route saves/restores command; supplied zero/nonzero 0x81aa returns select 0x14248/0x143ca')


if __name__ == '__main__':
    main()
