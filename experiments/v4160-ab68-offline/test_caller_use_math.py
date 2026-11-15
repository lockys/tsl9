#!/usr/bin/env python3
"""Finite checks of handwritten AB68 caller projections; not CPU execution."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def threshold(v):
    return (5 * v + 10) & 255


def update(v, value, state):
    t = threshold(v)
    if not state and value > t and t > 59:
        return 1, 159
    if state and value <= t:
        return 0, 158
    return state, None


def pack(v, a, b):
    return (a & 127) | ((v & 1) << 7), (b & 240) | ((v >> 1) & 15)


class CallerMath(unittest.TestCase):
    def test_origim_image(self):
        self.assertEqual(hashlib.sha256(BIN.read_bytes()).hexdigest(), SHA)

    def test_threshold_permutation_and_boundaries(self):
        values = [threshold(v) for v in range(256)]
        self.assertEqual(set(values), set(range(256)))
        self.assertEqual(sum(t > 59 for t in values), 196)
        for v, t in enumerate(values):
            self.assertEqual((205 * (t - 10)) & 255, v)
            for s in (0, 1, 127, 255, 0xffffffff):
                self.assertEqual(update(v, s, 0)[1] == 159, s > t and t > 59)
                self.assertEqual(update(v, s, 7)[1] == 158, s <= t)
        self.assertEqual(update(10, 61, 0), (1, 159))  # t=60
        self.assertEqual(update(10, 60, 7), (0, 158))
        self.assertEqual(update(10, 61, 7), (7, None))

    def test_packed_bits(self):
        for v in range(256):
            for old in range(256):
                a, b = pack(v, old, old)
                self.assertEqual(a & 127, old & 127)
                self.assertEqual(a >> 7, v & 1)
                self.assertEqual(b & 240, old & 240)
                self.assertEqual(b & 15, (v >> 1) & 15)
                self.assertEqual(pack(v ^ 0xe0, old, old), (a, b))


if __name__ == '__main__':
    unittest.main()
