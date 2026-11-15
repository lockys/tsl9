#!/usr/bin/env python3
"""Short-circuit read order checks for the 13c4e bounded decoder."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('gate', Path(__file__).with_name('state-13c4e-gate.py'))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class GateTest(unittest.TestCase):
    def test_first_slot_short_circuits_unmapped_second(self):
        mem = gate.fixture((0xffff, 1, 7), (0, 1, 1))
        for offset in (6, 7, 8, 9):
            del mem[gate.DATA + offset]
        self.assertEqual(gate.machine(gate.CODE, mem),
                         (0x13c9a, [(gate.DATA+2, 2), (gate.DATA+5, 1), (gate.DATA+4, 1)]))

    def test_sentinel_and_tag_skip_later_reads(self):
        self.assertEqual(gate.machine(gate.CODE, gate.fixture((0xfffe, 1, 1), (0xfffe, 1, 1))),
                         (0x13cda, [(gate.DATA+2, 2), (gate.DATA+6, 2)]))
        self.assertEqual(gate.machine(gate.CODE, gate.fixture((0, 2, 1), (0, 2, 1))),
                         (0x13cda, [(gate.DATA+2, 2), (gate.DATA+5, 1),
                                    (gate.DATA+6, 2), (gate.DATA+9, 1)]))

    def test_second_slot_nonzero_flag(self):
        first, second = (0xfffe, 1, 1), (0xffff, 1, 255)
        self.assertEqual(gate.machine(gate.CODE, gate.fixture(first, second)),
                         (0x13c9a, [(gate.DATA+2, 2), (gate.DATA+6, 2),
                                    (gate.DATA+9, 1), (gate.DATA+8, 1)]))

    def test_zero_first_flag_then_qualifying_second(self):
        first, second = (0, 1, 0), (0xffff, 1, 255)
        self.assertEqual(gate.machine(gate.CODE, gate.fixture(first, second)),
                         (0x13c9a, [(gate.DATA+2, 2), (gate.DATA+5, 1), (gate.DATA+4, 1),
                                    (gate.DATA+6, 2), (gate.DATA+9, 1), (gate.DATA+8, 1)]))

    def test_inverted_first_sentinel_branch_changes_behavior_even_with_new_pin(self):
        original = gate.CODE
        try:
            changed = bytearray(original)
            changed[0x13c62-gate.START+1] ^= 0x10  # beq -> bne
            gate.CODE = bytes(changed)
            first, second = (0xfffe, 1, 1), (0xfffe, 1, 1)
            self.assertNotEqual(gate.machine(changed, gate.fixture(first, second)),
                                gate.oracle(first, second))
        finally:
            gate.CODE = original

    def test_required_read_must_exist(self):
        mem = gate.fixture((0, 1, 1), (0, 1, 1))
        del mem[gate.DATA+5]
        with self.assertRaisesRegex(ValueError, 'unmapped synthetic read'):
            gate.machine(gate.CODE, mem)

    def test_instruction_identity_rejected(self):
        bad = bytearray(gate.CODE)
        bad[0] ^= 1
        with self.assertRaisesRegex(ValueError, 'identity'):
            gate.machine(bad, {})


if __name__ == '__main__':
    unittest.main()
