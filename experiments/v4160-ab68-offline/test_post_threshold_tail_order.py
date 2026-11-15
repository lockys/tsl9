#!/usr/bin/env python3
"""Offline, instruction-pinned projection of the two post-threshold tails.

Successful little-endian word reads and byte stores are assumed; address wrap
is modeled but alignment faults, asynchronous effects and the callee are not.
"""
import hashlib
import unittest

import caller_threshold_projection as prefix

MASK = 0xffffffff
TAIL = bytes.fromhex('2244b24092442389f10441016f309006')
RETURN = bytes.fromhex('b2402244924441018280')


def model(sp, gp, bit, memory, changed):
    """Return final SP, restored registers, transfer and ordered memory events."""
    sp &= MASK
    gp &= MASK
    events = []

    def load(offset):
        addr = (sp + offset) & MASK
        value = sum(memory[(addr + i) & MASK] << (8 * i) for i in range(4))
        events.append(('read32', addr, value))
        return value

    if changed:
        s0, ra, s1 = load(8), load(12), load(4)
        address = (gp + 82) & MASK
        memory[address] = bit & 255
        events.append(('write8', address, bit & 255))
        target = 0x13c4e
    else:
        ra, s0, s1 = load(12), load(8), load(4)
        target = ra & ~1
    return (sp + 16) & MASK, (s0, ra, s1), target, events


class TailOrderTests(unittest.TestCase):
    def test_original_instruction_bytes(self):
        data = prefix.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), prefix.SHA)
        self.assertEqual(data[0x103da-0x8000:0x103ea-0x8000], TAIL)
        self.assertEqual(data[0x103f8-0x8000:0x10402-0x8000], RETURN)

    def test_store_occurs_after_all_restores_even_if_saved_ra_aliases(self):
        for offset in (4, 8, 12):
            for byte in range(4):
                sp = 0x100
                address = sp + offset + byte
                memory = {sp + i: (i * 19 + 1) & 255 for i in range(16)}
                before = memory.copy()
                result = model(sp, address - 82, 1, memory, True)
                self.assertEqual(result[0], 0x110)
                self.assertEqual(result[2], 0x13c4e)
                self.assertEqual([e[0] for e in result[3]], ['read32'] * 3 + ['write8'])
                self.assertEqual(result[1][1], int.from_bytes(bytes(before[sp + 12 + i] for i in range(4)), 'little'))
                self.assertEqual(memory[address], 1)

    def test_no_change_return_and_wrap(self):
        sp = 0xfffffff8
        memory = {(sp + i) & MASK: i for i in range(16)}
        before = memory.copy()
        result = model(sp, 0, 0, memory, False)
        self.assertEqual(result[0], 8)
        self.assertEqual([e[1] for e in result[3]], [4, 0, 0xfffffffc])
        self.assertEqual(result[2], result[1][1] & ~1)
        self.assertEqual(memory, before)


if __name__ == '__main__':
    unittest.main()
