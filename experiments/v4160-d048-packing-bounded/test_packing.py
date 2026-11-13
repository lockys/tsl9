"""Bounded arithmetic model, not an emulator or a complete CFG proof."""
import hashlib
from pathlib import Path
import random
import unittest

BIN = (Path(__file__).resolve().parents[2] /
       'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
DIGEST = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOW = bytes.fromhex(
    'ef900ff2230ca1000545efc0efff1375f57f9317850062453707f8ff'
    '1307f70f798d5d8d2acc0145efc00ffe1375f57f931735016245370708c0'
    '7d17798d5d8d2acc')
MASK32 = 0xffffffff


def stores(entry_word, byte_result, first_result, second_result):
    """Entry word is immediately before sb; assume no later external writes."""
    word = (entry_word & 0xffffff00) | (byte_result & 0xff)
    first = (word & 0xfff800ff) | ((first_result & 0x7ff) << 8)
    second = (first & 0xc007ffff) | ((second_result & 0x7ff) << 19)
    return word, first, second


class PackingTest(unittest.TestCase):
    def test_reference_window(self):
        with BIN.open('rb') as f:
            data = f.read(76801)
        self.assertEqual(len(data), 76800)
        self.assertEqual(hashlib.sha256(data).hexdigest(), DIGEST)
        self.assertEqual(data[0x13928 - 0x8000:0x1396a - 0x8000], WINDOW)

    def test_each_input_bit(self):
        for bit in range(32):
            with self.subTest(source='entry', bit=bit):
                initial, first, final = stores(1 << bit, 0, 0, 0)
                self.assertEqual(initial, (1 << bit) & 0xffffff00)
                self.assertEqual(first, (1 << bit) & 0xfff80000)
                self.assertEqual(final, (1 << bit) & 0xc0000000)
            with self.subTest(source='byte', bit=bit):
                self.assertEqual(stores(0, 1 << bit, 0, 0)[2], (1 << bit) & 0xff)
            with self.subTest(source='first', bit=bit):
                self.assertEqual(stores(0, 0, 1 << bit, 0)[2], ((1 << bit) & 0x7ff) << 8)
            with self.subTest(source='second', bit=bit):
                self.assertEqual(stores(0, 0, 0, 1 << bit)[2], ((1 << bit) & 0x7ff) << 19)

    def test_composed_formula(self):
        rng = random.Random(0xd048)
        for _ in range(4096):
            old, byte, first, second = (rng.getrandbits(32) for _ in range(4))
            expected_initial = (old & 0xffffff00) | (byte & 0xff)
            expected_first = ((old & 0xfff80000) | (byte & 0xff) |
                              ((first & 0x7ff) << 8))
            expected_final = ((old & 0xc0000000) | (byte & 0xff) |
                              ((first & 0x7ff) << 8) | ((second & 0x7ff) << 19))
            self.assertEqual(stores(old, byte, first, second),
                             (expected_initial, expected_first, expected_final & MASK32))


if __name__ == '__main__':
    unittest.main()
