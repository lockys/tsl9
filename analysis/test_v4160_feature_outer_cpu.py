"""Original 829e getter and 14d2e outer feature dispatch, offline only.
Stop before mode1 and tail providers; candidate-only consumer composition optional.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from test_v4160_zero_id_queue_cpu import CPU, IMAGE, BASE, STACK, RETURN, MASK, check

ENTRY, GETTER, MODE, TABLE, ROW = 0x14d2e, 0x829e, 0x2000bfb5, 0x1a6b8, 0x28000000
MODE1, DEFAULT, MODE0 = 0x14d5e, 0x1074c, 0x10b60
SP, SAVED_S0 = STACK+0x800, 0x11223344
APP_HASH = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ENTRIES = (0x14d52, MODE1, 0x153ba, 0x153da, 0x153fa, 0x1543a, 0x1547a)
MAP = {
    2: {169: 0x10870, 540: 0x108d8},
    3: {169: 0x10870, 540: 0x10944},
    4: {169: 0x10870, 393: 0x109c4, 1676: 0x10a00},
    5: {890: 0x10ac6, 929: 0x10a16, 1002: 0x10b0a},
    6: {169: 0x10870, 1176: 0x10936},
}
RANGES = ((GETTER, 0x82a8), (ENTRY, MODE1), (0x14da2, 0x14daa), (0x153ba, 0x154a6))
TAILS = {DEFAULT, MODE0} | {target for values in MAP.values() for target in values.values()}


class Trace:
    def mem(self, address, size, value=None):
        result = super().mem(address, size, value)
        if getattr(self, 'trace_active', False) and (
            not BASE <= address < BASE+76800 or TABLE <= address < TABLE+28
        ):
            self.events.append(('r' if value is None else 'w', address, size,
                                result if value is None else value & ((1 << (size*8))-1)))
        return result


class Outer(Trace, CPU):
    CODE_RANGES = RANGES

    def __init__(self, image):
        super().__init__(image, bytes(384))
        self.regions.extend(((MODE, bytearray([0, 0xff]), True),
                             (ROW, bytearray(range(12)), True)))
        self.regions[2][1][:] = bytes([0xcc])*0x1000


def registers(c, pointer=ROW):
    c.reg = [0x11110000+i*0x101 for i in range(32)]
    c.reg[0], c.reg[1], c.reg[2], c.reg[8], c.reg[10] = 0, RETURN, SP, SAVED_S0, pointer


def execute(c, mode, ident):
    before = c.reg[:]
    pointer, resume, caller_sp, caller_s0 = before[10], before[1], before[2], before[8]
    bank_frame = caller_sp-16
    expected = [('w', caller_sp-8, 4, caller_s0), ('w', caller_sp-4, 4, resume),
                ('r', MODE, 1, mode)]
    if mode <= 6:
        expected.append(('r', TABLE+mode*4, 4, (ENTRIES[mode]-TABLE) & MASK))
    if mode in MAP:
        expected.append(('r', pointer, 2, ident))
    endpoint = MODE1 if mode == 1 else MODE0 if mode == 0 else DEFAULT if mode > 6 else MAP[mode].get(ident, resume)
    if mode != 1:
        restores = [(caller_sp-4, resume), (caller_sp-8, caller_s0)] if endpoint == resume else [(caller_sp-8, caller_s0), (caller_sp-4, resume)]
        expected.extend(('r', address, 4, value) for address, value in restores)
    c.events, c.trace_active = [], True
    c.writes.clear()
    stop = c.run(ENTRY, TAILS | {MODE1, resume})
    c.trace_active = False
    check(stop == endpoint, 'outer endpoint')
    check(c.events == expected, 'outer ordered data accesses')
    check(c.writes == [(caller_sp-8, 4, caller_s0), (caller_sp-4, 4, resume)], 'outer write footprint')
    changed = (1, 2, 8, 10, 14, 15)
    check(all(c.reg[i] == before[i] for i in range(32) if i not in changed), 'outer other registers preserved')
    if mode == 1:
        check((c.reg[1], c.reg[2], c.reg[8], c.reg[10], c.reg[14], c.reg[15]) ==
              (0x14d3a, bank_frame, pointer, TABLE+4, TABLE, MODE1), 'mode1 entry frame')
    else:
        check((c.reg[1], c.reg[2], c.reg[8]) == (resume, caller_sp, caller_s0), 'outer restored caller')
        a0 = 0 if mode > 6 else TABLE+mode*4 if endpoint == resume else pointer
        check(c.reg[10] == a0, 'outer A0 boundary value')
    check(not c.calls, 'provider executed')
    return endpoint


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(tuple((TABLE+int.from_bytes(image[TABLE-BASE+i*4:TABLE-BASE+i*4+4], 'little')) & MASK
                for i in range(7)) == ENTRIES, 'original relative table')
    c = Outer(image)
    for mode in range(256):
        registers(c)
        c.mem(MODE, 1, mode)
        before = c.reg[:]
        c.events, c.trace_active = [], True
        c.writes.clear()
        check(c.run(GETTER, {RETURN}) == RETURN, 'mode getter return')
        c.trace_active = False
        check(c.events == [('r', MODE, 1, mode)] and not c.writes, 'mode getter byte read')
        check(c.reg[10] == mode and all(c.reg[i] == before[i] for i in range(32) if i != 10), 'mode getter registers')
        for ident in (0, 169, 0xffff):
            registers(c)
            c.mem(ROW, 2, ident)
            execute(c, mode, ident)
    exhaustive = 0
    for mode in MAP:
        c.mem(MODE, 1, mode)
        for ident in range(65536):
            registers(c)
            c.mem(ROW, 2, ident)
            execute(c, mode, ident)
            exhaustive += 1
    # Modes 0, 1 and >6 do not read any record bytes before their stop boundary.
    for mode in (0, 1, 7, 255):
        registers(c, 0)
        c.mem(MODE, 1, mode)
        execute(c, mode, 0)
    for address, before, after in (
        (TABLE+8, '02adffff', '22adffff'),  # mode2 -> mode3 entry
        (0x82a2, '034575d1', '034585d1'),  # getter reads adjacent byte
    ):
        mutant = bytearray(image)
        offset = address-BASE
        check(mutant[offset:offset+len(bytes.fromhex(before))] == bytes.fromhex(before), 'outer mutation pin')
        mutant[offset:offset+len(bytes.fromhex(after))] = bytes.fromhex(after)
        probe = Outer(mutant)
        registers(probe)
        probe.mem(MODE, 1, 2)
        probe.mem(ROW, 2, 540)
        try:
            execute(probe, 2, 540)
        except RuntimeError as exc:
            check(str(exc) == 'outer endpoint', 'unexpected outer mutation failure: '+str(exc))
        else:
            raise RuntimeError('outer mutation undetected')
    print(f'PASS: 256 byte getters; 768 mode/ID probes; {exhaustive} mode2-6/full-ID cases; '
          '4 null-record boundaries; 2 mutations; mode1/tail providers NOT executed')


def composition(image, carrier):
    from test_v4160_consumer_classify_cpu import (Classification, classify, snapshot,
        CARRIER_HASH, BODY_HASH, CONTROL, CONTROL_INITIAL, OTHER, NEXT, S_REGS, S_VALUES)
    from test_v4160_queue_filter_cpu import TABLE as FILTER_TABLE, table_bytes, execute_filter
    from test_v4160_consumer_detach_cpu import fixture, CALLBACK, FRAME_SP, INITIAL_SP
    from test_v4160_tx_entry_cpu import CONFIG
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'copy candidate identity')
    body = carrier[0x5a2:0x5dc]
    check(sha256(body).hexdigest() == BODY_HASH and carrier[0x4c:0x50] == (0x20000332).to_bytes(4, 'little'),
          'copy candidate body/slot')
    class Chained(Trace, Classification):
        CODE_RANGES = Classification.CODE_RANGES+RANGES
    cases = returns = tails = mode1 = 0
    ids = (0x123, 169, 540, 393, 1676, 890, 929, 1002, 1176)
    for mode in range(256):
        for ident in ids:
            row = snapshot(ident=ident)
            data = fixture([])
            data[17*12:17*12+12] = row
            c = Chained(image, body, data, 0)
            c.regions.extend(((MODE, bytearray([mode, 0xff]), True),
                              (FILTER_TABLE, table_bytes(((0xfffe, 1, 0), (0xfffe, 1, 0))), True)))
            c.mem(CONFIG+4, 1, 0)
            check(c.advance() == CALLBACK, 'outer composed consumer detach')
            execute_filter(c)
            check(c.reg[10] == 0 and classify(c, row, 1) == OTHER and c.probe_calls == 1,
                  'outer composed classification')
            check(c.reg[10] == FRAME_SP+8 and c.reg[1] == 0x12d90 and c.reg[2] == FRAME_SP,
                  'outer composed handoff')
            stop = execute(c, mode, ident)
            cases += 1
            if stop == 0x12d90:
                c.scan_start = stop
                check(c.advance() == RETURN and c.reg[2] == INITIAL_SP and
                      [c.reg[r] for r in S_REGS] == list(S_VALUES), 'outer unmatched consumer completion')
                returns += 1
            elif stop == MODE1:
                mode1 += 1
            else:
                tails += 1
            data[17*12:17*12+2] = bytes(2)
            check(c.queue() == data and c.mem(FRAME_SP+8, 12) == int.from_bytes(row, 'little') and
                  c.csr == 0x88 and c.mem(CONTROL, 4) == CONTROL_INITIAL, 'outer composed memory/control preserved')
    print(f'PASS: {cases} detached-consumer/filter/classification/outer chains; {returns} unmatched scan completions; '
          f'{tails} tail boundaries; {mode1} mode1 boundaries; candidate-only copy binding')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--standalone-only', action='store_true')
    parser.add_argument('--carrier', type=Path, default=Path(__file__).resolve().parent/'wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin')
    args = parser.parse_args()
    image = IMAGE.read_bytes()
    verify(image)
    if not args.standalone_only:
        composition(image, args.carrier.read_bytes())
