#!/usr/bin/env python3
"""Negative and post-provider ordering tests for the 13c4e composition."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('composition', Path(__file__).with_name('state-13c4e-composition.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CompositionTest(unittest.TestCase):
    def setUp(self):
        self.codes = (c.gate.CODE, c.delta.CODE, c.tail.CODE)
        self.first, self.second = (0xffff, 1, 1), (0xfffe, 0, 0)

    def test_post_call_word_not_stale_previous_value(self):
        got = c.compose(self.codes, self.first, self.second, 0x20004000, 0x2000ff00,
                        0x12345678, lambda: (35, 1))
        self.assertEqual((got[2], got[3], got[4]), (None, 0x9124, (0x137c0, 0, 35, 0)))
        got = c.compose(self.codes, self.first, self.second, 0x20004000, 0x2000ff00,
                        0x12345678, lambda: (35, 0))
        self.assertEqual((got[2], got[3], got[4]), ((0x20004154, 35), 0x137c0, (0,)))

    def test_no_provider_call_for_failed_gate(self):
        def fail():
            raise AssertionError('provider must not run')
        got = c.compose(self.codes, (0xfffe, 1, 1), (0xfffe, 1, 1),
                        0, 0x2000ff00, 123, fail)
        self.assertEqual((got[1], got[2], got[3]), ([], None, 0x13cda))

    def test_saved_return_slot_overlap_is_rejected(self):
        sp = 0x2000ff00
        for shift in range(-3, 4):
            with self.subTest(shift=shift), self.assertRaisesRegex(ValueError, 'overlaps'):
                c.compose(self.codes, self.first, self.second, sp-344+shift, sp, 123, lambda: (35, 0))

    def test_jal_decoder_known_targets_and_nonzero_rd_rejection(self):
        # jal x0,+4, jal x0,-4, jal x1,+4
        self.assertEqual(c.tail.jal_target(0x1000, 0x0040006f), 0x1004)
        self.assertEqual(c.tail.jal_target(0x1000, 0xffdff06f), 0x0ffc)
        with self.assertRaises(ValueError):
            c.tail.jal_target(0x1000, 0x004000ef)

    def test_each_original_window_rejected_even_with_recomputed_image_hash(self):
        image = bytearray(0x13cda-c.gate.BASE)
        for start, data in ((c.gate.START, c.gate.CODE), (0x13c9a, c.CALL_BYTES),
                            (c.delta.PC, c.delta.CODE), (c.tail.START, c.tail.CODE)):
            image[start-c.gate.BASE:start-c.gate.BASE+len(data)] = data
        old = c.gate.SHA256
        try:
            c.gate.SHA256 = hashlib.sha256(image).hexdigest()
            self.assertEqual(c.prepare(image), self.codes)
            for offset in (c.gate.START, 0x13c9a, 0x13c9e, c.delta.PC, c.tail.START):
                with self.subTest(offset=hex(offset)), self.assertRaises(ValueError):
                    bad = bytearray(image)
                    bad[offset-c.gate.BASE] ^= 1
                    c.gate.SHA256 = hashlib.sha256(bad).hexdigest()
                    c.prepare(bad)
        finally:
            c.gate.SHA256 = old


if __name__ == '__main__':
    unittest.main()
