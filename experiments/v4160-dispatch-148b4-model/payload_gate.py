"""Original-byte c0 payload-prefix classifier, stopping before its first call.

Read bytes are externally supplied and may be outside the declared length; no
memory-safety, caller reachability, or device execution is implied.
"""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
EXITS = {0x14498, 0x1491a, 0x147f8}


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def run(image, length, first, second, base, handle=0x1234):
    if not 0 <= length <= MASK or not 0 <= base <= MASK or not 0 <= handle <= MASK or not 0 <= first <= 255 or not 0 <= second <= 255:
        raise ValueError('invalid projection input')
    regs = [0] * 32
    regs[8], regs[9], regs[11], regs[18] = base, handle, 0xc0, length
    memory = {base: first, (base + 1) & MASK: second}
    pc, reads, trace = 0x143ca, [], []
    for _ in range(32):
        if pc in EXITS:
            return pc, reads, trace, regs
        offset = pc - 0x8000
        if offset < 0 or offset + 4 > len(image) or pc & 1:
            raise ValueError(f'invalid PC {pc:#x}')
        trace.append(pc)
        h = int.from_bytes(image[offset:offset + 2], 'little')
        if h & 3 != 3:
            rd = h >> 7 & 31
            if (h & 3, h >> 13) == (1, 2) and rd:
                regs[rd] = signed((h >> 2 & 31) | ((h >> 12 & 1) << 5), 6) & MASK
            elif (h & 3, h >> 13, h >> 12 & 1) == (2, 4, 0) and rd and (h >> 2 & 31):
                regs[rd] = regs[h >> 2 & 31]
            else:
                raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
            pc += 2
        else:
            w = int.from_bytes(image[offset:offset + 4], 'little')
            op, rd, f3, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
            if op == 0x13 and f3 == 0:
                regs[rd] = (regs[rs1] + signed(w >> 20, 12)) & MASK
                pc += 4
            elif op == 3 and f3 == 4:
                address = (regs[rs1] + signed(w >> 20, 12)) & MASK
                if address not in memory:
                    raise ValueError(f'unexpected byte read {address:#x}')
                reads.append(address)
                regs[rd] = memory[address]
                pc += 4
            elif op == 0x63 and f3 in (0, 1, 6, 7):
                imm = (w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1
                taken = ((regs[rs1] == regs[rs2]) if f3 == 0 else (regs[rs1] != regs[rs2]) if f3 == 1
                         else (regs[rs1] < regs[rs2]) if f3 == 6 else (regs[rs1] >= regs[rs2]))
                pc = (pc + signed(imm, 13)) & MASK if taken else pc + 4
            else:
                raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        regs[0] = 0
    raise ValueError('instruction budget exceeded')


def main():
    data = IMAGE.read_bytes()
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    base = 0x2000b9d8
    for first in range(256):
        for second in range(256):
            pc, reads, _, regs = run(data, 20, first, second, base)
            expected = 0x147f8 if (first, second) == (255, 255) else 0x1491a
            expected_reads = [base, base + 1] if first == 255 else [base]
            if pc != expected or reads != expected_reads:
                raise ValueError(f'prefix mismatch at {first:#x},{second:#x}')
            if pc == 0x147f8 and (regs[10], regs[11], regs[8], regs[9], regs[18]) != (0x1234, 2, base, 0x1234, 20):
                raise ValueError('call arguments or saved registers mismatch')
    for length in (0, 1, 2, 514, MASK):
        pc, reads, _, regs = run(data, length, 255, 255, MASK)
        if (pc, reads) != ((0x14498, [MASK]) if length == 1 else (0x147f8, [MASK, 0])):
            raise ValueError(f'length/byte boundary mismatch at {length}')
    for handle in (0, 1, 0xffff, 0x10000, MASK):
        pc, _, _, regs = run(data, 20, 255, 255, base, handle)
        if pc != 0x147f8 or (regs[10], regs[11], regs[8], regs[9], regs[18]) != (handle, 2, base, handle, 20):
            raise ValueError(f'call argument mismatch at handle {handle:#x}')
    mutant = bytearray(data)
    mutant[0x147e8 - 0x8000 + 1] ^= 0x10  # swap BEQ/BNE where encoding permits
    try:
        pc, _, _, _ = run(mutant, 20, 255, 255, base)
    except ValueError:
        pass
    else:
        if pc == 0x147f8: raise ValueError('prefix branch mutation not detected')
    print('PASS: all 65536 prefix pairs at length 20, first call arguments and saved registers; short-length and 32-bit address boundaries checked')


if __name__ == '__main__':
    main()
