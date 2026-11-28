"""Bounded, offline RV32 subset interpretation of the counter lookup slice.

Memory is synthetic after the unknown provider has returned. No provider,
device, interrupt, or reachability model is supplied. Unsupported instructions,
unmapped data, and unexpected control edges fail closed.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
DIGEST = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
GP, SP = 0x20004000, 0x21000800
WINDOWS = {
    0x81ee: '17450020034575ce828017450020034525cf8280',
    0xa0e2: 'efe06f9183c7a10a6386a710',
    0xa114: 'a2470347a100a183bd8ba207d98f93877785c207c1831307200b636df70aefe0cf8b05479307807a6306e5028947630df50a83c7010b13971700971701009387a79fba9783d70700',
    0xa1e2: '83c7f10a9df7',
    0xa1f6: 'e39f07f0e5b7',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def check_image(data):
    need(len(data) == 76800 and hashlib.sha256(data).hexdigest() == DIGEST,
         'image identity mismatch')
    for pc, text in WINDOWS.items():
        expected = bytes.fromhex(text)
        need(data[pc - 0x8000:pc - 0x8000 + len(expected)] == expected,
             'instruction window mismatch')


class CPU:
    def __init__(self, image, counter=4, x=1961, selector=0, aa=1, leaf=1, af=0):
        need(all(isinstance(v, int) and 0 <= v <= 255
                 for v in (counter, selector, aa, leaf, af)), 'byte input')
        need(isinstance(x, int) and 0 <= x < 4096, '12-bit input')
        self.image = image
        self.r = [0] * 32
        self.r[2], self.r[3] = SP, GP
        self.pc = 0xa0e2
        self.memory = {GP + 170: aa, GP + 175: af, GP + 176: counter,
                       0x2000beea: leaf, 0x2000bed5: selector,
                       SP + 8: 0x5a, SP + 9: x >> 8,
                       SP + 10: x & 255, SP + 11: 0xc3}
        self.trace = []
        self.reads = []

    def load(self, address, width):
        address &= MASK
        need(all(address + i in self.memory for i in range(width)), 'unmapped data read')
        self.reads.append((self.trace[-1], address, width))
        return sum(self.memory[address + i] << (8 * i) for i in range(width))

    def put(self, rd, value):
        if rd:
            self.r[rd] = value & MASK

    def fetch(self):
        for base, text in WINDOWS.items():
            end = base + len(bytes.fromhex(text))
            if base <= self.pc < end:
                offset = self.pc - 0x8000
                h = int.from_bytes(self.image[offset:offset + 2], 'little')
                size = 4 if h & 3 == 3 else 2
                need(self.pc + size <= end and not self.pc & 1, 'fetch boundary')
                return int.from_bytes(self.image[offset:offset + size], 'little'), size
        raise ValueError('unexpected instruction address')

    def run(self, budget=80):
        stops = {0xa0ee: 'unequal', 0xa1e8: 'exit', 0xa168: 'selector1', 0xa1fc: 'selector2'}
        for _ in range(budget):
            if self.pc in stops:
                return {'edge': stops[self.pc]}
            p, r = self.pc, self.r
            w, size = self.fetch()
            self.trace.append(p)
            if p == 0xa158:
                need(w == 0x0007d783 and size == 4, 'expected terminal LHU')
                # Observe the effective address BEFORE reading unknown table contents.
                return {'edge': 'read', 'address': r[15], 'width': 2}
            self.pc += size
            if size == 4:
                op, rd, f, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
                if op == 0x17:
                    self.put(rd, p + (w & 0xfffff000))
                elif op == 0x03 and f == 4:
                    self.put(rd, self.load(r[rs1] + sx(w >> 20, 12), 1))
                elif op == 0x13 and f == 0:
                    self.put(rd, r[rs1] + sx(w >> 20, 12))
                elif op == 0x13 and f == 1 and w >> 25 == 0:
                    self.put(rd, r[rs1] << rs2)
                elif op == 0x6f:
                    imm = ((w >> 31) << 20 | (w >> 12 & 255) << 12 |
                           (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1)
                    self.put(rd, p + 4)
                    self.pc = (p + sx(imm, 21)) & MASK
                elif op == 0x63 and f in (0, 1, 6):
                    imm = ((w >> 31) << 12 | (w >> 7 & 1) << 11 |
                           (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                    taken = (r[rs1] == r[rs2]) if f == 0 else ((r[rs1] != r[rs2]) if f == 1 else r[rs1] < r[rs2])
                    if taken:
                        self.pc = (p + sx(imm, 13)) & MASK
                else:
                    raise ValueError('unsupported RV32 instruction')
            else:
                q, f, rd, rs2 = w & 3, w >> 13, w >> 7 & 31, w >> 2 & 31
                imm = sx((w >> 2 & 31) | (w >> 7 & 32), 6)
                d = 8 + (w >> 7 & 7)
                if q == 2 and f == 2 and rd != 0:
                    off = (w >> 12 & 1) << 5 | (w >> 4 & 7) << 2 | (w >> 2 & 3) << 6
                    self.put(rd, self.load(r[2] + off, 4))
                elif q == 1 and f == 2 and rd != 0:
                    self.put(rd, imm)
                elif q == 2 and f == 0 and not w & 0x1000 and rd != 0:
                    self.put(rd, r[rd] << rs2)
                elif q == 1 and f == 4 and w >> 10 & 3 == 0 and not w & 0x1000:
                    self.put(d, r[d] >> (w >> 2 & 31))
                elif q == 1 and f == 4 and w >> 10 & 3 == 2:
                    self.put(d, r[d] & imm)
                elif q == 1 and f == 4 and w >> 10 & 3 == 3 and not w & 0x1000 and w >> 5 & 3 == 2:
                    self.put(d, r[d] | r[8 + (w >> 2 & 7)])
                elif q == 2 and f == 4 and w & 0x1000 and rs2 and rd:
                    self.put(rd, r[rd] + r[rs2])
                elif q == 2 and f == 4 and not w & 0x1000 and rs2 == 0 and rd:
                    self.pc = r[rd] & ~1
                elif q == 1 and f == 7:
                    off = ((w >> 12 & 1) << 8 | (w >> 10 & 3) << 3 |
                           (w >> 5 & 3) << 6 | (w >> 3 & 3) << 1 | (w >> 2 & 1) << 5)
                    if r[d] != 0:
                        self.pc = p + sx(off, 9)
                elif q == 1 and f == 5:
                    off = ((w >> 12 & 1) << 11 | (w >> 11 & 1) << 4 |
                           (w >> 9 & 3) << 8 | (w >> 8 & 1) << 10 |
                           (w >> 7 & 1) << 6 | (w >> 6 & 1) << 7 |
                           (w >> 3 & 7) << 1 | (w >> 2 & 1) << 5)
                    self.pc = p + sx(off, 12)
                else:
                    raise ValueError('unsupported compressed instruction')
        raise ValueError('instruction budget exceeded')


def expected(counter, x, selector, aa, leaf, af):
    if aa != leaf:
        return {'edge': 'unequal'}
    if aa == 0 and af == 0 or not 1961 <= x <= 2139:
        return {'edge': 'exit'}
    if selector in (1, 2):
        return {'edge': 'selector' + str(selector)}
    return {'edge': 'read', 'address': 0x1ab48 + counter * 2, 'width': 2}


def verify(image):
    check_image(image)
    cases = 0
    edges = {}
    def compare(counter, x, selector, aa=1, leaf=1, af=0):
        nonlocal cases
        cpu = CPU(image, counter, x, selector, aa, leaf, af)
        result = cpu.run()
        need(result == expected(counter, x, selector, aa, leaf, af), 'instruction/formula disagreement')
        need(cpu.r[2:4] == [SP, GP] and not any(0xa0ee <= p <= 0xa0fa for p in cpu.trace), 'preserved state/equal edge')
        cases += 1
        edges[result['edge']] = edges.get(result['edge'], 0) + 1
    # All 256 counter values, every selector byte, and both equal-edge paths.
    for counter in range(256):
        for selector in range(256):
            compare(counter, 1961, selector)
        for x in (0, 1960, 1961, 2139, 2140, 4095):
            compare(counter, x, 0, aa=0, leaf=0, af=1)
            compare(counter, x, 0, aa=0, leaf=0, af=0)
    # Complete reconstructed 12-bit stack field domain, including range wrap.
    for x in range(4096):
        compare(4, x, 0)
    # Every aa/leaf combination, including the unmodeled unequal successor.
    for aa in range(256):
        for leaf in range(256):
            compare(4, 1961, 0, aa=aa, leaf=leaf)
    witness = CPU(image)
    result = witness.run()
    need(result == {'edge': 'read', 'address': 0x1ab50, 'width': 2}, 'conditional address witness')
    return {'passed': True, 'image_sha256': DIGEST, 'cases': cases, 'edges': edges,
            'witness': result, 'witness_trace': [hex(p) for p in witness.trace],
            'table_contents_read': False, 'provider_executed': False,
            'reachability_proved': False, 'device_executed': False,
            'formal_coverage_bytes_added': 0}


if __name__ == '__main__':
    print(json.dumps(verify(IMAGE.read_bytes()), indent=2))
