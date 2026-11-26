"""Original transfer/capture/guard/queue with a pinned SDK reference copy body.

Candidate binding and MMIO inputs are synthetic, not installed-device evidence.
Consumer checks stop at the ID branch, before CSR or any consumer operation.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from test_v4160_reference_copy_cpu import (
    ReferenceCPU, CARRIER, CARRIER_HASH, APP_HASH, BODY_HASH, RAM, CONTROL,
    CONTROL_INITIAL, FENCE,
)
from test_v4160_receive_frame_cpu import Capture
from test_v4160_ingress_queue_chain import ingress, INSERT, REJECT
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, QUEUE, STACK, RETURN, check, fixture, guard

INITIAL_SP = STACK+0x800
FRAME_SP = INITIAL_SP-48
CALLER_S = (0x11223344, 0x55667788, 0x99aabbcc)
MMIO = 0x40010810


class RXReference(ReferenceCPU):
    CODE_RANGES = ((RAM, RAM+58), (0x12bc8, 0x12c24))
    capture = Capture.capture

    def __init__(self, image, body, scenarios, free):
        super().__init__(image, body)
        self.regions[1][1][:] = fixture(free)
        self.regions.append((MMIO, bytearray(8), True))
        self.scenarios = iter(scenarios)
        self.transfers, self.trace = [], []
        self.reg[1], self.reg[2] = RETURN, INITIAL_SP
        for reg, value in zip((8, 9, 18), CALLER_S):
            self.reg[reg] = value


def setup(image, body, ident, length, free, tag=1, replace=None):
    received = [0xaa, 0xbb, ident >> 3, (ident & 7) << 5, 0x23, 0x45, length,
                *range(0xa0, 0xa8)]
    scenarios = [(1, 1, value) for value in received]
    if replace is not None:
        index, pattern = replace
        scenarios[index] = pattern
    c = RXReference(image, body, scenarios, free)
    c.reg[10:12] = [tag, 0x61]
    c.capture()
    values = [value & 255 if first and second else 0 for first, second, value in scenarios]
    frame = bytes(values[2:])
    check(c.mem(FRAME_SP+16, 13) == int.from_bytes(frame, 'little'), 'RX captured frame')
    outgoing = [3, 0x61]+[0]*13
    expected_trace = [(value, first or 255, (second or 255) if first else 0,
                       (arg,) if first else (), int(bool(first and second)))
                      for arg, value, (first, second, _) in zip(outgoing, values, scenarios)]
    check(c.trace == expected_trace and next(c.scenarios, None) is None, 'RX transfer trace')
    check(c.transfers == [(0x16aa2, 3), (0x16aae, 0x61)]+[(0x16ab4, 0)]*13, 'RX call sequence')
    expected_route = not (frame[1] & 0x18) and 1 <= (frame[4] & 15) <= 8
    check((ingress(c) == INSERT) == expected_route, 'RX guard route')
    return c, frame, expected_route


def run_case(image, body, ident, length, free, tag=1, replace=None):
    c, frame, accepted = setup(image, body, ident, length, free, tag, replace)
    before = bytes(fixture(free))
    expected = bytearray(before)
    called = accepted and free < 32
    actual_id = frame[0] << 3 | frame[1] >> 5
    actual_length = frame[4] & 15
    if accepted:
        stop = c.run(INSERT, {RAM, REJECT})
        check(stop == (RAM if called else REJECT), 'RX queue destination')
    if called:
        slot = QUEUE+12*free
        source = FRAME_SP+21
        check(c.reg[10:13] == [slot+3, source, actual_length] and c.reg[1] == 0x12c0e, 'RX reference arguments')
        c.run_reference(0x12c0e)
        effects = [('read', CONTROL, 4, CONTROL_INITIAL), ('write', CONTROL, 4, 0), ('fence.i', FENCE)]
        for i in range(actual_length):
            effects += [('read', source+i, 1, frame[5+i]), ('write', slot+3+i, 1, frame[5+i])]
        effects.append(('write', CONTROL, 4, CONTROL_INITIAL))
        check(c.effects == effects, 'RX reference copy effects')
        check(c.run(0x12c0e, {REJECT}) == REJECT, 'RX producer continuation')
        expected[12*free:12*free+2] = actual_id.to_bytes(2, 'little')
        expected[12*free+2] = actual_length
        expected[12*free+3:12*free+3+actual_length] = frame[5:5+actual_length]
        expected[12*free+11] = tag
        writes = [(a, n, v) for a, n, v in c.writes if QUEUE <= a < QUEUE+384]
        check(writes == [(slot, 2, actual_id), (slot+2, 1, actual_length)] +
              [(slot+3+i, 1, frame[5+i]) for i in range(actual_length)] + [(slot+11, 1, tag)], 'RX queue write order')
        # Later slots are checked by direct S0 setup; this is not a full scan.
        check(guard(image, c.queue(), free, entry=(free == 0)) ==
              (0x12cee if actual_id == 0 else 0x12c96), 'RX slot ID guard')
    else:
        check(not c.effects and not any(QUEUE <= a < QUEUE+384 for a, _, _ in c.writes), 'RX rejection/full queue effects')
    c.capture(REJECT, RETURN)
    check(c.queue() == expected and c.mem(CONTROL, 4) == CONTROL_INITIAL, 'RX final memory')
    check(c.reg[1] == RETURN and c.reg[2] == INITIAL_SP and
          [c.reg[i] for i in (8, 9, 18)] == list(CALLER_S), 'RX restored caller')
    check(not c.calls, 'synthetic one-byte provider executed')
    return c


def zero_reuse(image, body, free):
    c = run_case(image, body, 0, 8, free, 1)
    before = bytearray(c.queue())
    source = STACK+0x100
    c.mem(source, 3, 0x332211)
    c.reg[1] = RETURN
    c.reg[10:14] = [0x123, source, 3, 2]
    check(c.run(INSERT, {RAM, RETURN}) == RAM, 'zero-ID reuse entry')
    check(c.reg[10:13] == [QUEUE+12*free+3, source, 3], 'zero-ID same-slot reuse')
    c.run_reference(0x12c0e)
    c.run(0x12c0e, {RETURN})
    before[12*free:12*free+6] = bytes.fromhex('230103112233')
    before[12*free+11] = 2
    check(c.queue() == before and c.mem(CONTROL, 4) == CONTROL_INITIAL, 'zero-ID reuse result')


def interrupted(image, body, ident):
    free = 17
    c, frame, accepted = setup(image, body, ident, 8, free)
    check(accepted and c.run(INSERT, {RAM}) == RAM, 'partial RX entry')
    c.fail_store = 3
    try:
        c.run_reference(0x12c0e)
    except RuntimeError as exc:
        check(str(exc) == 'synthetic byte-store stop', 'unexpected RX copy stop')
    else:
        raise RuntimeError('RX copy stop absent')
    c.reference_active = False
    expected = fixture(free)
    expected[12*free:12*free+5] = ident.to_bytes(2, 'little')+bytes([8, frame[5], frame[6]])
    check(c.queue() == expected and c.mem(CONTROL, 4) == 0, 'RX interrupted prefix')
    check(c.reg[2] == FRAME_SP-16 and c.effects[-1][0] == 'blocked_store', 'RX interrupted nonreturn')
    check(guard(image, c.queue(), free) == (0x12cee if ident == 0 else 0x12c96), 'RX interrupted snapshot ID guard')


def verify(image, carrier):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'SDK candidate identity')
    check(carrier[0x4c:0x50] == RAM.to_bytes(4, 'little'), 'SDK candidate slot')
    body = carrier[0x5a2:0x5dc]
    check(len(body) == 58 and sha256(body).hexdigest() == BODY_HASH, 'SDK candidate body')
    cases = 0
    for ident in (0, 1, 7, 8, 0x123, 0x3ff, 0x7fe, 0x7ff):
        for length in range(1, 9):
            for free in range(32):
                for tag in (1, 2):
                    run_case(image, body, ident, length, free, tag)
                    cases += 1
    for index in range(15):
        for pattern in ((1, 1, 0), (0, 0, 0xa5), (1, 0, 0xa5)):
            run_case(image, body, 325, 8, 17, replace=(index, pattern))
    for ident in (0, 325):
        for length in (1, 8):
            run_case(image, body, ident, length, 32)
    for free in range(32):
        zero_reuse(image, body, free)
    for ident in (0, 325):
        interrupted(image, body, ident)
    mutant = bytearray(image)
    off = 0x12c0e-BASE
    check(mutant[off:off+4] == bytes.fromhex('a3059400'), 'RX tag mutation pin')
    mutant[off:off+4] = bytes.fromhex('23059400')  # SB tag to +10 rather than +11
    try:
        run_case(mutant, body, 325, 8, 17)
    except RuntimeError as exc:
        check(str(exc) == 'RX queue write order', 'unexpected RX tag mutation failure')
    else:
        raise RuntimeError('RX tag mutation undetected')
    print(f'PASS: {cases} RX/reference/slot/tag cases; 45 zero/timeout substitutions; 4 full queues; 32 zero-ID reuses; 2 interrupted snapshots; tag mutation detected; installed binding UNPROVED')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--carrier', type=Path, default=CARRIER)
    args = parser.parse_args()
    verify(IMAGE.read_bytes(), args.carrier.read_bytes())
