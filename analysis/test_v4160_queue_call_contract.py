"""Bounded original-instruction queue checks; never execute the resident provider.

Run from any directory with Python 3.10+. The sibling CPU is deliberately small
and fails closed on unsupported instructions/accesses. Synthetic provider return
tests below are conditional on the stated ABI/memory assumptions, not hardware.
"""
from hashlib import sha256
from test_v4160_zero_id_queue_cpu import (
    CPU, IMAGE, BASE, QUEUE, SOURCE, PROVIDER, RETURN, MASK, check, fixture,
)

IDENTITY = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
IDS = (0, 0x10000, 0xffff0000, 1, 0xffff, 0x10001, MASK)
LENGTHS = (0, 1, 8, 0xff, 0x100, 0x101, MASK)


def enter(image, free, ident, length):
    before = fixture(free)
    c = CPU(image, before)
    c.reg[8:10] = [0x12345678, 0x9abcdef0]  # caller's saved S0/S1
    c.reg[10:14] = [ident, SOURCE, length, 0x12345642]
    check(c.run(0x12bc8, {PROVIDER, RETURN}) == PROVIDER, 'provider entry')
    off = free * 12
    expected = bytearray(before)
    expected[off:off+2] = (ident & 0xffff).to_bytes(2, 'little')
    expected[off+2] = length & 255
    check(c.queue() == expected, 'pre-call queue writes')
    check(c.reg[10:13] == [QUEUE + off + 3, SOURCE, length], 'full call arguments')
    check(c.reg[1] == 0x12c0e and c.reg[9] == 0x12345642, 'return PC and saved tag')
    check(not c.calls, 'provider must not execute')
    return c, expected


def verify(image):
    check(len(image) == 76800 and sha256(image).hexdigest() == IDENTITY, 'image identity')
    count = 0
    for free in range(32):
        for ident in IDS:
            for length in LENGTHS:
                enter(image, free, ident, length)
                count += 1
    # Provider is not executed: simulate a return with NO memory writes and
    # arbitrary caller-saved register values, preserving SP, S0, S1 and stack.
    # This checks only the post-call instruction contract, not a copy routine.
    returned = 0
    for free in range(32):
        for ident in IDS:
            c, expected = enter(image, free, ident, 1)
            resume = c.reg[1]
            sp = c.reg[2]
            for reg in (1, 5, 6, 7, *range(10, 18), *range(28, 32)):
                c.reg[reg] = (0xa5a50000 + reg * 0x101) & MASK
            c.run(resume, {RETURN})
            expected[12*free+11] = 0x42
            check(c.queue() == expected, 'post-return tag write')
            check(c.reg[2] == sp + 16 and c.reg[8:10] == [0x12345678, 0x9abcdef0], 'frame restoration')
            returned += 1
    full = 0
    for ident in IDS:
        for length in LENGTHS:
            before = fixture(32)
            c = CPU(image, before)
            c.reg[10:14] = [ident, SOURCE, length, 0x42]
            check(c.run(0x12bc8, {PROVIDER, RETURN}) == RETURN, 'full queue must return')
            check(c.queue() == before and not c.calls, 'full queue effects')
            full += 1
    # Negative control changes SB A2 to SB A1 only in a memory copy. A boundary
    # case must fail the metadata check rather than silently accepting the edit.
    mutant = bytearray(image)
    off = 0x12bfa - BASE
    check(mutant[off:off+4] == bytes.fromhex('2301c400'), 'mutation pin')
    mutant[off:off+4] = bytes.fromhex('2301b400')
    try:
        enter(mutant, 0, 1, 0x101)
    except RuntimeError as exc:
        check(str(exc) == 'pre-call queue writes', 'unexpected mutation failure')
    else:
        raise RuntimeError('metadata mutation went undetected')
    print(f'PASS: {count} pre-provider ID/length/slot cases; {returned} conditional clobbered-return cases; {full} full-queue cases; SB mutation detected')


if __name__ == '__main__':
    verify(IMAGE.read_bytes())
