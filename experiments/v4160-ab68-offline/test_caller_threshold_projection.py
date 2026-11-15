#!/usr/bin/env python3
"""Boundary and semantic controls for the bounded caller fragment."""
import hashlib
import unittest
from unittest.mock import patch
import caller_threshold_projection as p


class ThresholdProjection(unittest.TestCase):
    def test_original_image(self):
        image = p.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), p.SHA)
        self.assertEqual(image[p.START-0x8000:p.START-0x8000+len(p.CODE)], p.CODE)

    def test_wide_return_and_wrapping_load(self):
        for value in (0, 255, 256, 0x80000000, 0xffffffff):
            threshold = (5 * value + 10) & 255
            self.assertEqual(p.run(p.CODE, value, 0xfffffecc, {0: 0x7f}),
                             (threshold, 0x7f, threshold, [('read', 0, 0x7f)]))
        with self.assertRaises(KeyError):
            p.run(p.CODE, 1, 0, {})

    def test_identity_rejects_mutations(self):
        for i in range(len(p.CODE)):
            changed = bytearray(p.CODE)
            changed[i] ^= 1
            with self.subTest(offset=i), self.assertRaisesRegex(ValueError, 'instruction bytes'):
                p.run(bytes(changed), 0, 0, {})

    def test_semantic_mutation_after_replacing_pin(self):
        # ANDI immediate 255 -> 254; witness isolates its low bit.
        changed = bytearray(p.CODE)
        changed[14] ^= 0x10
        with patch.object(p, 'CODE', bytes(changed)):
            self.assertEqual(p.run(bytes(changed), 1, 0, {308: 7}),
                             (14, 7, 14, [('read', 308, 7)]))
        self.assertEqual(p.run(p.CODE, 1, 0, {308: 7}),
                         (15, 7, 15, [('read', 308, 7)]))


if __name__ == '__main__':
    unittest.main()
