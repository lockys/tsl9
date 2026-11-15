#!/usr/bin/env python3
"""Field-level checks of the original AB68 leaf; not CPU execution."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('ab68_decode', HERE.parent / 'v4160-8202-offline-leaf' / 'verify.py')
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)
decoder.PC = 0xab68
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
EXPECTED = bytes.fromhex('17150020034505388280')
TARGET = 0x2000bee8

class InstructionProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = BIN.read_bytes()
        if hashlib.sha256(raw).hexdigest() != decoder.IMAGE_SHA256:
            raise ValueError('firmware SHA-256')
        cls.leaf = raw[decoder.PC-decoder.IMAGE_BASE:decoder.PC-decoder.IMAGE_BASE+10]
        if cls.leaf != EXPECTED:
            raise ValueError('original bytes')

    def test_target_and_zero_extension(self):
        self.assertEqual(decoder.decode(self.leaf), TARGET)
        for value in range(256):
            self.assertEqual(value & 0xff, value)
            self.assertEqual(decoder.sign_extend(value, 8), value if value < 128 else value-256)
        self.assertNotEqual(decoder.sign_extend(0x80, 8), 0x80)

    def test_opcode_register_and_return_mutants(self):
        for offset, mask in ((0, 1), (0, 0x80), (4, 1), (4, 0x80), (5, 0x40), (5, 0x80), (8, 1)):
            mutated = bytearray(self.leaf)
            mutated[offset] ^= mask
            with self.subTest(offset=offset, mask=mask), self.assertRaises(ValueError):
                decoder.decode(mutated)
        for length in (0, 9, 11):
            with self.subTest(length=length), self.assertRaises(ValueError):
                decoder.decode((self.leaf + b'\x00')[:length])

    def test_immediates_change_target(self):
        for offset, mask in ((1, 0x10), (6, 0x10)):
            mutated = bytearray(self.leaf)
            mutated[offset] ^= mask
            self.assertNotEqual(decoder.decode(mutated), TARGET)

if __name__ == '__main__':
    unittest.main()
