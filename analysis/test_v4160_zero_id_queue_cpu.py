"""Bounded RV32IMC slice execution, not a device or provider emulation.

Flat image at 0x8000; queue, stack, source, and pointer cell are synthetic.
The indirect provider is assumed to copy exactly one byte and return, preserving
all registers except the link register written by the call. Consumer execution
stops immediately after its ID branch, before CSR or opaque calls. For slots
other than zero the guard is entered directly with s0 set to that slot.
"""
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
BASE, QUEUE, STACK, SOURCE, PROVIDER, RETURN = 0x8000, 0x2000c038, 0x21000000, 0x22000000, 0x30000000, 0x30000004
MASK = 0xffffffff


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


class CPU:
    CODE_RANGES = ((0x12bc8, 0x12c24), (0x12c58, 0x12c96))

    def __init__(self, image, queue):
        self.reg = [0] * 32
        self.reg[2] = STACK + 0x800
        self.reg[1] = RETURN
        self.pc = 0
        self.regions = [(BASE, bytearray(image), False), (QUEUE, bytearray(queue), True),
                        (STACK, bytearray(0x1000), True), (SOURCE, bytearray([0xa5]), True),
                        (0x4004c, bytearray(PROVIDER.to_bytes(4, 'little')), False)]
        self.writes = []
        self.calls = []

    def mem(self, addr, size, value=None):
        addr &= MASK
        for base, data, writable in self.regions:
            if base <= addr and addr + size <= base + len(data):
                off = addr - base
                if value is None:
                    return int.from_bytes(data[off:off + size], 'little')
                check(writable, 'write to read-only memory')
                data[off:off + size] = (value & ((1 << (size * 8)) - 1)).to_bytes(size, 'little')
                self.writes.append((addr, size, value & ((1 << (size * 8)) - 1)))
                return
        raise RuntimeError('unmapped access %#x size %d' % (addr, size))

    def put(self, reg, value):
        if reg:
            self.reg[reg] = value & MASK

    def run(self, start, stops, budget=1000):
        self.pc = start
        for _ in range(budget):
            p = self.pc
            if p in stops:
                return p
            if p == PROVIDER:
                a, b, n = self.reg[10:13]
                check(n == 1 and b == SOURCE and QUEUE + 3 <= a < QUEUE + 384, 'unexpected provider arguments')
                self.calls.append((a, b, n))
                self.mem(a, 1, self.mem(b, 1))
                self.pc = self.reg[1]
                continue
            check(any(lo <= p < hi for lo, hi in self.CODE_RANGES) and not p & 1, 'execution outside bounded slices: %#x' % p)
            h = self.mem(p, 2)
            r = self.reg
            if h & 3 != 3:
                self.pc = p + 2
                q, f = h & 3, h >> 13
                rd, rs2 = (h >> 7) & 31, (h >> 2) & 31
                imm = sx(((h >> 2) & 31) | ((h >> 7) & 32), 6)
                if q == 1 and f == 0:  # c.addi
                    self.put(rd, r[rd] + imm)
                elif q == 1 and f == 2:  # c.li
                    self.put(rd, imm)
                elif q == 1 and f == 3 and rd == 2:  # c.addi16sp
                    v = ((h >> 12 & 1) << 9 | (h >> 6 & 1) << 4 | (h >> 5 & 1) << 6 | (h >> 3 & 3) << 7 | (h >> 2 & 1) << 5)
                    self.put(2, r[2] + sx(v, 10))
                elif q == 1 and f == 3 and rd and imm:  # c.lui
                    self.put(rd, imm << 12)
                elif q == 2 and f == 0:  # c.slli
                    check(not h & 0x1000, 'invalid RV32 shift')
                    self.put(rd, r[rd] << rs2)
                elif q == 1 and f == 4 and (h >> 10 & 3) == 0:  # c.srli
                    check(not h & 0x1000, 'invalid RV32 shift')
                    d = 8 + (h >> 7 & 7)
                    self.put(d, r[d] >> (h >> 2 & 31))
                elif q == 1 and f == 4 and (h >> 10 & 3) == 2:  # c.andi
                    d = 8 + (h >> 7 & 7)
                    self.put(d, r[d] & imm)
                elif q == 1 and f == 4 and (h >> 10 & 3) == 3 and not h & 0x1000 and (h >> 5 & 3) == 2:  # c.or
                    d = 8 + (h >> 7 & 7)
                    self.put(d, r[d] | r[8 + (h >> 2 & 7)])
                elif q == 0 and f == 0:  # c.addi4spn
                    off = ((h >> 11 & 3) << 4 | (h >> 7 & 15) << 6 | (h >> 6 & 1) << 2 | (h >> 5 & 1) << 3)
                    check(off != 0, 'reserved c.addi4spn')
                    self.put(8 + (h >> 2 & 7), r[2] + off)
                elif q == 2 and f == 6:  # c.swsp
                    off = ((h >> 9 & 15) << 2) | ((h >> 7 & 3) << 6)
                    self.mem(r[2] + off, 4, r[rs2])
                elif q == 2 and f == 2:  # c.lwsp
                    off = ((h >> 12 & 1) << 5) | ((h >> 4 & 7) << 2) | ((h >> 2 & 3) << 6)
                    self.put(rd, self.mem(r[2] + off, 4))
                elif q == 0 and f == 2:  # c.lw
                    off = ((h >> 10 & 7) << 3) | ((h >> 6 & 1) << 2) | ((h >> 5 & 1) << 6)
                    self.put(8 + (h >> 2 & 7), self.mem(r[8 + (h >> 7 & 7)] + off, 4))
                elif q == 2 and f == 4:
                    if h & 0x1000:
                        if rs2:
                            self.put(rd, r[rd] + r[rs2])
                        else:
                            target = r[rd] & ~1
                            self.put(1, p + 2)
                            self.pc = target
                    elif rs2:
                        self.put(rd, r[rs2])
                    else:
                        self.pc = r[rd] & ~1
                elif q == 1 and f in (6, 7):
                    v = ((h >> 12 & 1) << 8 | (h >> 10 & 3) << 3 | (h >> 5 & 3) << 6 | (h >> 3 & 3) << 1 | (h >> 2 & 1) << 5)
                    if (r[8 + (h >> 7 & 7)] == 0) == (f == 6):
                        self.pc = p + sx(v, 9)
                elif q == 1 and f in (1, 5):  # RV32 c.jal / c.j
                    v = ((h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 | (h >> 9 & 3) << 8 | (h >> 8 & 1) << 10 | (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 | (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5)
                    if f == 1:
                        self.put(1, p + 2)
                    self.pc = p + sx(v, 12)
                else:
                    raise RuntimeError('unsupported compressed %#x at %#x' % (h, p))
            else:
                w = self.mem(p, 4)
                self.pc = p + 4
                op, rd, f, a, b, f7 = w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, w >> 25
                imm = sx(w >> 20, 12)
                if op == 0x17: self.put(rd, p + (w & 0xfffff000))
                elif op == 0x37: self.put(rd, w & 0xfffff000)
                elif op == 0x13 and f == 0: self.put(rd, r[a] + imm)
                elif op == 0x13 and f == 7: self.put(rd, r[a] & imm)
                elif op == 0x13 and f == 4: self.put(rd, r[a] ^ imm)
                elif op == 0x13 and f == 1 and f7 == 0: self.put(rd, r[a] << b)
                elif op == 0x13 and f == 5 and f7 == 0: self.put(rd, r[a] >> b)
                elif op == 0x33 and f == 0 and f7 == 0: self.put(rd, r[a] + r[b])
                elif op == 0x33 and f == 0 and f7 == 0x20: self.put(rd, r[a] - r[b])
                elif op == 0x33 and f == 0 and f7 == 1: self.put(rd, r[a] * r[b])
                elif op == 0x33 and f == 3 and f7 == 0: self.put(rd, int(r[a] < r[b]))
                elif op == 0x03 and f in (2, 4, 5): self.put(rd, self.mem(r[a] + imm, {2: 4, 4: 1, 5: 2}[f]))
                elif op == 0x23 and f in (0, 1, 2):
                    off = sx((w >> 25 << 5) | (w >> 7 & 31), 12)
                    self.mem(r[a] + off, {0: 1, 1: 2, 2: 4}[f], r[b])
                elif op == 0x67 and f == 0:
                    target = (r[a] + imm) & MASK & ~1
                    self.put(rd, p + 4)
                    self.pc = target
                elif op == 0x6f:
                    off = ((w >> 31) << 20 | (w >> 12 & 255) << 12 | (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1)
                    self.put(rd, p + 4)
                    self.pc = p + sx(off, 21)
                elif op == 0x63 and f in (0, 1, 6, 7):
                    off = ((w >> 31) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                    taken = (r[a] == r[b]) == (f == 0) if f in (0, 1) else (r[a] < r[b]) == (f == 6)
                    if taken: self.pc = p + sx(off, 13)
                else: raise RuntimeError('unsupported instruction %#x at %#x' % (w, p))
        raise RuntimeError('instruction budget exceeded')

    def queue(self):
        return bytes(self.regions[1][1])


def fixture(free):
    data = bytearray((i * 37 + 11) & 255 for i in range(384))
    for i in range(32):
        data[i * 12:i * 12 + 2] = (0x100 + i if i < free else 0).to_bytes(2, 'little')
    return data


def producer(image, data, ident, payload=0xa5, trailer=0x42):
    c = CPU(image, data)
    c.reg[10:14] = [ident, SOURCE, 1, trailer]
    c.regions[3][1][0] = payload
    c.run(0x12bc8, {RETURN})
    return c


def guard(image, data, index, entry=False):
    c = CPU(image, data)
    if not entry:
        c.reg[8] = QUEUE + 12 * index
    result = c.run(0x12c58 if entry else 0x12c8c, {0x12cee, 0x12c96})
    check(not c.calls and not any(QUEUE <= a < QUEUE + 384 for a, _, _ in c.writes), 'guard side effects')
    return result


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'firmware identity mismatch')
    for i in range(32):
        before = fixture(i)
        c = producer(image, before, 0)
        expected = bytearray(before)
        expected[12*i:12*i+4] = bytes([0, 0, 1, 0xa5])
        expected[12*i+11] = 0x42
        check(c.queue() == expected and c.calls == [(QUEUE + 12*i + 3, SOURCE, 1)], 'zero producer slot %d' % i)
        check(guard(image, c.queue(), i, entry=(i == 0)) == 0x12cee, 'zero guard slot %d' % i)
        d = producer(image, c.queue(), 0x10123, 0x5a, 0x124)
        expected[12*i:12*i+4] = bytes([0x23, 1, 1, 0x5a])
        expected[12*i+11] = 0x24
        check(d.queue() == expected and d.calls == [(QUEUE + 12*i + 3, SOURCE, 1)], 'reuse slot %d' % i)
        check(guard(image, d.queue(), i, entry=(i == 0)) == 0x12c96, 'nonzero guard slot %d' % i)
    before = fixture(32)
    c = producer(image, before, 0)
    check(c.queue() == before and not c.calls and not any(QUEUE <= a < QUEUE + 384 for a, _, _ in c.writes), 'full queue')
    # In-memory mutation: change c.beqz to c.bnez; original identity remains pinned.
    mutant = bytearray(image)
    off = 0x12c94 - BASE
    check(mutant[off:off+2] == bytes.fromhex('a9cf'), 'mutation pin')
    mutant[off+1] ^= 0x20
    check(guard(mutant, fixture(0), 0, entry=True) == 0x12c96, 'mutation control not detected')
    print('PASS: 32 occupied-prefix zero-ID, guard and nonzero reuse cases; full queue; inverted-branch mutation detected')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
