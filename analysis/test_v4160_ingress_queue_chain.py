"""Offline original-instruction ingress/queue chain; stop before opaque provider.

The 13-byte receive frame, queue, and initial registers are synthetic. This does
not execute reception, interrupts, resident code, or a device. Uses only stdlib
and the published bounded queue CPU in the same directory.
"""
from hashlib import sha256
from test_v4160_zero_id_queue_cpu import (
    CPU, IMAGE, BASE, QUEUE, STACK, PROVIDER, MASK, check, fixture, sx,
)

ENTRY, REJECT, INSERT = 0x16acc, 0x16afe, 0x12bc8
DIGEST = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def frame(c, b0, b1, b4, tag=0x12345642):
    c.reg = [0] * 32
    c.reg[2], c.reg[9] = STACK + 0x800, tag
    data = bytes([b0, b1, 0x23, 0x45, b4, *range(0xa0, 0xa8)])
    c.mem(c.reg[2] + 16, 13, int.from_bytes(data, 'little'))
    c.writes.clear()


def ingress(c):
    """Decode only the RV32IC instructions needed by the original guard slice."""
    c.pc = ENTRY
    for _ in range(24):
        p, r = c.pc, c.reg
        if p in (REJECT, INSERT):
            return p
        check(ENTRY <= p < REJECT and not p & 1, 'outside ingress slice')
        h = c.mem(p, 2)
        if h & 3 != 3:
            c.pc = p + 2
            q, f = h & 3, h >> 13
            rd, rs2 = h >> 7 & 31, h >> 2 & 31
            imm = sx((h >> 2 & 31) | (h >> 7 & 32), 6)
            if q == 1 and f == 2:  # C.LI
                c.put(rd, imm)
            elif q == 1 and f == 4:
                d, mode = 8 + (h >> 7 & 7), h >> 10 & 3
                if mode == 0:  # C.SRLI
                    check(not h & 0x1000, 'RV32 shift')
                    c.put(d, r[d] >> (h >> 2 & 31))
                elif mode == 2:  # C.ANDI
                    c.put(d, r[d] & imm)
                elif mode == 3 and not h & 0x1000 and (h >> 5 & 3) == 2:  # C.OR
                    c.put(d, r[d] | r[8 + (h >> 2 & 7)])
                else:
                    raise RuntimeError('unsupported ingress arithmetic')
            elif q == 1 and f in (6, 7):  # C.BEQZ/C.BNEZ
                off = ((h >> 12 & 1) << 8 | (h >> 10 & 3) << 3 |
                       (h >> 5 & 3) << 6 | (h >> 3 & 3) << 1 | (h >> 2 & 1) << 5)
                if (r[8 + (h >> 7 & 7)] == 0) == (f == 6):
                    c.pc = p + sx(off, 9)
            elif q == 2 and f == 0:  # C.SLLI
                check(not h & 0x1000, 'RV32 shift')
                c.put(rd, r[rd] << rs2)
            elif q == 2 and f == 4 and not h & 0x1000 and rs2:  # C.MV
                c.put(rd, r[rs2])
            else:
                raise RuntimeError('unsupported ingress compressed instruction')
        else:
            w = c.mem(p, 4)
            c.pc = p + 4
            op, d, f, a = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31
            imm = sx(w >> 20, 12)
            if op == 3 and f == 4:  # LBU
                c.put(d, c.mem(r[a] + imm, 1))
            elif op == 0x13 and f == 7:  # ANDI
                c.put(d, r[a] & imm)
            elif op == 0x13 and f == 0:  # ADDI
                c.put(d, r[a] + imm)
            elif op == 0x63 and f in (6, 7):  # BLTU/BGEU (latter for negative control)
                off = ((w >> 31) << 12 | (w >> 7 & 1) << 11 |
                       (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
                if (r[a] < r[w >> 20 & 31]) == (f == 6):
                    c.pc = p + sx(off, 13)
            elif op == 0x6f:  # JAL
                off = ((w >> 31) << 20 | (w >> 12 & 255) << 12 |
                       (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1)
                c.put(d, p + 4)
                c.pc = p + sx(off, 21)
            else:
                raise RuntimeError('unsupported ingress instruction')
    raise RuntimeError('ingress budget exceeded')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == DIGEST, 'image identity')
    c = CPU(image, fixture(0))
    accepted = 0
    for b1 in range(256):
        for b4 in range(256):
            frame(c, 0xa5, b1, b4)
            target = ingress(c)
            expect = not (b1 & 0x18) and 1 <= (b4 & 15) <= 8
            check((target == INSERT) == expect, 'flag/length domain')
            check(not c.writes, 'ingress guard wrote memory')
            if expect:
                check(c.reg[10:14] == [(0xa5 << 3) | (b1 >> 5), c.reg[2]+21, b4 & 15, 0x12345642], 'ingress arguments')
                check(c.reg[1] == REJECT, 'ingress link')
                accepted += 1
    check(accepted == 8192, 'accepted flag/length count')
    counts = [0] * 2048
    for b0 in range(256):
        for b1 in range(256):
            frame(c, b0, b1, 1)
            if ingress(c) == INSERT:
                ident = (b0 << 3) | (b1 >> 5)
                check(c.reg[10] == ident, 'header ID projection')
                counts[ident] += 1
    check(counts == [8] * 2048, 'ID multiplicity')
    chained = 0
    for ident in range(2048):
        free = ident % 32
        for length in range(1, 9):
            before = fixture(free)
            c = CPU(image, before)
            frame(c, ident >> 3, (ident & 7) << 5, 0xf0 | length)
            check(ingress(c) == INSERT, 'chain ingress')
            source = c.reg[2] + 21
            check(c.run(INSERT, {PROVIDER, REJECT}) == PROVIDER, 'chain provider entry')
            expected = bytearray(before)
            expected[12*free:12*free+2] = ident.to_bytes(2, 'little')
            expected[12*free+2] = length
            check(c.queue() == expected, 'chain pre-provider stores')
            check(c.reg[10:13] == [QUEUE + 12*free+3, source, length], 'chain call arguments')
            check(c.mem(source, length) == int.from_bytes(bytes(range(0xa0, 0xa0+length)), 'little'), 'payload stays within eight frame bytes')
            check(not c.calls, 'opaque provider executed')
            chained += 1
    # Check full queue without executing either the provider or ingress epilogue.
    for length in range(1, 9):
        before = fixture(32)
        c = CPU(image, before)
        frame(c, 0, 0, length)
        check(ingress(c) == INSERT, 'zero ID ingress accepted')
        check(c.run(INSERT, {PROVIDER, REJECT}) == REJECT, 'full queue chain return')
        check(c.queue() == before and not c.calls, 'full queue chain side effects')
    # Mutate branch polarity in memory; zero length must now incorrectly pass.
    mutant = bytearray(image)
    off = 0x16ae6 - BASE
    check(mutant[off:off+4] == bytes.fromhex('63ece600'), 'branch mutation pin')
    mutant[off+1] ^= 0x10  # BLTU -> BGEU
    c = CPU(mutant, fixture(0))
    frame(c, 0, 0, 0)
    check(ingress(c) == INSERT, 'length branch mutation control')
    print(f'PASS: 65536 flag/length pairs ({accepted} accepted); 65536 headers (2048 IDs x 8); {chained} ingress-to-provider cases; 8 full queues; branch mutation detected')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
