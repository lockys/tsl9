"""Bounded decoder for the original 0x14122 predicate, not a full CPU."""
BASE = 0x14122
MASK = 0xffffffff


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def run(code, data, configured, length=4):
    if len(code) != 88 or len(data) != 4 or len(configured) != 4:
        raise ValueError('invalid input size')
    x = [0] * 32
    x[2], x[3], x[8], x[13] = 0x1000, 0x2000, 0x3000, length
    memory = {0x3000+i: v for i, v in enumerate(data)}
    memory.update({0x400c+i: v for i, v in enumerate(configured)})
    for i, b in enumerate((0x00, 0x40, 0, 0)):
        memory[0x2054+i] = b
    def load(address, size):
        try:
            return sum(memory[(address+i) & MASK] << (8*i) for i in range(size))
        except KeyError as exc:
            raise ValueError('unmapped read') from exc
    pc = BASE
    for _ in range(120):
        if pc == 0x14098: return 'length'
        if pc == 0x1411a: return 'mismatch'
        if pc == 0x1416e: return 'match'  # before first outgoing JAL
        off = pc - BASE
        if off < 0 or off + 2 > len(code) or pc & 1: raise ValueError('PC outside window')
        h = int.from_bytes(code[off:off+2], 'little')
        if h & 3 != 3:
            q, f, rd, rs = h & 3, h >> 13, (h >> 7) & 31, (h >> 2) & 31
            if q == 1 and f == 2 and rd:  # C.LI
                x[rd] = sx(((h >> 12 & 1) << 5) | (h >> 2 & 31), 6) & MASK
            elif q == 1 and f == 0 and rd:  # C.ADDI
                x[rd] = (x[rd] + sx(((h >> 12 & 1) << 5) | (h >> 2 & 31), 6)) & MASK
            elif q == 2 and f == 6:  # C.SWSP
                imm = ((h >> 9 & 15) << 2) | ((h >> 7 & 3) << 6)
                addr = (x[2] + imm) & MASK
                for i in range(4): memory[(addr+i) & MASK] = (x[rs] >> (8*i)) & 255
            elif q == 0 and f == 2:  # C.LW
                dest, src = 8 + (h >> 2 & 7), 8 + (h >> 7 & 7)
                imm = ((h >> 10 & 7) << 3) | ((h >> 6 & 1) << 2) | ((h >> 5 & 1) << 6)
                x[dest] = load((x[src] + imm) & MASK, 4)
            elif q == 0 and f == 0:  # C.ADDI4SPN
                imm = ((h >> 7 & 15) << 6) | ((h >> 11 & 3) << 4) | ((h >> 5 & 1) << 3) | ((h >> 6 & 1) << 2)
                if not imm: raise ValueError('reserved C.ADDI4SPN')
                x[8 + (h >> 2 & 7)] = (x[2] + imm) & MASK
            elif q == 2 and f == 4 and rd and rs:  # C.MV / C.ADD
                x[rd] = ((x[rd] if h >> 12 & 1 else 0) + x[rs]) & MASK
            elif q == 1 and f == 5:  # C.J
                imm = ((h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 | (h >> 9 & 3) << 8 | (h >> 8 & 1) << 10 | (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 | (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5)
                pc += sx(imm, 12)
                continue
            else: raise ValueError(f'unsupported compressed {h:#x} at {pc:#x}')
            pc += 2
        else:
            if off + 4 > len(code): raise ValueError('truncated')
            w = int.from_bytes(code[off:off+4], 'little')
            op, rd, f, r1, r2 = w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31
            if op == 0x37: x[rd] = w & 0xfffff000  # LUI
            elif op == 0x13 and f == 0: x[rd] = (x[r1] + sx(w >> 20, 12)) & MASK
            elif op == 0x33 and f == 0 and w >> 25 == 0: x[rd] = (x[r1] + x[r2]) & MASK
            elif op == 3 and f == 4: x[rd] = load((x[r1] + sx(w >> 20, 12)) & MASK, 1)
            elif op == 0x63 and f in (0, 1):
                imm = ((w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                if (x[r1] == x[r2]) == (f == 0):
                    pc += sx(imm, 13)
                    continue
            else: raise ValueError(f'unsupported word {w:#x} at {pc:#x}')
            pc += 4
        x[0] = 0
    raise ValueError('step limit')
