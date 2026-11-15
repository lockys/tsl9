#!/usr/bin/env python3
"""Finite-decoder checks, including changed instruction semantics."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('machine', Path(__file__).with_name('wrapper_81b0_machine.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
w = m.w


class MachineTest(unittest.TestCase):
    def run_both(self, sp, ra, raw, change_sp):
        memories = [{}, {}]
        for mem in memories:
            w.store32(mem, w.SLOT, 0x12345679)
        def provider(target, frame, mem):
            self.assertEqual(target, 0x12345678)
            if change_sp:
                w.store32(mem, 0x300c, 0x9877)
                return raw, 0x3000
            return raw, frame
        result = w.project(w.CODE, memories[0], sp, ra, provider)
        self.assertEqual(m.machine(w.CODE, memories[1], sp, ra, provider), result)
        self.assertEqual(memories[0], memories[1])
        return result

    def test_alias_and_live_stack(self):
        self.assertEqual(self.run_both(0x40080, 0xaabbccdd, 16, False),
                         (10, 0x40080, 0xaabbccdd, 0xaabbccdc))
        self.assertEqual(self.run_both(0x2000, 3, 0xffffffff, True),
                         (0x0fffffff, 0x3010, 0x9877, 0x9876))

    def test_shift_mutant_changes_result(self):
        code = bytearray(w.CODE)
        code[22] ^= 4  # c.srli a0,4 becomes c.srli a0,5
        memory = {}
        w.store32(memory, w.SLOT, 0)
        self.assertEqual(m.machine(code, memory, 0x2000, 0, lambda t, s, b: (16, s))[0], 5)

    def test_wrong_multiply_destination_changes_result(self):
        code = bytearray(w.CODE)
        code[14] ^= 0x80  # mul writes a1 rather than a0
        memory = {}
        w.store32(memory, w.SLOT, 0)
        self.assertEqual(m.machine(code, memory, 0x2000, 0, lambda t, s, b: (16, s))[0], 1)

    def test_invalid_instruction_is_rejected(self):
        code = bytearray(w.CODE)
        code[14:18] = b'\xff\xff\xff\xff'
        memory = {}
        w.store32(memory, w.SLOT, 0)
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            m.machine(code, memory, 0x2000, 0, lambda t, s, b: (1, s))


if __name__ == '__main__':
    unittest.main()
