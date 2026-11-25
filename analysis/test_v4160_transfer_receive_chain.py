"""Offline original transfer -> capture -> guard -> queue execution.

Only status/data inputs are synthetic. Execute 0x16896 with the SAME registers
as its caller; never execute the opaque queue provider or access real MMIO.
"""
from hashlib import sha256
from test_v4160_receive_frame_cpu import Capture, IDENTITY, TRANSFER, MMIO
from test_v4160_ingress_queue_chain import ingress, INSERT, REJECT
from test_v4160_zero_id_queue_cpu import (
    IMAGE, BASE, STACK, QUEUE, PROVIDER, RETURN, MASK, check, fixture, sx,
)

STATUS, DATA = 0x40013008, 0x4001300c


class Integrated(Capture):
    def __init__(self, image, scenarios, **kwargs):
        super().__init__(image, [], **kwargs)
        self.scenarios = iter(scenarios)
        self.trace = []

    def transfer(self):
        first, second, received = next(self.scenarios)
        check(0 <= first <= 255 and 0 <= second <= 255, 'scenario readiness')
        r = self.reg
        resume, outgoing = r[1], r[10]
        preserved = {i: r[i] for i in range(32) if i not in (10, 13, 14, 15)}
        self.transfers.append((resume, outgoing))
        reads, writes, data_reads = [0, 0], [], 0
        self.pc = TRANSFER
        for _ in range(5000):
            p = self.pc
            if p == resume:
                check(all(r[i] == value for i, value in preserved.items()), 'transfer preservation')
                self.trace.append((r[10], *reads, tuple(writes), data_reads))
                return
            check(TRANSFER <= p < 0x168de and not p & 1, 'outside transfer slice')
            h = self.mem(p, 2)
            if h & 3 != 3:
                self.pc = p + 2
                q, f, d = h & 3, h >> 13, h >> 7 & 31
                imm = sx((h >> 2 & 31) | (h >> 7 & 32), 6)
                if q == 1 and f in (0, 2):  # C.ADDI/C.LI
                    self.put(d, (r[d] if f == 0 else 0) + imm)
                elif q == 1 and f == 4 and (h >> 10 & 3) == 2:  # C.ANDI
                    d = 8 + (h >> 7 & 7)
                    self.put(d, r[d] & imm)
                elif q == 1 and f == 4 and (h >> 10 & 3) == 0:  # C.SRLI
                    check(not h & 0x1000, 'RV32 shift')
                    d = 8 + (h >> 7 & 7)
                    self.put(d, r[d] >> (h >> 2 & 31))
                elif q == 2 and f == 0:  # C.SLLI
                    check(not h & 0x1000, 'RV32 shift')
                    self.put(d, r[d] << (h >> 2 & 31))
                elif q == 1 and f in (6, 7):
                    off = ((h >> 12 & 1) << 8 | (h >> 10 & 3) << 3 |
                           (h >> 5 & 3) << 6 | (h >> 3 & 3) << 1 | (h >> 2 & 1) << 5)
                    if (r[8 + (h >> 7 & 7)] == 0) == (f == 6):
                        self.pc = p + sx(off, 9)
                elif q == 1 and f == 5:  # C.J
                    off = ((h >> 12 & 1) << 11 | (h >> 11 & 1) << 4 |
                           (h >> 9 & 3) << 8 | (h >> 8 & 1) << 10 |
                           (h >> 7 & 1) << 6 | (h >> 6 & 1) << 7 |
                           (h >> 3 & 7) << 1 | (h >> 2 & 1) << 5)
                    self.pc = p + sx(off, 12)
                elif h == 0x8082:
                    self.pc = r[1] & ~1
                else:
                    raise RuntimeError('unsupported transfer compressed instruction')
            else:
                w = self.mem(p, 4)
                self.pc = p + 4
                op, d, f, a, b = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
                imm = sx(w >> 20, 12)
                if op == 0x37:
                    self.put(d, w & 0xfffff000)
                elif op == 0x13 and f in (0, 7):
                    self.put(d, r[a] + imm if f == 0 else r[a] & imm)
                elif op == 3 and f == 5:  # LHU, synthetic status/data source
                    address = (r[a] + imm) & MASK
                    if address == STATUS:
                        phase = int(bool(writes))
                        reads[phase] += 1
                        position, bit = (first, 2) if phase == 0 else (second, 1)
                        self.put(d, 0xfffc | (bit if position and reads[phase] == position else 0))
                    elif address == DATA and writes:
                        self.put(d, received & 0xffff)
                        data_reads += 1
                    else:
                        raise RuntimeError('unexpected transfer LHU')
                elif op == 0x23 and f == 1:  # SH
                    off = sx((w >> 25 << 5) | (w >> 7 & 31), 12)
                    check((r[a]+off) & MASK == DATA and not writes, 'unexpected transfer SH')
                    writes.append(r[b] & 0xffff)
                else:
                    raise RuntimeError('unsupported transfer instruction')
        raise RuntimeError('transfer budget exceeded')


def run_scene(image, scenarios, full=False):
    check(len(scenarios) == 15, '15 scenarios required')
    c = Integrated(image, scenarios, command=0x12345678, full=full)
    c.capture()
    expected_trace = []
    values = []
    for index, (first, second, received) in enumerate(scenarios):
        outgoing = (3, 0x12345678)[index] if index < 2 else 0
        value = received & 255 if first and second else 0
        values.append(value)
        expected_trace.append((value, first or 255, (second or 255) if first else 0,
                               (outgoing & 0xffff,) if first else (), int(bool(first and second))))
    check(c.trace == expected_trace, 'transfer trace')
    check(c.transfers == [(0x16aa2, 3), (0x16aae, 0x12345678)] + [(0x16ab4, 0)]*13, 'transfer call sequence')
    sp = STACK + 0x800 - 48
    frame = bytes(values[2:])
    check(c.mem(sp+16, 13) == int.from_bytes(frame, 'little'), 'actual transfer frame')
    check([(a, n, v) for a, n, v in c.writes if n == 1] == [(sp+16+i, 1, v) for i, v in enumerate(frame)], 'frame store sequence')
    check([(a, n, v) for a, n, v in c.writes if MMIO <= a < MMIO+8] == [(MMIO+4, 4, 16), (MMIO, 4, 17)], 'capture MMIO sequence')
    accepted = not (frame[1] & 0x18) and 1 <= (frame[4] & 15) <= 8
    check((ingress(c) == INSERT) == accepted, 'actual transfer route')
    if accepted:
        ident, length = frame[0] << 3 | frame[1] >> 5, frame[4] & 15
        check(c.reg[10:14] == [ident, sp+21, length, 1], 'actual transfer queue arguments')
        check(c.run(INSERT, {PROVIDER, REJECT}) == (REJECT if full else PROVIDER), 'actual transfer queue destination')
        expected_queue = fixture(32 if full else 0)
        if not full:
            expected_queue[:3] = ident.to_bytes(2, 'little') + bytes([length])
            check(c.reg[10:13] == [QUEUE+3, sp+21, length], 'actual transfer provider arguments')
            check(c.mem(sp+21, length) == int.from_bytes(frame[5:5+length], 'little'), 'provider source bytes')
        check(c.queue() == expected_queue, 'actual transfer queue writes')
    else:
        check(c.queue() == fixture(32 if full else 0), 'rejected frame queue unchanged')
    if not accepted or full:
        c.capture(REJECT, RETURN)
        check(c.reg[2] == STACK+0x800 and c.reg[1] == RETURN, 'final SP/RA')
        check([c.reg[i] for i in (8, 9, 18)] == [0x11223344, 0x55667788, 0x99aabbcc], 'final callee-saved state')
    check(not c.calls, 'opaque provider executed')
    return c, frame


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'image identity')
    # Valid received frame: ID=325, length=8, eight payload bytes.
    data = [0xaa, 0xbb, 0x28, 0xa0, 0x23, 0x45, 8, *range(0xa0, 0xa8)]
    baseline = [(1, 1, 0xab00 | v) for v in data]
    readiness = 0
    for phase in (0, 1):
        for position in range(1, 256):
            scenarios = baseline.copy()
            index = (position-1) % 15
            one = list(scenarios[index])
            one[phase] = position
            scenarios[index] = tuple(one)
            run_scene(image, scenarios)
            readiness += 1
    substitutions = 0
    for index in range(15):
        observations = []
        for replacement in ((1, 1, 0), (0, 0, 0xa5), (1, 0, 0xa5)):
            scenarios = baseline.copy()
            scenarios[index] = replacement
            c, frame = run_scene(image, scenarios)
            observations.append((frame, c.queue()))
            substitutions += 1
        check(observations[0] == observations[1] == observations[2], 'zero-source caller equivalence')
    for pattern in ((1, 1, 0), (0, 0, 0xa5), (1, 0, 0xa5)):
        _, frame = run_scene(image, [pattern]*15)
        check(frame == bytes(13), 'all-zero frame')
    for length in range(1, 9):
        scenarios = baseline.copy()
        scenarios[6] = (255, 255, length)
        run_scene(image, scenarios)
    run_scene(image, baseline, full=True)
    mutations = ((0x168a2, '098b', '058b'), (0x168ba, '058b', '098b'),
                 (0x16896, '9307f00f', '9307e00f'))
    for address, before, after in mutations:
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+len(bytes.fromhex(before))] == bytes.fromhex(before), 'mutation pin')
        mutant[off:off+len(bytes.fromhex(after))] = bytes.fromhex(after)
        scenarios = baseline.copy()
        scenarios[0] = (255, 1, 0xaa)
        try:
            run_scene(mutant, scenarios)
        except RuntimeError as exc:
            check(str(exc) == 'transfer trace', 'unexpected mutation failure')
        else:
            raise RuntimeError('transfer mutation undetected')
    print(f'PASS: {readiness} readiness-position chain cases; {substitutions} zero/timeout substitutions; 3 all-zero paths; 8 lengths; full queue; 3 instruction mutations detected')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
