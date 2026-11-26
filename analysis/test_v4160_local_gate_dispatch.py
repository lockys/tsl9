"""Original clear/readiness leaves and 12a08 dispatch, with explicit probe return.
No allocator, TX, hardware handler or physical peripheral operation executes.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from test_v4160_consumer_classify_cpu import Classification, snapshot, classify, FIRST
from test_v4160_queue_filter_cpu import TABLE, table_bytes, execute_filter
from test_v4160_consumer_detach_cpu import fixture, CALLBACK, FRAME_SP
from test_v4160_reference_copy_cpu import CARRIER, CARRIER_HASH, APP_HASH, BODY_HASH, RAM, CONTROL, CONTROL_INITIAL
from test_v4160_tx_entry_cpu import GP, CONFIG
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, STACK, RETURN, MASK, check

CLEAR, GATE, DISPATCH, PROBE, HW, TX, NEXT_HANDLER = 0x820c, 0x821e, 0x12a08, 0x81aa, 0x18ca4, 0x16b7c, 0x9454
STATE, ROW, INITIAL_SP = GP+192, STACK+0x300, STACK+0x800
SAVED_S0 = 0x11223344


class LocalCPU(Classification):
    CODE_RANGES = Classification.CODE_RANGES+((0x820c, 0x8248), (0x12a08, 0x12a6e))

    def __init__(self, image, body, data=None):
        self.state_reads = []
        super().__init__(image, body, fixture([]) if data is None else data, 0)
        self.regions.append((STATE, bytearray(4), True))

    def mem(self, address, size, value=None):
        result = super().mem(address, size, value)
        if value is None and STATE <= address < STATE+4:
            self.state_reads.append((address, size))
        return result


def prepare(c, index, flags, value):
    c.reg = [0]*32
    c.reg[1], c.reg[2], c.reg[3], c.reg[8], c.reg[10] = RETURN, INITIAL_SP, GP, SAVED_S0, index
    c.mem(STATE, 4, int.from_bytes(bytes([0xcc, value, value, value]), 'little'))
    c.mem(CONFIG+4, 1, flags)
    c.writes.clear()
    c.reads.clear()
    c.state_reads.clear()


def leaf(c, index, flags, value, clearing=False):
    prepare(c, index, flags, value)
    check(c.run(CLEAR if clearing else GATE, {RETURN}) == RETURN, 'local leaf return')
    expected = bytearray([0xcc, value, value, value])
    if clearing:
        if index <= 2:
            expected[index+1] = 0
        check(c.reg[10] == index, 'clear preserves A0')
        check(c.writes == ([(STATE+index+1, 1, 0)] if index <= 2 else []), 'clear write footprint')
        check(not c.reads, 'clear read configuration')
        check(not c.state_reads, 'clear read old state')
    else:
        check(c.reg[10] == int(not flags & 8 and index <= 2 and value < 3), 'gate result')
        check(not c.writes, 'gate wrote memory')
        check(c.reads == [(GP+84, 4), (CONFIG+4, 1)], 'gate configuration order')
        check(c.state_reads == ([(STATE+index+1, 1)] if not flags & 8 and index <= 2 else []), 'gate state-read address')
    check(c.mem(STATE, 4) == int.from_bytes(expected, 'little'), 'local state bytes')
    check(c.reg[1] == RETURN and c.reg[2] == INITIAL_SP and c.reg[8] == SAVED_S0, 'leaf caller state')


def dispatch(c, pointer, row, probe_reply, flags, state):
    entry_sp, resume, original_s0 = c.reg[2], c.reg[1], c.reg[8]
    c.reg[10] = pointer
    c.mem(STATE+1, 3, int.from_bytes(bytes([state, 0xa1, 0xa2]), 'little'))
    c.mem(CONFIG+4, 1, flags)
    c.writes.clear()
    c.reads.clear()
    c.state_reads.clear()
    expected = RETURN if (not probe_reply and int.from_bytes(row[:2], 'little') != 1) or flags & 8 or state >= 3 else (HW if row[11] == 0 else TX)
    pc, probes, copies = DISPATCH, 0, 0
    for _ in range(4):
        stop = c.run(pc, {PROBE, RAM, HW, TX, resume})
        if stop == PROBE:
            check(c.reg[1] == 0x12a14, 'dispatch probe link')
            probes += 1
            for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
                c.put(reg, 0xcafe0000+reg*0x101)
            c.put(10, probe_reply)
            pc = 0x12a14
        elif stop == RAM:
            check(c.reg[10:13] == [entry_sp-48+23, pointer+3, row[2]], 'dispatch copy arguments')
            c.run_reference(0x12a50)
            copies += 1
            pc = 0x12a50
        else:
            break
    else:
        raise RuntimeError('dispatch budget')
    actual = RETURN if stop == resume else stop
    check(actual == expected and probes == 1, 'record dispatch route')
    frame_sp = entry_sp-48
    writes = [(frame_sp+40, 4, original_s0), (frame_sp+44, 4, resume)]
    if actual == HW:
        check(c.reg[10:12] == [0x40006400, frame_sp+12] and c.reg[1] == 0x12a5e, 'dispatch hardware boundary')
        writes += [(frame_sp+20, 2, 0), (frame_sp+12, 4, int.from_bytes(row[:2], 'little')), (frame_sp+22, 1, row[2]), (CONTROL, 4, 0)]
        writes += [(frame_sp+23+i, 1, byte) for i, byte in enumerate(row[3:3+row[2]])]
        writes.append((CONTROL, 4, CONTROL_INITIAL))
        check(c.mem(frame_sp+16, 4) == 0xcccccccc, 'dispatch record hole was invented')
    elif actual == TX:
        check(c.reg[10] == pointer and c.reg[1] == 0x12a6c, 'dispatch TX boundary')
    else:
        check(c.reg[2] == entry_sp and c.reg[1] == resume and c.reg[8] == original_s0, 'dispatch early caller restoration')
    check(copies == int(actual == HW) and c.writes == writes, 'dispatch store footprint')
    gate_used = bool(probe_reply) or int.from_bytes(row[:2], 'little') == 1
    check(c.reads == ([(GP+84, 4), (CONFIG+4, 1)] + ([(0x4004c, 4)] if actual == HW else []) if gate_used else []), 'dispatch configuration/slot reads')
    check(c.state_reads == ([(STATE+1, 1)] if gate_used and not flags & 8 else []), 'dispatch gate index zero')
    check(c.mem(pointer, 12) == int.from_bytes(row, 'little') and c.mem(CONTROL, 4) == CONTROL_INITIAL and not c.calls, 'dispatch source/control preserved')


def standalone(image, body, ident, tag, length, probe_reply, flags, state):
    c = LocalCPU(image, body)
    c.regions[2][1][:] = bytes([0xcc])*0x1000
    c.reg[1], c.reg[2], c.reg[3], c.reg[8] = RETURN, INITIAL_SP, GP, SAVED_S0
    row = ident.to_bytes(2, 'little')+bytes([length, *range(0xa0, 0xa8), tag])
    c.mem(ROW, 12, int.from_bytes(row, 'little'))
    dispatch(c, ROW, row, probe_reply, flags, state)


def consumer_clear(image, body, parameter):
    row = snapshot(parameter=parameter)
    data = fixture([])
    data[17*12:17*12+12] = row
    c = LocalCPU(image, body, data)
    c.regions.append((TABLE, table_bytes(((0xfffe, 1, 0), (0xfffe, 1, 0))), True))
    c.mem(STATE, 4, int.from_bytes(bytes([0xcc, parameter, 0xa1, 0xa2]), 'little'))
    check(c.advance() == CALLBACK, 'clear consumer entry')
    execute_filter(c)
    check(c.reg[10] == 0 and classify(c, row, 0) == FIRST, 'clear classification entry')
    c.writes.clear()
    check(c.run(FIRST, {NEXT_HANDLER}) == NEXT_HANDLER, 'clear next handler')
    check(c.reg[10] == parameter and c.reg[1] == 0x12d1a and c.reg[2] == FRAME_SP, 'clear parameter handoff')
    check(c.writes == [(STATE+1, 1, 0)] and c.mem(STATE, 4) == int.from_bytes(bytes([0xcc, 0, 0xa1, 0xa2]), 'little'), 'clear actual index zero')


def verify(image, carrier):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'candidate identity')
    check(carrier[0x4c:0x50] == RAM.to_bytes(4, 'little'), 'candidate slot')
    body = carrier[0x5a2:0x5dc]
    check(len(body) == 58 and sha256(body).hexdigest() == BODY_HASH, 'candidate body')
    c = LocalCPU(image, body)
    for index in range(256):
        for value in range(256):
            leaf(c, index, 0, value, clearing=True)
            for flags in (0, 8):
                leaf(c, index, flags, value)
    for index in (0x10000, 0x10001, MASK):
        leaf(c, index, 0, 2, clearing=True)
        leaf(c, index, 0, 2)
    cases = 0
    for ident in (0, 1, 0x7ff, 0xffff):
        for tag in (0, 1, 2, 255):
            for length in (0, 4, 8):
                for probe_reply in (0, 1, MASK):
                    for flags in (0, 8):
                        for state in (0, 2, 3, 255):
                            standalone(image, body, ident, tag, length, probe_reply, flags, state)
                            cases += 1
    for parameter in range(256):
        consumer_clear(image, body, parameter)
    for address, before, after, mode in (
        (0x8240, '93b73700', '93b72700', 'gate'),
        (0x12a2c, '8def', '8dcf', 'dispatch'),
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+len(bytes.fromhex(before))] == bytes.fromhex(before), 'local mutation pin')
        mutant[off:off+len(bytes.fromhex(after))] = bytes.fromhex(after)
        try:
            if mode == 'gate':
                leaf(LocalCPU(mutant, body), 0, 0, 2)
            else:
                standalone(mutant, body, 1, 0, 4, 0, 0, 0)
        except RuntimeError as exc:
            check(str(exc) == ('gate result' if mode == 'gate' else 'record dispatch route'), 'unexpected local mutation failure')
        else:
            raise RuntimeError('local mutation undetected')
    print(f'PASS: 65536 clear cases; 131072 readiness cases; 6 full-width probes; {cases} dispatch cases; 256 actual consumer clear/handoff cases; 2 mutations; hardware/TX/allocator NOT executed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--carrier', type=Path, default=CARRIER)
    args = parser.parse_args()
    verify(IMAGE.read_bytes(), args.carrier.read_bytes())
