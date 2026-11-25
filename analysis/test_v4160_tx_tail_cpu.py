"""Original TX tail with explicit synthetic, normally-returning callees.

Begin at 16bfa after the unknown copy call. Never execute peripheral/provider
code. Row/frame and callee responses are synthetic, preserving SP/S registers.
"""
from hashlib import sha256
from test_v4160_zero_id_queue_cpu import CPU, IMAGE, BASE, QUEUE, STACK, RETURN, MASK, check

IDENTITY = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
QUERY, SEND, UPDATE = 0x16994, 0x168de, 0x1693e
SP = STACK+0x800
SELECTORS = (0x30, 0x40, 0x50)
SAVED = (0x11223344, 0x55667788, 0x99aabbcc, 0xddeeff00)


class TailCPU(CPU):
    CODE_RANGES = ((0x16bfa, 0x16c6c),)


def run_case(image, busy, final, tag=1, length=8, changes=None):
    changes = changes or {}
    c = TailCPU(image, bytes(384))
    c.reg[2], c.reg[8] = SP, QUEUE
    for offset, value in zip((56, 52, 48, 44), SAVED):
        c.mem(SP+offset, 4, value)
    c.mem(SP+60, 4, RETURN)
    for index, selector in enumerate(SELECTORS):
        c.mem(SP+12+index, 1, selector)
    c.mem(QUEUE+11, 1, tag)
    c.mem(QUEUE+2, 1, length)
    c.writes.clear()
    free = next((i for i in range(3) if not (busy[i] & 8)), None)
    expected = []
    live_tag, live_length = tag, length

    def expect(target, args, reply):
        nonlocal live_tag, live_length
        expected.append((target, args, reply))
        if len(expected)-1 in changes:
            live_tag, live_length = changes[len(expected)-1]

    for i in range(3 if free is None else free+1):
        expect(QUERY, [live_tag, SELECTORS[i]], busy[i])
    if free is not None:
        selector = SELECTORS[free]
        expect(SEND, [live_tag, selector+1, SP+16, (live_length+5) & 255], 0xfeedface)
        expect(UPDATE, [live_tag, selector, 8, 8], 0xdeadbeef)
        expect(QUERY, [live_tag, selector], final)
    pc = 0x16bfa
    for index, (target, args, reply) in enumerate(expected):
        actual = c.run(pc, {QUERY, SEND, UPDATE, RETURN})
        check(actual == target and c.reg[10:10+len(args)] == args, 'TX call trace')
        resume = c.reg[1]
        for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
            c.put(reg, 0xcafe0000 + reg*0x101)
        c.put(10, reply)
        if index in changes:
            changed_tag, changed_length = changes[index]
            c.mem(QUEUE+11, 1, changed_tag)
            c.mem(QUEUE+2, 1, changed_length)
        pc = resume
    check(c.run(pc, {QUERY, SEND, UPDATE, RETURN}) == RETURN, 'TX final return')
    expected_result = 4 if free is None or final & 0x70 else 0
    check(c.reg[10] == expected_result, 'TX result mask')
    check(c.reg[2] == SP+64 and c.reg[1] == RETURN, 'TX restored SP/RA')
    check([c.reg[i] for i in (8, 9, 18, 19)] == list(SAVED), 'TX restored S registers')
    check(not c.calls, 'provider executed')
    if not changes:
        check(not c.writes, 'tail wrote memory')
    else:
        check(len(c.writes) == 2*len(changes), 'unexpected memory effects beyond synthetic changes')


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'image identity')
    cases = 0
    for mask in range(8):
        busy = [0xf0000100 | (8 if mask >> i & 1 else 0) for i in range(3)]
        for final in range(256):
            for tag in (1, 2):
                run_case(image, busy, 0xbeef0000 | final, tag)
                cases += 1
    boundaries = 0
    for free in range(3):
        busy = [8 if i < free else 0 for i in range(3)]
        for length in range(9):
            run_case(image, busy, 0, length=length)
            boundaries += 1
    # Explicit callee-side row changes demonstrate later live loads, not real races.
    for length in (0, 8, 9, 250, 251, 255):
        run_case(image, [0, 0, 0], 0, changes={0: (2, length), 1: (1, length), 2: (2, length)})
    for address, before, after, busy, final, message in (
        (0x16c10, '2189', '1189', [8, 0, 0], 0, 'TX call trace'),
        (0x16c48, '13750507', '13750508', [0, 0, 0], 0x10, 'TX result mask'),
    ):
        mutant = bytearray(image)
        off = address-BASE
        check(mutant[off:off+len(bytes.fromhex(before))] == bytes.fromhex(before), 'tail mutation pin')
        mutant[off:off+len(bytes.fromhex(after))] = bytes.fromhex(after)
        try:
            run_case(mutant, busy, final)
        except RuntimeError as exc:
            check(str(exc) == message, 'unexpected tail mutation failure')
        else:
            raise RuntimeError('tail mutation undetected')
    print(f'PASS: {cases} busy/final/tag combinations; {boundaries} length/selector boundaries; 6 live-row changes; 2 mask mutations; restored caller state')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
