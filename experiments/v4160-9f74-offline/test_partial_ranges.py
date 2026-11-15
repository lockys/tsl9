#!/usr/bin/env python3
"""Ensure partial-coverage tests reach the intended fail-closed checks."""
import struct
import unittest
import audit_original_layout as audit
from test_audit_original_layout import ARTIFACTS

class PartialRanges(unittest.TestCase):
    def test_executable_partial_or_overlapping_ranges(self):
        path = ARTIFACTS / 'c/NONLOADABLE-ORIGINAL-LAYOUT.elf'
        if not path.exists():
            self.skipTest('retained diagnostic ELF is not available')
        original = path.read_bytes()
        image = audit.refs.BIN.read_bytes()
        shoff = struct.unpack_from('<16sHHIIIIIHHHHHH', original)[6]
        self.assertEqual(audit.audit(original, image)['present'], ['0xa356'])
        for addr in (0x9f75, 0xa0b8, 0xa1b8, 0xa356):
            altered = bytearray(original)
            struct.pack_into('<IIIIIIIIII', altered, shoff, 0, 1, 6, addr, 0, 2, 0, 0, 1, 0)
            message = ('partially covered' if addr in (0xa0b8, 0xa1b8)
                       else 'overlapping allocated sections')
            with self.subTest(addr=addr), self.assertRaisesRegex(ValueError, message):
                audit.audit(bytes(altered), image)

if __name__ == '__main__':
    unittest.main()
