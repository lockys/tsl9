#!/usr/bin/env python3
"""Mutation controls for the AB68 original direct-call evidence."""
import hashlib
from pathlib import Path
import unittest
import caller_sites as sites

BIN = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'

class CallerSites(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = BIN.read_bytes()

    def test_original(self):
        self.assertEqual(sites.inspect(self.image), (0x10394, 0x13ac6))

    def test_opcode_register_and_target(self):
        for pc, code in sites.SITES:
            for offset, mask in ((0, 1), (0, 0x80)):
                mutated = bytearray(code)
                mutated[offset] ^= mask
                with self.subTest(pc=pc, offset=offset), self.assertRaisesRegex(ValueError, 'JAL opcode or link register'):
                    sites.decode_jal(pc, mutated)
            mutated = bytearray(code)
            mutated[2] ^= 0x10
            self.assertNotEqual(sites.decode_jal(pc, mutated), sites.TARGET)
        with self.assertRaisesRegex(ValueError, 'JAL length'):
            sites.decode_jal(0x10394, b'\xef')

    def test_identity_and_rehashed_instruction_mutations(self):
        for pc, _ in sites.SITES:
            altered = bytearray(self.image)
            altered[pc-sites.BASE] ^= 1
            with self.assertRaisesRegex(ValueError, 'image SHA-256'):
                sites.inspect(altered)
            old = sites.SHA256
            try:
                sites.SHA256 = hashlib.sha256(altered).hexdigest()
                with self.assertRaisesRegex(ValueError, 'site bytes'):
                    sites.inspect(altered)
            finally:
                sites.SHA256 = old

if __name__ == '__main__':
    unittest.main()
