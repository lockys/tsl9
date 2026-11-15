#!/usr/bin/env python3
"""Test the 8202 ELF extractor with synthetic, non-executable ELF files."""
import struct
import unittest

import verify_compiled as candidate


LEAF = bytes.fromhex('174500200345f5cd8280')


def fixture():
    data = bytearray(0x180)
    ident = b'\x7fELF\x01\x01\x01' + bytes(9)
    struct.pack_into('<16sHHIIIIIHHHHHH', data, 0, ident, 2, 243, 1,
                     0x8202, 52, 0x100, 0, 52, 32, 1, 40, 2, 0)
    struct.pack_into('<8I', data, 52, 1, 0x80, 0x8202, 0x8202,
                     len(LEAF), len(LEAF), 5, 2)
    data[0x80:0x80 + len(LEAF)] = LEAF
    struct.pack_into('<10I', data, 0x128, 0, 1, 6, 0x8202,
                     0x80, len(LEAF), 0, 0, 2, 0)
    return data


class ExecutableSectionTests(unittest.TestCase):
    def test_valid_mapping(self):
        self.assertEqual(candidate.executable_section(fixture()), LEAF)

    def test_bad_header_size(self):
        data = fixture()
        struct.pack_into('<H', data, 40, 0)
        with self.assertRaisesRegex(ValueError, 'ELF header size'):
            candidate.executable_section(data)

    def test_alignment_and_congruence(self):
        for value in (3, 4096):
            with self.subTest(alignment=value):
                data = fixture()
                struct.pack_into('<I', data, 52 + 28, value)
                with self.assertRaisesRegex(ValueError, 'load alignment'):
                    candidate.executable_section(data)
        for value in (0, 1, 2):
            with self.subTest(alignment=value):
                data = fixture()
                struct.pack_into('<I', data, 52 + 28, value)
                self.assertEqual(candidate.executable_section(data), LEAF)

    def test_inaccessible_or_duplicate_section(self):
        data = fixture()
        struct.pack_into('<I', data, 52 + 24, 4)
        with self.assertRaisesRegex(ValueError, 'section must be file-backed'):
            candidate.executable_section(data)
        data = fixture()
        struct.pack_into('<H', data, 48, 3)
        data.extend(bytes(40))
        data[0x150:0x178] = data[0x128:0x150]
        with self.assertRaisesRegex(ValueError, 'one executable section'):
            candidate.executable_section(data)

    def test_truncated_tables(self):
        for data in (fixture()[:51], fixture()[:0x140]):
            with self.assertRaises(ValueError):
                candidate.executable_section(data)


if __name__ == '__main__':
    unittest.main()
