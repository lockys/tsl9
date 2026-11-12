import hashlib
from pathlib import Path
import unittest

from pcrel import decode_s, decode_target, patch_pair, patch_s, split_delta

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'


class PairTests(unittest.TestCase):
    def test_original_evidence(self):
        data = IMAGE.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
        self.assertEqual(data[0x7666:0x7672].hex(), '854717d7ff1fa308f7928280')
        hi = int.from_bytes(data[0x7668:0x766c], 'little')
        store = int.from_bytes(data[0x766c:0x7670], 'little')
        self.assertEqual(decode_s(store), -1743)
        self.assertEqual(decode_target(hi, store, 0xf668), 0x2000bf99)
        self.assertEqual(patch_pair(hi & 0xfff, patch_s(store, 0), 0xf668, 0x20004000, 0x7f99), (hi, store))

    def test_all_immediates_and_preservation(self):
        for imm in range(-2048, 2048):
            patched = patch_s(0x92f708a3, imm)
            self.assertEqual(decode_s(patched), imm)
            self.assertEqual(patched & ~0xfe000f80, 0x92f708a3 & ~0xfe000f80)
        for imm in (-2049, 2048, -4096, 4095):
            with self.assertRaises(ValueError):
                patch_s(0x92f708a3, imm)

    def test_rounding_and_wrap(self):
        for delta, expected in [(0x7ff, (0, 2047)), (0x800, (1, -2048)),
                                (-0x800, (0, -2048)), (-0x801, (0xfffff, 2047)),
                                (0x7fffffff, (0x80000, -1)), (-0x80000000, (0x80000, 0))]:
            self.assertEqual(split_delta(0, delta & 0xffffffff), expected)
        for pc, target, addend in [(0xfffffff0, 0x10, 0), (0x10, 0xfffffff0, 0),
                                    (0xffffffff, 0xffffffff, 2), (0, 0x7fffffff, 1)]:
            hi, store = patch_pair(0x717, 0x00f70023, pc, target, addend)
            self.assertEqual(decode_target(hi, store, pc), (target + addend) & 0xffffffff)

    def test_anchor_not_low_pc(self):
        hi, store = patch_pair(0x717, 0x00f70023, 0xf668, 0x20004000, 0x7f99)
        self.assertEqual(decode_target(hi, store, 0xf668), 0x2000bf99)
        self.assertEqual(decode_target(hi, store, 0xf66c), 0x2000bf9d)
        self.assertNotEqual(patch_pair(0x717, 0x00f70023, 0xf66c, 0x20004000, 0x7f99), (hi, store))

    def test_invalid_opcodes_and_words(self):
        for invalid in (0x00000003, 0x00000013, -1, 0x100000000):
            with self.assertRaises(ValueError):
                patch_s(invalid, 0)
            with self.assertRaises(ValueError):
                decode_s(invalid)
        with self.assertRaises(ValueError):
            patch_pair(0x37, 0x23, 0, 0)
        with self.assertRaises(ValueError):
            decode_target(0x37, 0x23, 0)
        for pc, target in [(-1, 0), (0, 0x100000000)]:
            with self.assertRaises(ValueError):
                split_delta(pc, target)


if __name__ == '__main__':
    unittest.main()
