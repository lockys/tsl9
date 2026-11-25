"""Offline slot-reference candidates and original NV-wrapper instruction checks.

Raw halfword-aligned LUI+word-access pairs are candidates, not a full CFG census.
The provider pointer cell is synthetic; stop at its loaded target, never run it.
"""
from hashlib import sha256
from test_v4160_zero_id_queue_cpu import CPU, IMAGE, BASE, STACK, RETURN, MASK, check, sx

SLOT, START, END = 0x4004c, 0x1979a, 0x197b8
IDENTITY = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def scan_slot(image):
    rows = []
    for off in range(0, len(image)-5, 2):
        w = int.from_bytes(image[off:off+4], 'little')
        if w & 127 != 0x37 or w & 0xfffff000 != 0x40000:
            continue
        base = w >> 7 & 31
        if base == 0:
            continue
        p = off+4
        h = int.from_bytes(image[p:p+2], 'little')
        size = 2 if h & 3 != 3 else 4
        if p+size > len(image):
            continue
        if size == 2:
            kind = h >> 13
            displacement = (h >> 10 & 7) << 3 | (h >> 6 & 1) << 2 | (h >> 5 & 1) << 6
            if h & 3 != 0 or kind not in (2, 6) or 8+(h >> 7 & 7) != base or displacement != 76:
                continue
            access, reg = ('load' if kind == 2 else 'store'), 8+(h >> 2 & 7)
        else:
            v = int.from_bytes(image[p:p+4], 'little')
            op = v & 127
            if op not in (3, 0x23) or v >> 12 & 7 != 2 or v >> 15 & 31 != base:
                continue
            displacement = sx(v >> 20, 12) if op == 3 else sx(v >> 25 << 5 | v >> 7 & 31, 12)
            if displacement != 76:
                continue
            access, reg = ('load', v >> 7 & 31) if op == 3 else ('store', v >> 20 & 31)
        rows.append({'lui': BASE+off, 'access': BASE+p, 'kind': access, 'register': reg,
                     'encoding': image[off:p+size].hex()})
    return rows


class NVProbe(CPU):
    def __init__(self, image):
        super().__init__(image, bytes(384))
        self.slot_reads = []

    def mem(self, address, size, value=None):
        if address == SLOT and value is None:
            self.slot_reads.append((address, size, self.reg[2]))
        return super().mem(address, size, value)

    def pointer(self, value):
        for base, data, _ in self.regions:
            if base == SLOT:
                data[:] = value.to_bytes(4, 'little')
                return
        raise RuntimeError('pointer cell missing')

    def run_nv(self, start, stops):
        self.pc = start
        for _ in range(32):
            p, r = self.pc, self.reg
            if p in stops:
                return p
            check(START <= p < END and not p & 1, 'outside NV wrapper')
            h = self.mem(p, 2)
            if h & 3 != 3:
                self.pc = p+2
                q, f, d, s = h & 3, h >> 13, h >> 7 & 31, h >> 2 & 31
                imm = sx((h >> 2 & 31) | (h >> 7 & 32), 6)
                if q == 0 and f == 2:  # C.LW
                    off = (h >> 10 & 7) << 3 | (h >> 6 & 1) << 2 | (h >> 5 & 1) << 6
                    self.put(8+(h >> 2 & 7), self.mem(r[8+(h >> 7 & 7)]+off, 4))
                elif q == 1 and f in (0, 2):
                    self.put(d, (r[d] if f == 0 else 0)+imm)
                elif q == 2 and f == 6:
                    self.mem(r[2]+((h >> 9 & 15) << 2 | (h >> 7 & 3) << 6), 4, r[s])
                elif q == 2 and f == 2:
                    off = (h >> 12 & 1) << 5 | (h >> 4 & 7) << 2 | (h >> 2 & 3) << 6
                    self.put(d, self.mem(r[2]+off, 4))
                elif q == 2 and f == 4:
                    if s and not h & 0x1000:  # C.MV
                        self.put(d, r[s])
                    elif not s and d:
                        target = r[d] & ~1
                        if h & 0x1000:  # C.JALR
                            self.put(1, p+2)
                        self.pc = target
                    else:
                        raise RuntimeError('unsupported NV jump')
                else:
                    raise RuntimeError('unsupported NV compressed instruction')
            else:
                w = self.mem(p, 4)
                self.pc = p+4
                op, d, f, a = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31
                if op == 0x37:
                    self.put(d, w & 0xfffff000)
                elif op == 0x13 and f == 1 and w >> 25 == 0:
                    self.put(d, r[a] << (w >> 20 & 31))
                else:
                    raise RuntimeError('unsupported NV instruction')
        raise RuntimeError('NV budget exceeded')


def wrapper_case(c, source, words, destination, pointer):
    c.reg = [0]*32
    c.reg[1], c.reg[2] = RETURN, STACK+0x800
    c.reg[10:13] = [source, words, destination]
    c.writes.clear()
    c.slot_reads.clear()
    c.pointer(pointer)
    target = pointer & ~1
    check(c.run_nv(START, {target}) == target, 'loaded target')
    check(c.slot_reads == [(SLOT, 4, STACK+0x800)], 'fresh load before frame')
    check(c.reg[10:13] == [destination, source, words << 2 & MASK], 'NV provider arguments')
    check(c.reg[1] == 0x197b0 and c.reg[2] == STACK+0x800-16, 'NV call frame')
    check(c.writes == [(STACK+0x800-4, 4, RETURN)], 'NV pre-call stores')
    # Conditional provider return: preserve stack/SP and supply an arbitrary A0.
    c.put(10, 0xdeadbeef)
    c.run_nv(0x197b0, {RETURN})
    check(c.reg[10] == 0 and c.reg[2] == STACK+0x800 and c.reg[1] == RETURN, 'NV zero return/restore')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'image identity')
    rows = scan_slot(image)
    loads = [r for r in rows if r['kind'] == 'load']
    stores = [r for r in rows if r['kind'] == 'store']
    check(len(loads) == 41 and not stores, 'adjacent-pair inventory changed')
    check({0x12c02, 0x1979e} <= {r['access'] for r in loads}, 'reviewed queue/NV anchors')
    c = NVProbe(image)
    count = 0
    for source in (0, 0x22000000, MASK):
        for words in (0, 1, 2, 0x3fffffff, 0x40000000, 0x40000001, MASK):
            for destination in (0, 0x2000c03b, MASK):
                for pointer in (0, 0x30000000, 0x30000101, 0x19bf1):
                    wrapper_case(c, source, words, destination, pointer)
                    count += 1
    # Scanner negative control: turn the reviewed C.LW into a C.SW candidate.
    mutant = bytearray(image)
    off = 0x1979e-BASE
    check(mutant[off:off+2] == bytes.fromhex('fc47'), 'slot-load mutation pin')
    mutant[off+1] ^= 0x80
    changed = scan_slot(mutant)
    check(len([r for r in changed if r['kind'] == 'load']) == 40 and
          [r['access'] for r in changed if r['kind'] == 'store'] == [0x1979e], 'scanner store control')
    # Wrapper negative control: word count becomes words<<1 instead of <<2.
    mutant = bytearray(image)
    off = 0x197a6-BASE
    check(mutant[off:off+4] == bytes.fromhex('13962500'), 'length mutation pin')
    mutant[off:off+4] = bytes.fromhex('13961500')
    try:
        wrapper_case(NVProbe(mutant), 0x22000000, 1, 0x2000c03b, 0x30000001)
    except RuntimeError as exc:
        check(str(exc) == 'NV provider arguments', 'unexpected NV mutation failure')
    else:
        raise RuntimeError('length mutation undetected')
    print(f'PASS: {len(loads)} adjacent load candidates; {len(stores)} adjacent word-store candidates; {count} NV-wrapper boundary cases; fresh-pointer reload; 2 mutation controls')
    print('Candidate load addresses: '+', '.join(hex(r['access']) for r in loads))


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
