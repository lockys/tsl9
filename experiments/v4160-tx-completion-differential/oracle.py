"""Bounded RV32IMC interpretation from TX bank selection to before JR T1."""
import struct

BASE = 0x2000b18c
MASK = 0xffffffff
REGIONS = ((0x8ace, 0x8b6c),)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


class Memory:
    def __init__(self, regions):
        self.regions = [(base, bytearray(data)) for base, data in regions]
        self.events = bytearray()
        ordered = sorted((base, base+len(data)) for base, data in self.regions)
        need(all(0 <= lo < hi <= 1 << 32 for lo, hi in ordered), 'bounded regions')
        need(all(a[1] <= b[0] for a, b in zip(ordered, ordered[1:])), 'disjoint address mappings')

    def access(self, address, width, value=None):
        need(width in (1, 2, 4) and address % width == 0, 'aligned original access')
        for base, data in self.regions:
            index = address - base
            if 0 <= index and index+width <= len(data):
                if value is None:
                    value = int.from_bytes(data[index:index+width], 'little')
                    kind = 1
                else:
                    value &= (1 << (8*width))-1
                    data[index:index+width] = value.to_bytes(width, 'little')
                    kind = 2
                self.events.extend(struct.pack('<4I', kind, address, width, value))
                return value
        raise ValueError('unmapped original memory access')


class Slice:
    def __init__(self, image):
        self.code = {}
        for start, end in REGIONS:
            pc = start
            while pc < end:
                offset = pc - 0x8000
                half = int.from_bytes(image[offset:offset + 2], 'little')
                size = 4 if half & 3 == 3 else 2
                need(pc + size <= end, 'instruction boundary')
                self.code[pc] = (int.from_bytes(image[offset:offset + size], 'little'), size)
                pc += size

    def run(self, regions, registers, budget=None):
        need(len(registers) == 32 and registers[0] == 0
             and all(type(v) is int and 0 <= v <= MASK for v in registers), 'RV32 registers')
        need(registers[12] in (0, 1) and registers[8] <= 65535, 'post-provider bank/length domain')
        memory = Memory(regions)
        r = list(registers)
        pc = 0x8ace
        budget = 16 * r[8] + 256 if budget is None else budget

        def put(rd, value):
            if rd:
                r[rd] = value & MASK

        for _ in range(budget):
            if pc == 0x8b50:
                return memory.regions, r, bytes(memory.events)
            need(pc in self.code, 'execution outside bounded slice')
            w, size = self.code[pc]
            p = pc
            pc += size
            if size == 4:
                op, rd, f, a, b, top = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, w >> 25
                if op == 0x37:
                    put(rd, w & 0xfffff000)
                elif op == 0x17:
                    put(rd, p + (w & 0xfffff000))
                elif op == 0x13 and f in (0, 4, 7):
                    imm = sx(w >> 20, 12)
                    value = r[a] + imm if f == 0 else r[a] ^ imm if f == 4 else r[a] & imm
                    put(rd, value)
                elif op == 0x13 and top == 0 and f in (1, 5):
                    put(rd, r[a] << b if f == 1 else r[a] >> b)
                elif op == 0x33 and f == 0 and top in (0, 1):
                    put(rd, r[a] + r[b] if top == 0 else r[a] * r[b])
                elif op == 0x03 and f in (2, 4):
                    address = (r[a] + sx(w >> 20, 12)) & MASK
                    put(rd, memory.access(address, 4 if f == 2 else 1))
                elif op == 0x23 and f in (0, 1):
                    off = sx((w >> 25 << 5) | (w >> 7 & 31), 12)
                    memory.access((r[a] + off) & MASK, 1 << f, r[b])
                elif op == 0x63 and f == 6:
                    off = ((w >> 31) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                    if r[a] < r[b]:
                        pc = p + sx(off, 13)
                else:
                    raise ValueError('unsupported RV32 instruction')
            else:
                q, f, rd, rs2 = w & 3, w >> 13, w >> 7 & 31, w >> 2 & 31
                imm = sx((w >> 2 & 31) | (w >> 7 & 32), 6)
                if q == 2 and f == 2 and rd:
                    off = (w >> 12 & 1) << 5 | (w >> 4 & 7) << 2 | (w >> 2 & 3) << 6
                    put(rd, memory.access((r[2]+off)&MASK, 4))
                elif q == 2 and f == 0 and rd and not w & 0x1000:
                    put(rd, r[rd] << rs2)
                elif q == 1 and f == 3 and rd == 2:
                    off = ((w >> 12 & 1) << 9 | (w >> 6 & 1) << 4 | (w >> 5 & 1) << 6 |
                           (w >> 3 & 3) << 7 | (w >> 2 & 1) << 5)
                    put(2, r[2]+sx(off,10))
                elif q == 1 and f == 3 and rd not in (0, 2) and imm:
                    put(rd, imm << 12)
                elif q == 1 and f == 0 and rd and imm:
                    put(rd, r[rd] + imm)
                elif q == 1 and f == 2 and rd:
                    put(rd, imm)
                elif q == 2 and f == 4 and w & 0x1000 and rd and rs2:
                    put(rd, r[rd] + r[rs2])
                elif q == 1 and f == 4 and w >> 10 & 3 == 0 and not w & 0x1000:
                    dreg = 8 + (w >> 7 & 7)
                    put(dreg, r[dreg] >> (w >> 2 & 31))
                elif q == 1 and f == 5:
                    off = ((w >> 12 & 1) << 11 | (w >> 11 & 1) << 4 | (w >> 9 & 3) << 8 |
                           (w >> 8 & 1) << 10 | (w >> 7 & 1) << 6 | (w >> 6 & 1) << 7 |
                           (w >> 3 & 7) << 1 | (w >> 2 & 1) << 5)
                    pc = p + sx(off, 12)
                else:
                    raise ValueError('unsupported compressed instruction')
        raise ValueError('slice instruction budget exceeded')
