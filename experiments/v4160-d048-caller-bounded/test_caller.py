"""Offline reference-byte check; no execution or CFG completeness claim."""
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
SITE = 0x13928


def decode_jal(word, pc):
    if word & 0x7f != 0x6f:
        raise ValueError('not JAL')
    immediate = (((word >> 31) & 1) << 20 | ((word >> 12) & 0xff) << 12 |
                 ((word >> 20) & 1) << 11 | ((word >> 21) & 0x3ff) << 1)
    if immediate & (1 << 20):
        immediate -= 1 << 21
    return ((word >> 7) & 31, (pc + immediate) & 0xffffffff)


def validate_window(window):
    if len(window) != 8:
        raise ValueError('window length')
    if decode_jal(int.from_bytes(window[:4], 'little'), SITE) != (1, 0xd048):
        raise ValueError('unexpected JAL')
    if window[4:] != bytes.fromhex('230ca100'):
        raise ValueError('unexpected following instruction')


def validate_reference(data):
    if len(data) != 76800:
        raise ValueError('reference length')
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('reference digest')
    window = data[SITE-BASE:SITE-BASE+8]
    validate_window(window)
    return window


class CallerTest(unittest.TestCase):
    def test_pinned_reference(self):
        with BIN.open('rb') as f:
            data = f.read(76801)
        self.assertEqual(validate_reference(data).hex(), 'ef900ff2230ca100')

    def test_reference_rejection(self):
        with BIN.open('rb') as f:
            data = f.read(76801)
        changed = bytearray(data)
        changed[0] ^= 1
        for candidate in (data[:-1], data + b'\0', changed):
            with self.subTest(length=len(candidate)):
                with self.assertRaises(ValueError):
                    validate_reference(candidate)

    def test_negative_controls(self):
        original = bytes.fromhex('ef900ff2230ca100')
        for index, bit in ((0, 1), (1, 1), (2, 0x10), (4, 1), (7, 1)):
            changed = bytearray(original)
            changed[index] ^= bit
            with self.subTest(index=index, bit=bit):
                with self.assertRaises(ValueError):
                    validate_window(changed)
        for candidate in (b'', original[:-1], original + b'\0'):
            with self.assertRaises(ValueError):
                validate_window(candidate)

    def test_jal_sign_extension_and_register(self):
        self.assertEqual(decode_jal(0x000000ef, 0x100), (1, 0x100))
        self.assertEqual(decode_jal(0xfffff0ef, 0x100), (1, 0xfe))
        self.assertEqual(decode_jal(0x000002ef, 0x100), (5, 0x100))
        self.assertEqual(decode_jal(0x7ffff0ef, 0), (1, 0xffffe))
        self.assertEqual(decode_jal(0x800000ef, 0x100000), (1, 0))
        self.assertEqual(decode_jal(0x002000ef, 0xfffffffe), (1, 0))


if __name__ == '__main__':
    unittest.main()
