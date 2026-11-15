#!/usr/bin/env python3
"""Synthetic ordering and corruption cases; BIN identity is checked by CLI."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('wrapper', Path(__file__).with_name('wrapper-81b0.py'))
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WrapperTest(unittest.TestCase):
    def test_fetch_before_saved_ra_overwrites_slot(self):
        memory = {}
        w.store32(memory, w.SLOT, 0x11223345)
        def provider(target, frame, bus):
            self.assertEqual((target, frame, w.load32(bus, w.SLOT)),
                             (0x11223344, 0x40070, 0xaabbccdd))
            return 16, frame
        self.assertEqual(w.project(w.CODE, memory, 0x40080, 0xaabbccdd, provider),
                         (10, 0x40080, 0xaabbccdd, 0xaabbccdc))

    def test_provider_can_change_live_sp_and_return_address(self):
        memory = {}
        w.store32(memory, w.SLOT, 0x1001)
        def provider(target, frame, bus):
            w.store32(bus, 0x300c, 0x5679)
            return 0xffffffff, 0x3000
        result = w.project(w.CODE, memory, 0x2000, 0x1234, provider)
        self.assertEqual(result, (0x0fffffff, 0x3010, 0x5679, 0x5678))

    def test_wrap_precedes_shift(self):
        memory = {}
        w.store32(memory, w.SLOT, 0)
        result = w.project(w.CODE, memory, 0x2000, 0, lambda target, frame, bus: (0x80000000, frame))
        self.assertEqual(result[0], 0)
        self.assertNotEqual(result[0], (0x80000000 * 10) >> 4)

    def test_fixed_overflow_boundary_vectors(self):
        for raw, expected in ((0, 0), (1, 0), (2, 1),
                              (0x19999999, 0x0fffffff), (0x1999999a, 0),
                              (0x80000000, 0), (0xffffffff, 0x0fffffff)):
            with self.subTest(raw=raw):
                memory = {}
                w.store32(memory, w.SLOT, 0)
                result = w.project(w.CODE, memory, 0x2000, 0, lambda target, frame, bus: (raw, frame))
                self.assertEqual(result[0], expected)

    def test_unknown_live_stack_read_fails(self):
        memory = {}
        w.store32(memory, w.SLOT, 0)
        with self.assertRaisesRegex(ValueError, 'unmapped synthetic read'):
            w.project(w.CODE, memory, 0x2000, 0, lambda target, frame, bus: (0, 0x3000))

    def test_mul_field_change_rejected_even_if_identity_pin_changes(self):
        original = w.CODE
        try:
            changed = bytearray(original)
            changed[14] ^= 0x80  # change mul destination register
            w.CODE = bytes(changed)
            with self.assertRaisesRegex(ValueError, 'mul a0'):
                w.validate(changed)
        finally:
            w.CODE = original


if __name__ == '__main__':
    unittest.main()
