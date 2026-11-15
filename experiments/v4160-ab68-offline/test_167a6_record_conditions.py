#!/usr/bin/env python3
"""Static record-match arithmetic at 0x167a6, not a CPU or provider model.

The two table pointers can be reloaded and calls can modify memory. This test
only checks the fixed instruction windows and exhaustive byte-level predicates
for the 158/159 arguments observed at the upstream call boundary.
"""
import hashlib
import unittest
from pathlib import Path

BIN = (Path(__file__).resolve().parents[2] / 'firmware-downloads' /
       'legacy-options-2026-10-20' / 'BINs' / 'ID-2966-V4.1.60-decoded.bin')
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS = {
    0x167c2: bytes.fromhex('83a70900a29703c7070063169700'),
    0x167ee: bytes.fromhex('03a709005697834607000347170093771700a207d58f63989700098b09c7'),
    0x16814: bytes.fromhex('03270a005697834607000347170093771700a207d58f6398f400098b09c7'),
}


class RecordConditions(unittest.TestCase):
    def test_instruction_identity(self):
        image = BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), SHA)
        for address, expected in WINDOWS.items():
            with self.subTest(address=hex(address)):
                self.assertEqual(image[address - 0x8000:address - 0x8000 + len(expected)], expected)

    def test_two_byte_predicate(self):
        # Each test corresponds to the value read at one table position, not
        # an assumption that the whole table or a callback stays unchanged.
        for target in (158, 159):
            hits = 0
            for low in range(256):
                for high in range(256):
                    key = ((high & 1) << 8) | low
                    match = key == target and bool(high & 2)
                    expected = low == target and (high & 3) == 2
                    self.assertEqual(match, expected)
                    hits += match
            self.assertEqual(hits, 64)

    def test_first_table_compares_full_input(self):
        for target in (158, 159, 0x19e, 0xffffffff):
            matched = [first for first in range(256) if first == target]
            self.assertEqual(matched, [target] if target < 256 else [])


if __name__ == '__main__':
    unittest.main()
