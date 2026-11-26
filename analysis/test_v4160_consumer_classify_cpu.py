"""Original filter-zero classification and response record construction.

Large matrices start from an explicit post-filter state; smaller compositions
execute consumer detach and actual empty-table filter first. Handlers do not run.
81aa may receive a declared synthetic normal return to test its branch only.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from test_v4160_queue_filter_cpu import FilterConsumer, TABLE, table_bytes, execute_filter
from test_v4160_consumer_detach_cpu import fixture, CALLBACK, FRAME_SP, INITIAL_SP, S_REGS, S_VALUES
from test_v4160_reference_copy_cpu import CARRIER, CARRIER_HASH, APP_HASH, BODY_HASH, RAM, CONTROL, CONTROL_INITIAL, FENCE
from test_v4160_tx_entry_cpu import GP, CONFIG
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, QUEUE, RETURN, MASK, check

NEXT, FIRST, RESPONSE, PROBE, OTHER = 0x12cee, 0x820c, 0x12a08, 0x81aa, 0x14d2e


class Classification(FilterConsumer):
    CODE_RANGES = FilterConsumer.CODE_RANGES+((0x12cb4, 0x12cee), (0x12d0e, 0x12d92))


def snapshot(ident=1, length=4, p0=0xb5, p1=0x62, opcode=0, parameter=0x55):
    return ident.to_bytes(2, 'little')+bytes([length, p0, p1, opcode, parameter, 0xa4, 0xa5, 0xa6, 0xa7, 2])


def expected_route(row, flags, ready, filter_result=0):
    if filter_result:
        return NEXT
    if int.from_bytes(row[:2], 'little') == 1:
        if row[2] != 4 or row[3:5] != bytes.fromhex('b562'):
            return NEXT
        if row[5] == 0:
            return FIRST
        return RESPONSE if row[5:7] == bytes.fromhex('5a55') else NEXT
    return OTHER if not flags & 8 and ready else NEXT


def classify(c, row, ready):
    pc = 0x12cb4
    write_start = len(c.writes)
    read_start, filter_result = len(c.reads), c.reg[10]
    c.response_copies = 0
    c.probe_calls = 0
    for _ in range(4):
        stop = c.run(pc, {NEXT, FIRST, RESPONSE, PROBE, OTHER, RAM})
        if stop == RAM:
            check(c.reg[10:13] == [FRAME_SP+20, FRAME_SP+8, 12] and c.reg[1] == 0x12d64, 'classification response copy arguments')
            c.run_reference(0x12d64)
            c.response_copies += 1
            pc = 0x12d64
        elif stop == PROBE:
            check(c.reg[1] == 0x12d88, 'classification probe link')
            c.probe_calls += 1
            for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
                c.put(reg, 0xbeef0000+reg*0x101)
            c.put(10, ready)
            pc = 0x12d88
        else:
            if stop == FIRST:
                check(c.reg[1] == 0x12d12, 'classification first-handler link')
            elif stop == RESPONSE:
                expected = bytearray(row)
                expected[6], expected[11] = 0x56, 0
                check(c.reg[10] == FRAME_SP+20 and c.reg[1] == 0x12d76 and
                      c.mem(FRAME_SP+20, 12) == int.from_bytes(expected, 'little'), 'classification response record')
            elif stop == OTHER:
                check(c.reg[10] == FRAME_SP+8 and c.reg[1] == 0x12d90, 'classification other-handler argument')
            expected_writes = []
            if stop == RESPONSE:
                expected_effects = [('read', CONTROL, 4, CONTROL_INITIAL), ('write', CONTROL, 4, 0), ('fence.i', FENCE)]
                expected_writes.append((CONTROL, 4, 0))
                for i, byte in enumerate(row):
                    expected_effects += [('read', FRAME_SP+8+i, 1, byte), ('write', FRAME_SP+20+i, 1, byte)]
                    expected_writes.append((FRAME_SP+20+i, 1, byte))
                expected_effects.append(('write', CONTROL, 4, CONTROL_INITIAL))
                expected_writes += [(CONTROL, 4, CONTROL_INITIAL), (FRAME_SP+26, 1, 0x56), (FRAME_SP+31, 1, 0)]
                check(c.effects == expected_effects, 'classification response copy effects')
            check(c.writes[write_start:] == expected_writes, 'classification write footprint')
            config_reads = [item for item in c.reads[read_start:] if item[0] in (GP+84, CONFIG+4)]
            expected_config = [] if filter_result or int.from_bytes(row[:2], 'little') == 1 else [(GP+84, 4), (CONFIG+4, 1)]
            check(config_reads == expected_config, 'classification configuration-read scope')
            check(c.mem(FRAME_SP+8, 12) == int.from_bytes(row, 'little'), 'classification snapshot preserved')
            return stop
    raise RuntimeError('classification budget')


def route_probe(c, row, flags=0, ready=0, filter_result=0):
    # Explicit state from just after a normally-returning zero filter. No claim
    # that all independently constructed rows are reachable from an RX ingress.
    c.reg = [0]*32
    c.reg[1], c.reg[2], c.reg[3] = RETURN, FRAME_SP, GP
    c.reg[19], c.reg[20], c.reg[23], c.reg[10] = 0x40000, 1, GP+84, filter_result
    c.mem(FRAME_SP+8, 12, int.from_bytes(row, 'little'))
    c.mem(CONFIG+4, 1, flags)
    c.effects.clear()
    c.reads.clear()
    c.writes.clear()
    actual = classify(c, row, ready)
    check(actual == expected_route(row, flags, ready, filter_result), 'classification route')
    expected_probe = not filter_result and int.from_bytes(row[:2], 'little') != 1 and not flags & 8
    check(c.probe_calls == int(expected_probe), 'classification probe count')
    check(c.response_copies == int(actual == RESPONSE), 'classification response copy count')
    check(c.mem(CONTROL, 4) == CONTROL_INITIAL and not c.calls, 'classification reference control')


def composed(image, body, row, flags=0, ready=0):
    data = fixture([])
    data[17*12:17*12+12] = row
    c = Classification(image, body, data, 0)
    c.regions.append((TABLE, table_bytes(((0xfffe, 1, 0), (0xfffe, 1, 0))), True))
    c.mem(CONFIG+4, 1, flags)
    check(c.advance() == CALLBACK, 'classification consumer callback')
    execute_filter(c)
    check(c.reg[10] == 0 and not c.requests, 'classification actual zero filter')
    actual = classify(c, row, ready)
    check(actual == expected_route(row, flags, ready), 'classification composed route')
    data[17*12:17*12+2] = bytes(2)
    check(c.queue() == data and c.csr == 0x88 and c.mem(CONTROL, 4) == CONTROL_INITIAL, 'classification detached queue')
    if actual == NEXT:
        c.scan_start = NEXT
        check(c.advance() == RETURN and c.reg[2] == INITIAL_SP and
              [c.reg[r] for r in S_REGS] == list(S_VALUES), 'classification skip/return')
    else:
        check(c.reg[2] == FRAME_SP, 'classification handler frame')


def verify(image, carrier):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'candidate identity')
    check(carrier[0x4c:0x50] == RAM.to_bytes(4, 'little'), 'candidate slot')
    body = carrier[0x5a2:0x5dc]
    check(len(body) == 58 and sha256(body).hexdigest() == BODY_HASH, 'candidate body')
    c = Classification(image, body, fixture([]), 0)
    for length in range(256):
        route_probe(c, snapshot(length=length))
    for p0 in range(256):
        for p1 in range(256):
            route_probe(c, snapshot(p0=p0, p1=p1))
    for opcode in range(256):
        for parameter in range(256):
            route_probe(c, snapshot(opcode=opcode, parameter=parameter))
    other = 0
    for ident in (2, 0x7ff, 0xffff):
        for flags in range(256):
            for ready in (0, 1, MASK):
                route_probe(c, snapshot(ident=ident), flags, ready)
                other += 1
    for result in (1, MASK):
        for opcode in (0, 0x5a):
            route_probe(c, snapshot(opcode=opcode), filter_result=result)
    # The special-ID route does not use the other-ID configuration bit gate.
    route_probe(c, snapshot(), flags=8)
    integrations = 0
    for opcode in range(256):
        composed(image, body, snapshot(opcode=opcode))
        integrations += 1
    for length in (0, 4, 8, 255):
        for opcode in (0, 0x5a):
            composed(image, body, snapshot(length=length, opcode=opcode))
            integrations += 1
    for ident in (2, 0x7ff, 0xffff):
        for flags in (0, 8):
            for ready in (0, 1, MASK):
                composed(image, body, snapshot(ident=ident), flags, ready)
                integrations += 1
    for address, before, after, row, message in (
        (0x12ccc, '9307500b', '9307400b', snapshot(), 'classification route'),
        (0x12d6a, '230df100', 'a30df100', snapshot(opcode=0x5a), 'classification response record'),
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+len(bytes.fromhex(before))] == bytes.fromhex(before), 'classification mutation pin')
        mutant[off:off+len(bytes.fromhex(after))] = bytes.fromhex(after)
        try:
            route_probe(Classification(mutant, body, fixture([]), 0), row)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected classification mutation failure')
        else:
            raise RuntimeError('classification mutation undetected')
    print(f'PASS: 256 lengths; 65536 signatures; 65536 opcode/parameter pairs; {other} other-ID cases; {integrations} actual consumer/filter compositions; response copy/patch; 2 mutations; handlers NOT executed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--carrier', type=Path, default=CARRIER)
    args = parser.parse_args()
    verify(IMAGE.read_bytes(), args.carrier.read_bytes())
