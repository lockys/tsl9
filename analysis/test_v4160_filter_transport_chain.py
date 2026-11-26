"""Original filter -> transport composition with candidate copy and explicit
lookup/event normal-return hypotheses; no unknown service body executes.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from test_v4160_queue_filter_cpu import FilterCPU, TABLE, SNAPSHOT, ENTRY_SP, FILTER_S, FILTER_VALUES, table_bytes, prediction, nodes_for
from test_v4160_transport_frame_cpu import GP, BUFFER, STRIDE, LOOKUP, POST
from test_v4160_reference_copy_cpu import CARRIER, CARRIER_HASH, APP_HASH, BODY_HASH, RAM, CONTROL, CONTROL_INITIAL
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, RETURN, MASK, check

REQUEST, CONTINUE = 0x8a56, 0x836a


def reply(c, value):
    for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
        c.put(reg, 0xcafe0000+reg*0x101)
    c.put(10, value)


class Chain(FilterCPU):
    CODE_RANGES = FilterCPU.CODE_RANGES+((0x8a56, 0x8b6e),)

    def __init__(self, image, body, nodes, handles):
        super().__init__(image, body)
        self.regions.extend(((TABLE, table_bytes(nodes), True),
                             (GP+128, bytearray(32), True),
                             (BUFFER, bytearray([0xcc])*(STRIDE*2), True),
                             (0x4013c, bytearray(LOOKUP.to_bytes(4, 'little')), False),
                             (0x40050, bytearray(POST.to_bytes(4, 'little')), False)))
        self.reg[1], self.reg[2], self.reg[3], self.reg[10] = RETURN, ENTRY_SP, GP, SNAPSHOT
        for reg, value in zip(FILTER_S, FILTER_VALUES):
            self.reg[reg] = value
        for bank in range(2):
            self.mem(GP+150+4*bank, 2, handles[bank])
            self.mem(GP+148+4*bank, 1, 7+4*bank)
        self.requests, self.lookups, self.events, self.transport_returns = [], [], [], []
        self.copies = 0

    def buffer(self):
        return bytes(next(data for base, data, _ in self.regions if base == BUFFER))

    def transport(self, replies, event_reply):
        sp, resume = self.reg[2], self.reg[1]
        check(resume == CONTINUE and sp == ENTRY_SP-64, 'chain transport entry frame/link')
        saved = [self.reg[r] for r in (8, 9, 18, 19)]
        pc = REQUEST
        for _ in range(4):
            stop = self.run(pc, {LOOKUP, POST, resume})
            if stop == resume:
                check(self.reg[1] == resume and self.reg[2] == sp and
                      [self.reg[r] for r in (8, 9, 18, 19)] == saved, 'chain transport return state')
                self.transport_returns.append(self.reg[10])
                return
            check(self.reg[2] == (sp if stop == POST else sp-32), 'chain transport SP')
            if stop == LOOKUP:
                continuation = self.reg[1]
                check(continuation in (0x8a90, 0x8ab6), 'chain lookup continuation')
                self.lookups.append((continuation, self.reg[10], self.reg[11]))
                bank = 0 if continuation == 0x8a90 else 1
                reply(self, replies[bank])
                pc = continuation
            else:
                check(self.reg[1] == resume and [self.reg[r] for r in (8, 9, 18, 19)] == saved, 'chain event tail state')
                self.events.append((self.reg[10:13].copy(), self.buffer()))
                reply(self, event_reply)
                self.transport_returns.append(event_reply)
                return
        raise RuntimeError('chain transport budget')

    def execute(self, replies, event_reply):
        pc = 0x82d2
        for _ in range(8):
            stop = self.run(pc, {RAM, REQUEST, RETURN})
            if stop == RETURN:
                return
            if stop == RAM:
                self.run_reference(0x8358)
                self.copies += 1
                pc = 0x8358
            else:
                args = self.reg[10:14].copy()
                packet = self.mem(args[2], args[3]).to_bytes(args[3], 'little')
                self.requests.append((args, packet))
                self.transport(replies, event_reply)
                pc = CONTINUE
        raise RuntimeError('filter transport chain budget')


def expected_transport(requests, handles, replies, event_reply):
    buffer = bytearray([0xcc])*(STRIDE*2)
    lookups, events, returns = [], [], []
    for (handle, command, _, length), packet in requests:
        selected, result = None, handle
        for bank in range(2):
            if handles[bank] == handle and handle != 0xfffe:
                lookups.append((0x8a90 if bank == 0 else 0x8ab6, handle, GP+128))
                result = replies[bank]
                if result == 1:
                    selected = bank
                    break
        if selected is None:
            returns.append(result)
            continue
        offset = selected*STRIDE
        buffer[offset+2:offset+6] = (length+6).to_bytes(2, 'little')+bytes(2)
        buffer[offset+6:offset+11] = bytes([0x55, 0x7f, command, length >> 8, length & 255])
        buffer[offset+11:offset+11+length] = packet
        buffer[offset+11+length] = (command+(length >> 8)+(length & 255)+sum(packet)) & 255
        events.append(([7+4*selected, 1, GP+148+4*selected], bytes(buffer)))
        returns.append(event_reply)
    return lookups, events, returns, bytes(buffer)


def run_case(image, body, nodes, handles, replies, length, ident=0x123, tag=2, event_reply=MASK):
    c = Chain(image, body, nodes, handles)
    snapshot = ident.to_bytes(2, 'little')+bytes([length, *range(0xa0, 0xa8), tag])
    c.mem(SNAPSHOT, 12, int.from_bytes(snapshot, 'little'))
    expected_flag, requests = prediction(nodes, snapshot, ENTRY_SP)
    lookups, events, returns, buffer = expected_transport(requests, handles, replies, event_reply)
    c.execute(replies, event_reply)
    check(c.requests == requests and c.copies == len(requests), 'chain filter requests')
    check(c.lookups == lookups, 'chain admission calls')
    check(c.events == events and c.buffer() == buffer, 'chain event frames')
    check(c.transport_returns == returns, 'chain actual transport returns')
    check(c.reg[10] == expected_flag, 'chain filter flag result')
    check(c.reg[1] == RETURN and c.reg[2] == ENTRY_SP and
          [c.reg[r] for r in FILTER_S] == list(FILTER_VALUES), 'chain caller restoration')
    check(c.mem(SNAPSHOT, 12) == int.from_bytes(snapshot, 'little') and
          c.mem(CONTROL, 4) == CONTROL_INITIAL and not c.calls, 'chain source/control preservation')
    return c


def verify(image, carrier):
    check(len(image) == 76800 and sha256(image).hexdigest() == APP_HASH, 'APP identity')
    check(len(carrier) == 191078 and sha256(carrier).hexdigest() == CARRIER_HASH, 'candidate identity')
    check(carrier[0x4c:0x50] == RAM.to_bytes(4, 'little'), 'candidate slot')
    body = carrier[0x5a2:0x5dc]
    check(len(body) == 58 and sha256(body).hexdigest() == BODY_HASH, 'candidate body')
    maps = ((0x123, 0x124), (0xfffe, 0xfffe), (0x123, 0xfffe), (0xfffe, 0x124), (0x123, 0x123))
    cases = 0
    for m0, m1 in ((0, 0), (7, 0), (0, 7), (7, 7)):
        for length in range(9):
            for handles in maps:
                for first in (0, 1, 2, MASK):
                    for second in (0, 1, 2, MASK):
                        run_case(image, body, nodes_for(m0, m1), handles, (first, second), length)
                        cases += 1
    for m0 in range(8):
        for m1 in range(8):
            for length in (9, 255):
                c = run_case(image, body, nodes_for(m0, m1), maps[0], (1, 1), length)
                check(not c.events and not c.requests, 'oversized filter entered transport')
    probes = 0
    for ident in (0, 0x123, 0x7ff, 0x800, 0xffff):
        for tag in (0, 1, 2, 15, 255):
            for result in (0, 1, MASK):
                run_case(image, body, nodes_for(7, 7), maps[0], (1, 1), 8, ident, tag, result)
                probes += 1
    c = run_case(image, body, nodes_for(7, 7), maps[0], (0, 0), 8)
    check(c.reg[10] != 0 and len(c.requests) == 2 and not c.events, 'nonzero flag without admitted frame')
    # Duplicate table handles may issue two events against the same bank.
    c = run_case(image, body, ((0x123, 2, 1), (0x123, 2, 2)), maps[0], (1, 1), 8)
    check(len(c.events) == 2 and c.events[0][0] == c.events[1][0], 'same-bank repeated event boundary')
    for address, before, after, message in (
        (0x8b2e, '8545', '8945', 'chain event frames'),
        (0x8a90, '8547', '8947', 'chain event frames'),
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+2] == bytes.fromhex(before), 'chain mutation pin')
        mutant[off:off+2] = bytes.fromhex(after)
        try:
            run_case(mutant, body, nodes_for(7, 0), maps[0], (1, 0), 8)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected chain mutation failure')
        else:
            raise RuntimeError('chain mutation undetected')
    print(f'PASS: {cases} filter/transport cases; 128 oversized-filter cases; {probes} nested-header/event-return probes; nonzero flag with no admitted frame; repeated same-bank events; 2 mutations; unknown services NOT executed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--carrier', type=Path, default=CARRIER)
    args = parser.parse_args()
    verify(IMAGE.read_bytes(), args.carrier.read_bytes())
