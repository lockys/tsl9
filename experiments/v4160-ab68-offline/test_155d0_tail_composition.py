#!/usr/bin/env python3
"""Compose 155d0 entry, guards and 155fc tail in shared synthetic RAM.

Only the nonzero guard path reaches the tail under test. Other branches stop
at their boundary. Successful ordinary memory and stable code are assumed;
this is neither a full CPU nor proof of reachability on a device.
"""
import hashlib
import unittest
import test_155d0_entry_order as entry
import test_155d0_machine as machine
import test_155e8_guard as early
import test_155f6_guard as guard
import test_155fc_machine as tail
import test_155fc_tail_order as model

MASK = 0xffffffff


class Composition(unittest.TestCase):
    def test_shared_memory_paths(self):
        image = entry.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), entry.SHA)
        for start, code in ((0x155d0, entry.CODE), (0x155e8, early.CODE),
                            (0x155f6, guard.CODE), (0x155fc, model.CODE)):
            self.assertEqual(image[start - 0x8000:start - 0x8000 + len(code)], code)
        counts = {0x155fc: 0, 0x1560e: 0, 0x1578c: 0}
        for flags in range(256):
            for a0 in (0, 250, 251, 252):
                for saved in (0, 1):
                    gp = 0x1000
                    address = gp + 358
                    # Entry saves s2 at sp-16, intentionally aliasing the guard.
                    sp = address + 16
                    memory = {0x3004: flags}
                    entry.store(memory, gp + 84, 0x3000)
                    regs, pc = machine.run(entry.CODE, memory, gp, sp, 0x1234,
                                           0x12345679, 0xabcdef01, saved)
                    if pc == 0x155e8:
                        pc = early.run(early.CODE, a0)[2]
                    if pc == 0x155f6:
                        value, pc, observed = guard.guard(guard.CODE, gp, memory)
                        self.assertEqual((value, observed), (saved, address))
                    counts[pc] += 1
                    if pc != 0x155fc:
                        continue
                    before = memory.copy()
                    candidate, expected_memory = memory.copy(), memory.copy()
                    actual = tail.run(model.CODE, regs[2], gp, a0, candidate)
                    expected = model.project(expected_memory, regs[2], gp, a0)
                    self.assertEqual(actual, expected)
                    self.assertEqual(candidate, expected_memory)
                    self.assertEqual(actual[:4], (sp, (0xabcdef01, 0x12345679, 0x1234, saved),
                                                   a0, 0x18110))
                    self.assertEqual(before[address], 1)
                    self.assertEqual(candidate[address], 0)
        self.assertEqual(counts, {0x155fc: 896, 0x1560e: 896, 0x1578c: 256})


if __name__ == '__main__':
    unittest.main()
