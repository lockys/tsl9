"""TX tail plus original query/send/update/transfer bodies; synthetic MMIO only.

Start after the opaque copy provider with a synthetic valid frame and row.
Never execute provider code, access hardware, or infer physical transmission.
"""
from hashlib import sha256
from test_v4160_tx_tail_cpu import TailCPU, QUERY, SEND, UPDATE, SP, SELECTORS, SAVED
from test_v4160_transfer_receive_chain import Integrated
from test_v4160_zero_id_queue_cpu import IMAGE, BASE, QUEUE, RETURN, check

TRANSFER, MMIO = 0x16896, 0x40010810
IDENTITY = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


class DirectChain(TailCPU):
    CODE_RANGES = ((0x168de, 0x169dc), (0x16bfa, 0x16c6c))
    transfer = Integrated.transfer

    def __init__(self, image, scenarios):
        super().__init__(image, bytes(384))
        self.regions.append((MMIO, bytearray(8), True))
        self.scenarios = iter(scenarios)
        self.trace, self.transfers, self.entries = [], [], []

    def execute(self):
        pc = 0x16bfa
        for _ in range(200):
            if pc == RETURN:
                return
            if pc in (QUERY, SEND, UPDATE):
                n = 2 if pc == QUERY else 4
                self.entries.append((pc, self.reg[10:10+n].copy()))
            if pc == TRANSFER:
                self.transfer()
                pc = self.pc
            else:
                pc = self.run(pc, {QUERY, SEND, UPDATE, TRANSFER, RETURN}-{pc})
        raise RuntimeError('direct-chain budget exceeded')


def plan(busy, final, tag, length, frame):
    entries, outgoing, scenarios = [], [], []
    free = next((i for i in range(3) if not busy[i] & 8), None)

    def query(selector, status):
        entries.append((QUERY, [tag, selector]))
        outgoing.extend(((0x169be, 3), (0x169c6, selector), (0x169cc, 0)))
        scenarios.extend(((1, 1, 0xaa), (1, 1, 0xbb), (1, 1, status)))

    for i in range(3 if free is None else free+1):
        query(SELECTORS[i], busy[i])
    if free is not None:
        selector, n = SELECTORS[free], length+5
        entries.append((SEND, [tag, selector+1, SP+16, n]))
        outgoing.extend(((0x16910, 2), (0x1691a, selector+1)))
        outgoing.extend((0x1693c, byte) for byte in frame[:n])
        scenarios.extend([(1, 1, 0xa5)]*(n+2))
        entries.append((UPDATE, [tag, selector, 8, 8]))
        outgoing.extend(((0x1696c, 5), (0x16974, selector), (0x1697c, 8), (0x16984, 8)))
        scenarios.extend([(1, 1, 0x5a)]*4)
        query(selector, final)
    return entries, outgoing, scenarios


def run_scene(image, busy=(0, 0, 0), final=0, tag=1, length=8, replace=None, all_pattern=None):
    frame = bytes([0x28, 0xa0, 0, 0, length, *range(0xa0, 0xa8)])
    entries, outgoing, scenarios = plan(busy, final, tag, length, frame)
    if replace is not None:
        index, pattern = replace
        scenarios[index] = pattern
    if all_pattern is not None:
        scenarios = [all_pattern]*len(scenarios)
    # Special scenarios here preserve the planned selector decision: busy=0 and
    # final=0. Other injected returns may be arbitrary in ignored positions.
    c = DirectChain(image, scenarios)
    c.reg[2], c.reg[8] = SP, QUEUE
    for offset, value in zip((56, 52, 48, 44), SAVED):
        c.mem(SP+offset, 4, value)
    c.mem(SP+60, 4, RETURN)
    for i, selector in enumerate(SELECTORS):
        c.mem(SP+12+i, 1, selector)
    c.mem(SP+16, 13, int.from_bytes(frame, 'little'))
    c.mem(QUEUE+11, 1, tag)
    c.mem(QUEUE+2, 1, length)
    c.writes.clear()
    before_queue = c.queue()
    c.execute()
    check(c.entries == entries, 'direct callee sequence')
    check(c.transfers == outgoing, 'actual transfer argument sequence')
    first_free = next((i for i in range(3) if not busy[i] & 8), None)
    check(len(c.transfers) == (9 if first_free is None else 17+length+3*first_free), 'transfer count formula')
    expected_trace = []
    for (_, arg), (first, second, received) in zip(outgoing, scenarios):
        value = received & 255 if first and second else 0
        expected_trace.append((value, first or 255, (second or 255) if first else 0,
                               (arg & 0xffff,) if first else (), int(bool(first and second))))
    check(c.trace == expected_trace, 'direct-chain transfer trace')
    expected_result = 4 if all(value & 8 for value in busy) or final & 0x70 else 0
    check(c.reg[10] == expected_result, 'direct-chain return')
    check(c.reg[2] == SP+64 and c.reg[1] == RETURN, 'direct-chain SP/RA')
    check([c.reg[i] for i in (8, 9, 18, 19)] == list(SAVED), 'direct-chain S registers')
    check(c.queue() == before_queue and c.mem(SP+16, 13) == int.from_bytes(frame, 'little'), 'row/frame preservation')
    mmio = [(a, n, v) for a, n, v in c.writes if MMIO <= a < MMIO+8]
    expected_mmio = [(address, 4, value) for _ in entries for address, value in
                     ((MMIO+4, 16 if tag == 1 else 1), (MMIO, 17))]
    check(mmio == expected_mmio, 'direct-chain MMIO sequence')
    check(not c.calls, 'opaque provider executed')
    check(next(c.scenarios, None) is None, 'unused transfer scenarios')
    return c, len(outgoing)


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'image identity')
    cases = 0
    for mask in range(8):
        busy = tuple(8 if mask >> i & 1 else 0 for i in range(3))
        for final in range(256):
            for tag in (1, 2):
                run_scene(image, busy, final, tag)
                cases += 1
    lengths = 0
    for free in range(3):
        for length in range(9):
            run_scene(image, tuple(8 if i < free else 0 for i in range(3)), length=length)
            lengths += 1
    _, total = run_scene(image)
    check(total == 25, 'length-eight transfer count')
    substitutions = 0
    for index in range(total):
        for pattern in ((1, 1, 0), (0, 0, 0xa5), (1, 0, 0xa5)):
            run_scene(image, replace=(index, pattern))
            substitutions += 1
    for pattern, writes, reads in (((0, 0, 0xa5), 0, 0), ((1, 0, 0xa5), 25, 0), ((1, 1, 0), 25, 25)):
        c, _ = run_scene(image, all_pattern=pattern)
        check(c.reg[10] == 0 and sum(len(t[3]) for t in c.trace) == writes and
              sum(t[4] for t in c.trace) == reads, 'zero return without success evidence')
    for first, second in ((255, 1), (1, 255), (255, 255)):
        run_scene(image, all_pattern=(first, second, 0))
    # Mutate the query dummy read outgoing byte; no hardware is accessed.
    mutant = bytearray(image)
    off = 0x169c6-BASE
    check(mutant[off:off+2] == bytes.fromhex('0145'), 'query dummy mutation pin')
    mutant[off:off+2] = bytes.fromhex('0545')  # LI A0,0 -> 1
    try:
        run_scene(mutant)
    except RuntimeError as exc:
        check(str(exc) == 'actual transfer argument sequence', 'unexpected query mutation failure')
    else:
        raise RuntimeError('query mutation undetected')
    print(f'PASS: {cases} original-callee status/tag combinations; {lengths} length/selector cases; {substitutions} zero/timeout substitutions; 3 all-zero paths; 3 late-ready paths; query mutation detected')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
