"""Bounded raw RV32 store-pattern scan, not a code/reachability analysis."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOT = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
SHA = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'


def gp_store(word):
    if word & 127 != 0x23 or (word >> 15) & 31 != 3:
        return None
    width = {0: 1, 1: 2, 2: 4}.get((word >> 12) & 7)
    if width is None:
        return None
    imm = ((word >> 25) << 5) | ((word >> 7) & 31)
    if imm & 0x800:
        imm -= 4096
    return imm, width, (word >> 20) & 31


def overlaps_task(word):
    store = gp_store(word)
    return store is not None and store[0] <= 124 < store[0] + store[1]


def scan(data):
    return [(0x1000 + i, data[i:i+4].hex(), gp_store(int.from_bytes(data[i:i+4], 'little')))
            for i in range(0, len(data)-3, 2)
            if overlaps_task(int.from_bytes(data[i:i+4], 'little'))]


class Tests(unittest.TestCase):
    def test_image(self):
        data = BOOT.read_bytes()
        self.assertEqual(len(data), 12288)
        self.assertEqual(hashlib.sha256(data).hexdigest(), SHA)
        self.assertEqual(data[0x8ca:0x8ce].hex(), '03c5c107')
        self.assertEqual(scan(data), [])

    def test_positive_and_negative_patterns(self):
        # sb a0,124(gp), sh a0,123(gp), sw a0,121(gp)
        def store(imm, funct3, rs1=3):
            return ((imm >> 5) << 25) | (10 << 20) | (rs1 << 15) | (funct3 << 12) | ((imm & 31) << 7) | 0x23
        for imm, f in ((124, 0), (123, 1), (121, 2)):
            self.assertTrue(overlaps_task(store(imm, f)))
            self.assertEqual(len(scan(store(imm, f).to_bytes(4, 'little'))), 1)
        for word in (store(123, 0), store(120, 2), store(124, 0, 4), 0x07c1c503, store(124, 3)):
            self.assertFalse(overlaps_task(word))
        changed = bytearray(BOOT.read_bytes()); changed[0] ^= 1
        self.assertNotEqual(hashlib.sha256(changed).hexdigest(), SHA)


if __name__ == '__main__':
    unittest.main(verbosity=2)
