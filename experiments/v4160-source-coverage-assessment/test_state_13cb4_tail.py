#!/usr/bin/env python3
"""Check 13cb4 tail edge cases; these are synthetic ordinary-memory cases."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('state_tail', HERE/'state-13cb4-tail.py')
tail = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tail)


class TailTest(unittest.TestCase):
    def test_jump_and_argument_decoding(self):
        self.assertEqual(tail.decode(tail.CODE), (0x137c0, 0x9124, 0x137c0, 340))

    def test_restore_precedes_aliasing_store(self):
        # Synthetic word-addressed memory, stack save slot equals gp+340.
        for sp in (0x2000ff00, 0xfffffff8, 0):
            saved_addr = (sp+12) & tail.MASK
            gp = (saved_addr-340) & tail.MASK
            memory = {saved_addr: 0x12345678}
            restored = memory[saved_addr]  # lw ra precedes sw a0
            ra, new_sp, write, target, args = tail.project(tail.CODE, True, gp, sp, 0x89abcdef, restored)
            address, value = write
            memory[address] = value
            self.assertEqual((ra, memory[saved_addr], target, args),
                             (0x12345678, 0x89abcdef, 0x137c0, (0,)))
            self.assertEqual(new_sp, (sp+16) & tail.MASK)

    def test_scheduled_path_does_not_write(self):
        ra, new_sp, write, target, args = tail.project(tail.CODE, False, 0, 0xfffffff8, 123, 456)
        self.assertEqual((ra, new_sp, write, target, args), (456, 8, None, 0x9124, (0x137c0, 0, 35, 0)))

    def test_semantic_fields_reject_changes_even_if_pin_is_changed(self):
        original = tail.CODE
        try:
            for index in range(len(original)):
                with self.subTest(index=index), self.assertRaises(ValueError):
                    changed = bytearray(original)
                    changed[index] ^= 1
                    tail.CODE = bytes(changed)
                    tail.decode(changed)
        finally:
            tail.CODE = original

    def test_identity_rejects_changes(self):
        for index in range(len(tail.CODE)):
            with self.subTest(index=index), self.assertRaises(ValueError):
                changed = bytearray(tail.CODE)
                changed[index] ^= 1
                tail.decode(changed)


if __name__ == '__main__':
    unittest.main()
