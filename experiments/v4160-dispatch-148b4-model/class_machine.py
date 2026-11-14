"""Limited RV32I/C byte decoder for classifier and shared tail, no memory effects."""
MASK = 0xffffffff
REGS = (11, 12, 14, 15, 16, 17, 2, 6, 28)

def signed(x, bits):
    return x - (1 << bits) if x & (1 << (bits - 1)) else x

def run(window, values):
    if len(window) != 0x42:
        raise ValueError('wrong instruction window size')
    if len(values) != len(REGS) or any(not isinstance(x, int) or not 0 <= x <= MASK for x in values):
        raise ValueError('expected nine unsigned RV32 values')
    x = [0] * 32
    for reg, val in zip(REGS, values): x[reg] = val
    pc = 0x148de
    addr = value = wrote = 0
    for _ in range(30):
        if pc == 0x1488e:
            return tuple(x[r] for r in REGS), pc, addr, value, wrote
        off = pc - 0x148d8
        if pc & 1 or off < 0 or off + 2 > len(window):
            raise ValueError(f'PC outside classifier window: {pc:#x}')
        h = int.from_bytes(window[off:off+2], 'little')
        if h & 3 != 3:
            quadrant, f3, rd, rs2 = h & 3, h >> 13, (h >> 7) & 31, (h >> 2) & 31
            if quadrant == 2 and f3 == 0 and rd and not (h >> 12 & 1):
                x[rd] = (x[rd] << rs2) & MASK; pc += 2
            elif quadrant == 2 and f3 == 4 and (h >> 12 & 1) and rd and rs2:
                x[rd] = (x[rd] + x[rs2]) & MASK; pc += 2
            elif quadrant == 1 and f3 == 5:
                imm = ((h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 | (h >> 9 & 3) << 8 |
                       (h >> 8 & 1) << 10 | (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 |
                       (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5)
                pc += signed(imm, 12)
            else: raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
        else:
            if off + 4 > len(window): raise ValueError('truncated instruction')
            w = int.from_bytes(window[off:off+4], 'little')
            op, rd, f3, rs1, rs2, f7 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, w >> 25
            if op == 0x33 and f3 == 7 and f7 == 0:
                x[rd] = x[rs1] & x[rs2]; pc += 4
            elif op == 0x13 and f3 in (0, 7):
                imm = signed(w >> 20, 12)
                x[rd] = ((x[rs1] + imm) if f3 == 0 else (x[rs1] & imm)) & MASK; pc += 4
            elif op == 0x63 and f3 == 0:
                imm = ((w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                pc = pc + signed(imm, 13) if x[rs1] == x[rs2] else pc + 4
            elif op == 0x23 and f3 == 1:
                imm = signed((w >> 25) << 5 | rd, 12)
                addr, value, wrote = (x[rs1] + imm) & MASK, x[rs2] & 65535, 1
                pc += 4
            else: raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        x[0] = 0
    raise ValueError('instruction limit exceeded')
