#!/usr/bin/env python3
"""Instruction-order projection of 0x155fc, not a CPU or device model.

Only successful byte-addressable RAM accesses are modeled.  In particular,
word alignment traps, concurrency and the target's effects are out of scope.
"""
import hashlib
import unittest
import test_155d0_entry_order as entry

CODE = bytes.fromhex('2244b240924402492383011641016f207030')
MASK = 0xffffffff


def project(memory, sp, gp, a0):
    events = []
    restored = []
    for offset in (8, 12, 4, 0):
        address = (sp + offset) & MASK
        value = entry.load(memory, address)
        events.append(('read32', address, value))
        restored.append(value)
    address = (gp + 358) & MASK
    memory[address] = 0
    events.append(('write8', address, 0))
    return (sp + 16) & MASK, tuple(restored), a0 & MASK, 0x18110, events


class TailOrder(unittest.TestCase):
    def test_binary_identity(self):
        image = entry.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), entry.SHA)
        self.assertEqual(image[0x155fc - 0x8000:0x1560e - 0x8000], CODE)

    def test_restore_before_clear_even_when_aliased(self):
        sp = 0xfffffff8
        for offset in (0, 4, 8, 12):
            for byte_offset in range(4):
                memory = {(sp + i) & MASK: (i + 1) for i in range(16)}
                before = memory.copy()
                address = (sp + offset + byte_offset) & MASK
                result = project(memory, sp, (address - 358) & MASK, 0xabcdef01)
                values = tuple(entry.load(before, (sp + n) & MASK) for n in (8, 12, 4, 0))
                self.assertEqual(result[:4], (8, values, 0xabcdef01, 0x18110))
                self.assertEqual(result[4], [('read32', (sp + n) & MASK, v) for n, v in zip((8, 12, 4, 0), values)] + [('write8', address, 0)])
                before[address] = 0
                self.assertEqual(memory, before)

    def test_missing_read_does_not_clear(self):
        memory = {0x2000: 7}
        with self.assertRaises(KeyError):
            project(memory, 0x1000, 0x2000 - 358, 0)
        self.assertEqual(memory[0x2000], 7)


if __name__ == '__main__':
    unittest.main()
