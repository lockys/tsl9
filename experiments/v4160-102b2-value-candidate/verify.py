"""Offline byte identity and abstract model checks; does not execute C or ISA."""
import hashlib
from pathlib import Path
import unittest

BASE = 0x8000
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
# Contiguous real instruction sequence, including branches and the store.
WINDOW = bytes.fromhex('41 11 22 c4 03 44 75 00 83 47 65 00 26 c2 05 88 22 04 5d 8c 06 c6 93 07 f0 1f aa 84 63 13 f4 00 01 44 83 d7 01 05 63 8e 87 10 23 98 81 04')
START = 0x10288 - BASE


def check_window(data):
    if len(data) < START + len(WINDOW) or data[START:START + len(WINDOW)] != WINDOW:
        raise ValueError('instruction window mismatch')


def check_image(data):
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('firmware identity mismatch')
    check_window(data)


def model(p6, p7, old):
    raw = p6 | ((p7 & 1) << 8)
    value = 0 if raw == 0x1ff else raw
    return value, old != value


class Verify(unittest.TestCase):
    def test_image_and_window_mutations(self):
        data = IMAGE.read_bytes()
        check_image(data)
        for bad in (data[:-1], data + b'\0', bytes([data[0] ^ 1]) + data[1:]):
            with self.assertRaises(ValueError):
                check_image(bad)
        for i in range(len(WINDOW)):
            for bit in range(8):
                bad = bytearray(data)
                bad[START + i] ^= 1 << bit
                with self.assertRaises(ValueError):
                    check_window(bad)
        with self.assertRaises(ValueError):
            check_window(data[:START + len(WINDOW) - 1])
        # Outside the window does not alter the window check, but fails whole-image pin.
        bad = bytearray(data)
        bad[START - 1] ^= 1
        check_window(bad)
        with self.assertRaises(ValueError):
            check_image(bad)

    def test_exhaustive_inputs_and_old_boundaries(self):
        for p6 in range(256):
            for p7 in range(256):
                raw = p6 + 256 * (p7 % 2)
                expected = 0 if raw == 511 else raw
                for old in {0, 1, 0x1fe, 0x1ff, 0x200, 0xffff,
                            expected, (expected - 1) & 0xffff, (expected + 1) & 0xffff}:
                    self.assertEqual(model(p6, p7, old), (expected, old != expected))

    def test_explicit_edges(self):
        self.assertEqual(model(255, 1, 0), (0, False))
        self.assertEqual(model(255, 255, 0xffff), (0, True))
        self.assertEqual(model(254, 1, 0x1fe), (0x1fe, False))
        self.assertEqual(model(255, 0, 0x100), (0xff, True))
        self.assertEqual(model(0, 2, 0), (0, False))


if __name__ == '__main__':
    unittest.main()
