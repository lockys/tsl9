"""Bounded RV32IMC subset for the original TX header/copy slice only."""
BASE = 0x2000b18c
MASK = 0xffffffff
REGIONS = ((0x8ace, 0x8b14), (0x8b52, 0x8b6c))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


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

    def run(self, initial, origin, base_index, source_index, bank, length, command, entry_a6, budget=None):
        need(all(type(v) is int and 0 <= v <= MASK for v in
                 (origin, base_index, source_index, bank, length, command, entry_a6)), 'uint32 slice inputs')
        need(bank in (0, 1) and 0 <= length <= 65535 and origin + base_index == BASE, 'slice domain')
        need(0 <= source_index < len(initial) and source_index + length <= len(initial), 'source object bounds')
        d = base_index + 1062 * bank + 6
        need(0 <= d and d + 5 + length <= len(initial), 'destination object bounds')
        need(origin >= 0 and origin + len(initial) <= 1 << 32, 'no address wrap')
        memory = bytearray(initial)
        r = [0] * 32
        r[8], r[9], r[19], r[12], r[16] = length, origin + source_index, command, bank, entry_a6
        pc = 0x8ace
        writes, reads = 0, 0
        first_write, last_write_end = len(memory), 0
        budget = 16 * length + 128 if budget is None else budget

        def put(rd, value):
            if rd:
                r[rd] = value & MASK

        for _ in range(budget):
            if pc == 0x8b14:
                return memory, tuple(r[10:17] + [r[8], r[9], r[19]]), {
                    'writes': writes, 'reads': reads,
                    'write_start_index': first_write, 'write_end_index': last_write_end}
            need(pc in self.code, 'execution outside bounded slice')
            w, size = self.code[pc]
            p = pc
            pc += size
            if size == 4:
                op, rd, f, a, b, top = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31, w >> 25
                if op == 0x17:
                    put(rd, p + (w & 0xfffff000))
                elif op == 0x13 and f in (0, 4, 7):
                    imm = sx(w >> 20, 12)
                    value = r[a] + imm if f == 0 else r[a] ^ imm if f == 4 else r[a] & imm
                    put(rd, value)
                elif op == 0x13 and top == 0 and f in (1, 5):
                    put(rd, r[a] << b if f == 1 else r[a] >> b)
                elif op == 0x33 and f == 0 and top in (0, 1):
                    put(rd, r[a] + r[b] if top == 0 else r[a] * r[b])
                elif op == 0x03 and f == 4:
                    index = ((r[a] + sx(w >> 20, 12)) & MASK) - origin
                    need(0 <= index < len(memory), 'unmapped byte load')
                    put(rd, memory[index])
                    reads += 1
                elif op == 0x23 and f in (0, 1):
                    off = sx((w >> 25 << 5) | (w >> 7 & 31), 12)
                    index = ((r[a] + off) & MASK) - origin
                    width = 1 << f
                    need(0 <= index and index + width <= len(memory), 'unmapped store')
                    need(width == 1 or (index + origin) % 2 == 0, 'aligned halfword store')
                    for i in range(width):
                        memory[index + i] = r[b] >> (8 * i) & 255
                    writes += 1
                    first_write = min(first_write, index)
                    last_write_end = max(last_write_end, index + width)
                elif op == 0x63 and f == 6:
                    off = ((w >> 31) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                    if r[a] < r[b]:
                        pc = p + sx(off, 13)
                else:
                    raise ValueError('unsupported RV32 instruction')
            else:
                q, f, rd, rs2 = w & 3, w >> 13, w >> 7 & 31, w >> 2 & 31
                imm = sx((w >> 2 & 31) | (w >> 7 & 32), 6)
                if q == 1 and f == 3 and rd not in (0, 2) and imm:
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
