"""Read-only source-bound listing audit; no firmware or hardware execution."""
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
SHA = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
SPANS = ((0x2260, 0x229e), (0x20e6, 0x2126), (0x2fe2, 0x30a8))


def check_listing(raw, rows):
    """Check every contiguous instruction byte, including fall-throughs and loops.

    Mnemonics are retained disassembler output, not independently decoded here.
    """
    i = 0
    for start, end in SPANS:
        pc = start
        while pc < end:
            if i >= len(rows):
                raise ValueError('missing row')
            row = rows[i]
            b = bytes.fromhex(row['bytes'])
            if row['addr'] != pc or row['size'] != len(b) or len(b) not in (2, 4):
                raise ValueError('instruction boundary mismatch')
            if pc + len(b) > end or raw[pc-0x1000:pc-0x1000+len(b)] != b:
                raise ValueError(f'instruction bytes mismatch at {pc:#x}')
            pc += len(b)
            i += 1
    if i != len(rows):
        raise ValueError('extra row')


class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = IMAGE.read_bytes()
        listing = (HERE / 'listing.json').read_bytes()
        if hashlib.sha256(listing).hexdigest() != '4ff67c0379fcbecc9d87341a026f1d835caf5fdb33d0eb3cbfc401e0cb2d1f4c':
            raise ValueError('listing changed')
        cls.rows = json.loads(listing)

    def test_identity_and_all_instruction_bytes(self):
        self.assertEqual(len(self.raw), 12288)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), SHA)
        self.assertEqual(int.from_bytes(self.raw[0x38:0x3c], 'little'), 0x1000)
        self.assertEqual(len(self.rows), 119)
        check_listing(self.raw, self.rows)

    def test_negative_instruction_mutations_without_hash_gate(self):
        # W call, wrapper erase call, erase address, poll branch, program store,
        # program loop, and wrapper fall-through to program: separate path anchors.
        for pc in (0x2272, 0x2108, 0x3028, 0x3036, 0x3078, 0x3084, 0x2110):
            with self.subTest(pc=hex(pc)):
                raw = bytearray(self.raw)
                raw[pc-0x1000] ^= 1
                with self.assertRaises(ValueError):
                    check_listing(raw, self.rows)

    def test_negative_listing_coverage(self):
        for rows in (self.rows[:-1], self.rows[1:], self.rows + self.rows[:1]):
            with self.assertRaises(ValueError):
                check_listing(self.raw, rows)


if __name__ == '__main__':
    unittest.main(verbosity=2)
