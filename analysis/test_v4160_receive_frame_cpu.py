"""Execute bounded original capture instructions with prescribed transfer returns.

No peripheral or resident implementation executes. MMIO is synthetic writable
memory; transfer hooks preserve SP, callee-saved registers and memory, deliberately
clobber caller-saved registers, and supply explicitly chosen A0 return values.
"""
from hashlib import sha256
from test_v4160_zero_id_queue_cpu import (
    CPU, IMAGE, BASE, STACK, QUEUE, PROVIDER, RETURN, MASK, check, fixture, sx,
)
from test_v4160_ingress_queue_chain import ingress, INSERT, REJECT

ENTRY, GUARD, TRANSFER = 0x16a7c, 0x16acc, 0x16896
MMIO = 0x40010810
IDENTITY = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


class Capture(CPU):
    def __init__(self, image, returns, channel=1, command=0x12345678, full=False):
        super().__init__(image, fixture(32 if full else 0))
        self.regions.append((MMIO, bytearray(8), True))
        self.reg[8], self.reg[9], self.reg[18] = 0x11223344, 0x55667788, 0x99aabbcc
        self.reg[10:12] = [channel, command]
        self.returns = iter(returns)
        self.transfers = []

    def capture(self, start=ENTRY, stop=GUARD):
        self.pc = start
        for _ in range(1000):
            p, r = self.pc, self.reg
            if p == stop:
                return
            if p == TRANSFER:
                self.transfers.append((r[1], r[10]))
                resume = r[1]
                value = next(self.returns)
                for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
                    self.put(reg, 0xbaba0000 + reg * 0x101)
                self.put(10, value)
                self.pc = resume
                continue
            check((ENTRY <= p < GUARD or REJECT <= p < 0x16b0a) and not p & 1, 'outside capture slice')
            h = self.mem(p, 2)
            if h & 3 != 3:
                self.pc = p + 2
                q, f = h & 3, h >> 13
                rd, rs2 = h >> 7 & 31, h >> 2 & 31
                imm = sx((h >> 2 & 31) | (h >> 7 & 32), 6)
                if q == 1 and f == 0:  # C.ADDI
                    self.put(rd, r[rd] + imm)
                elif q == 1 and f == 2:  # C.LI
                    self.put(rd, imm)
                elif q == 1 and f == 3 and rd == 2:  # C.ADDI16SP
                    v = ((h >> 12 & 1) << 9 | (h >> 6 & 1) << 4 |
                         (h >> 5 & 1) << 6 | (h >> 3 & 3) << 7 | (h >> 2 & 1) << 5)
                    self.put(2, r[2] + sx(v, 10))
                elif q == 2 and f == 6:  # C.SWSP
                    off = (h >> 9 & 15) << 2 | (h >> 7 & 3) << 6
                    self.mem(r[2] + off, 4, r[rs2])
                elif q == 2 and f == 2:  # C.LWSP
                    off = (h >> 12 & 1) << 5 | (h >> 4 & 7) << 2 | (h >> 2 & 3) << 6
                    self.put(rd, self.mem(r[2] + off, 4))
                elif q == 0 and f == 6:  # C.SW
                    off = (h >> 10 & 7) << 3 | (h >> 6 & 1) << 2 | (h >> 5 & 1) << 6
                    self.mem(r[8 + (h >> 7 & 7)] + off, 4, r[8 + (h >> 2 & 7)])
                elif q == 0 and f == 0:  # C.ADDI4SPN
                    off = ((h >> 11 & 3) << 4 | (h >> 7 & 15) << 6 |
                           (h >> 6 & 1) << 2 | (h >> 5 & 1) << 3)
                    check(off != 0, 'reserved C.ADDI4SPN')
                    self.put(8 + (h >> 2 & 7), r[2] + off)
                elif q == 2 and f == 4:
                    if rs2:
                        self.put(rd, r[rd] + r[rs2] if h & 0x1000 else r[rs2])
                    elif not h & 0x1000 and rd:
                        self.pc = r[rd] & ~1
                    else:
                        raise RuntimeError('unsupported capture jump')
                else:
                    raise RuntimeError('unsupported capture compressed instruction')
            else:
                w = self.mem(p, 4)
                self.pc = p + 4
                op, rd, f, a, b = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
                imm = sx(w >> 20, 12)
                if op == 0x37:  # LUI
                    self.put(rd, w & 0xfffff000)
                elif op == 0x13 and f == 0:  # ADDI
                    self.put(rd, r[a] + imm)
                elif op == 0x23 and f in (0, 2):  # SB/SW
                    off = sx((w >> 25 << 5) | (w >> 7 & 31), 12)
                    self.mem(r[a] + off, {0: 1, 2: 4}[f], r[b])
                elif op == 0x63 and f == 1:  # BNE
                    off = ((w >> 31) << 12 | (w >> 7 & 1) << 11 |
                           (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                    if r[a] != r[b]:
                        self.pc = p + sx(off, 13)
                elif op == 0x6f:  # JAL
                    off = ((w >> 31) << 20 | (w >> 12 & 255) << 12 |
                           (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1)
                    self.put(rd, p + 4)
                    self.pc = p + sx(off, 21)
                else:
                    raise RuntimeError('unsupported capture instruction')
        raise RuntimeError('capture budget exceeded')


def run_case(image, values, channel=1, command=0x12345678, preliminary=(MASK, 0xfeedbeef), full=False):
    c = Capture(image, [*preliminary, *values], channel, command, full)
    c.capture()
    sp = STACK + 0x800 - 48
    expected = bytes(value & 255 for value in values)
    check(len(expected) == 13, 'test frame size')
    check(c.reg[2] == sp and c.reg[9] == channel and c.reg[8] == 13 and c.reg[18] == 13, 'capture state')
    check(c.transfers == [(0x16aa2, 3), (0x16aae, command)] + [(0x16ab4, 0)] * 13, '15 transfer call arguments')
    check(c.mem(sp+16, 13) == int.from_bytes(expected, 'little'), '13 captured bytes')
    stores = [(addr, size, value) for addr, size, value in c.writes if size == 1]
    check(stores == [(sp+16+i, 1, b) for i, b in enumerate(expected)], 'capture write boundaries/order')
    mmio = [(addr, size, value) for addr, size, value in c.writes if MMIO <= addr < MMIO+8]
    check(mmio == [(MMIO+4, 4, 16 if channel == 1 else 1), (MMIO, 4, 17)], 'synthetic MMIO write sequence')
    check(c.queue() == fixture(32 if full else 0), 'capture must not write queue')
    target = ingress(c)
    accepted = not (expected[1] & 0x18) and 1 <= (expected[4] & 15) <= 8
    check((target == INSERT) == accepted, 'captured frame routing')
    if accepted:
        ident, length = expected[0] << 3 | expected[1] >> 5, expected[4] & 15
        check(c.reg[10:14] == [ident, sp+21, length, channel], 'capture-to-ingress arguments')
        stop = c.run(INSERT, {PROVIDER, REJECT})
        check(stop == (REJECT if full else PROVIDER), 'queue stop')
        if not full:
            queue = fixture(0)
            queue[:3] = ident.to_bytes(2, 'little') + bytes([length])
            check(c.queue() == queue, 'capture-to-queue writes')
            check(c.reg[10:13] == [QUEUE+3, sp+21, length], 'provider arguments')
        else:
            check(c.queue() == fixture(32), 'full queue changed')
    if not accepted or full:
        c.capture(REJECT, RETURN)
        check(c.reg[2] == STACK+0x800 and c.reg[1] == RETURN, 'caller SP/RA restoration')
        check([c.reg[i] for i in (8, 9, 18)] == [0x11223344, 0x55667788, 0x99aabbcc], 'caller saved-register restoration')
    check(not c.calls, 'opaque provider executed')
    return c


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'image identity')
    base = [0x28, 0xa0, 0x23, 0x45, 8, *range(0xa0, 0xa8)]
    count = 0
    for index in range(13):
        for value in range(256):
            values = base.copy()
            values[index] = 0xdeadbe00 | value
            run_case(image, values)
            count += 1
    channels = 0
    for channel in (0, 1, 2, 0x10001, MASK):
        for command in (0, 1, MASK):
            run_case(image, base, channel, command)
            channels += 1
    run_case(image, [0]*13)
    zero_id = [0]*13
    zero_id[4] = 1
    run_case(image, zero_id)
    run_case(image, zero_id, full=True)
    # Negative control in memory only: reduce the loop bound from 13 to 12.
    mutant = bytearray(image)
    off = 0x16aa6 - BASE
    check(mutant[off:off+2] == bytes.fromhex('3549'), 'loop mutation pin')
    mutant[off:off+2] = bytes.fromhex('3149')
    try:
        run_case(mutant, base)
    except RuntimeError as exc:
        check(str(exc) == 'capture state', 'unexpected mutation failure')
    else:
        raise RuntimeError('loop mutation not detected')
    print(f'PASS: {count} per-position byte cases; {channels} channel/command cases; all-zero rejection; zero-ID call; full-queue return; 13-to-12 loop mutation detected')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
