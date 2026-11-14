"""Small byte-decoding RV32I/C executor for the fixed 0x148b4 window only."""
MASK = 0xffffffff
NAMES = ('a0', 'a1', 'a2', 'a3', 's0', 'sp', 't1', 't3')
REGS = (10, 11, 12, 13, 8, 2, 6, 28)

def signed(x, width):
    return x - (1 << width) if x & (1 << (width - 1)) else x

def run(window, values, loaded):
    if len(window) != 42:
        raise ValueError('wrong window size')
    if len(values) != 8 or any(not isinstance(v, int) or not 0 <= v <= MASK for v in values):
        raise ValueError('expected eight unsigned 32-bit register values')
    if not isinstance(loaded, int) or not 0 <= loaded <= 0xffff:
        raise ValueError('loaded must be an unsigned 16-bit value')
    x = [0] * 32
    for reg, value in zip(REGS, values): x[reg] = value
    pc, read_addr, write_addr, write_value, wrote = 0x148b4, 0, 0, 0, 0
    for _ in range(20):
        if pc in (0x148de, 0x1488e):
            return tuple(x[i] for i in REGS), pc, read_addr, write_addr, write_value, wrote
        offset = pc - 0x148b4
        if offset < 0 or offset + 2 > len(window) or pc & 1:
            raise ValueError('PC outside instruction window')
        h = int.from_bytes(window[offset:offset + 2], 'little')
        if h & 3 != 3:
            quadrant, funct3, rd = h & 3, h >> 13, (h >> 7) & 31
            if quadrant == 1 and funct3 == 0 and rd:  # C.ADDI
                imm = signed((h >> 2 & 31) | (h >> 12 & 1) << 5, 6)
                x[rd] = (x[rd] + imm) & MASK; pc += 2
            elif quadrant == 2 and funct3 == 0 and rd and not (h >> 12 & 1):  # C.SLLI RV32
                x[rd] = (x[rd] << (h >> 2 & 31)) & MASK; pc += 2
            elif quadrant == 2 and funct3 == 4 and h >> 12 & 1 and rd and (h >> 2 & 31):  # C.ADD
                x[rd] = (x[rd] + x[h >> 2 & 31]) & MASK; pc += 2
            elif quadrant == 1 and funct3 == 5:  # C.J
                imm = ((h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 | (h >> 9 & 3) << 8 |
                       (h >> 8 & 1) << 10 | (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 |
                       (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5)
                pc += signed(imm, 12)
            else: raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
        else:
            if offset + 4 > len(window): raise ValueError('truncated instruction')
            w = int.from_bytes(window[offset:offset + 4], 'little')
            op, rd, f3, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
            if op == 0x13 and f3 in (0, 7):  # ADDI, ANDI
                imm = signed(w >> 20, 12)
                x[rd] = ((x[rs1] + imm) if f3 == 0 else (x[rs1] & imm)) & MASK; pc += 4
            elif op == 0x13 and f3 == 1 and w >> 25 == 0:  # SLLI
                x[rd] = (x[rs1] << rs2) & MASK; pc += 4
            elif op == 3 and f3 == 5:  # LHU, supplied value models successful read
                read_addr = (x[rs1] + signed(w >> 20, 12)) & MASK
                x[rd] = loaded; pc += 4
            elif op == 0x23 and f3 == 1:  # SH, report event without memory side effects
                imm = signed(((w >> 25) << 5) | rd, 12)
                write_addr = (x[rs1] + imm) & MASK; write_value = x[rs2] & 65535; wrote = 1; pc += 4
            elif op == 0x63 and f3 == 6:  # BLTU
                imm = ((w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                pc = pc + signed(imm, 13) if x[rs1] < x[rs2] else pc + 4
            else: raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        x[0] = 0
    raise ValueError('instruction limit exceeded')
