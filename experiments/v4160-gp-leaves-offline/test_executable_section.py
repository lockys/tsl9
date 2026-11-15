#!/usr/bin/env python3
"""Exercise GP leaf ELF extraction using synthetic, non-runnable ELF32 fixtures."""
import importlib.util
from pathlib import Path
import struct
import subprocess
import sys
import unittest

spec = importlib.util.spec_from_file_location('gp_verify_compiled', Path(__file__).with_name('verify_compiled.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
LEAVES, executable_section = module.LEAVES, module.executable_section


def fixture(address, leaf):
    # One executable LOAD and one allocated executable PROGBITS section.
    data = bytearray(0x180)
    ident = b'\x7fELF\x01\x01\x01' + bytes(9)
    struct.pack_into('<16sHHIIIIIHHHHHH', data, 0, ident, 2, 243, 1,
                     address, 52, 0x100, 0, 52, 32, 1, 40, 2, 0)
    struct.pack_into('<8I', data, 52, 1, 0x80, address, address,
                     len(leaf), len(leaf), 5, 2)
    data[0x80:0x80 + len(leaf)] = leaf
    struct.pack_into('<10I', data, 0x128, 0, 1, 6, address,
                     0x80, len(leaf), 0, 0, 2, 0)
    return data


class ExecutableSectionTests(unittest.TestCase):
    def setUp(self):
        self.address = 0x10402
        self.original = LEAVES[self.address][2]
        self.data = fixture(self.address, self.original)

    def reject(self, offset, value, message):
        struct.pack_into('<I', self.data, offset, value)
        with self.assertRaisesRegex(ValueError, message):
            executable_section(self.data, self.address)

    def test_extracts_both_leaf_bytes(self):
        for address, (_, _, leaf) in LEAVES.items():
            self.assertEqual(executable_section(fixture(address, leaf), address), leaf)

    def test_header_and_tables(self):
        self.data[4] = 2
        with self.assertRaisesRegex(ValueError, 'ELF32 RISC-V executable'):
            executable_section(self.data, self.address)
        self.data = fixture(self.address, self.original)
        struct.pack_into('<H', self.data, 40, 0)
        with self.assertRaisesRegex(ValueError, 'ELF header size'):
            executable_section(self.data, self.address)
        self.data = fixture(self.address, self.original)
        self.reject(28, len(self.data), 'ELF bounds')
        with self.assertRaisesRegex(ValueError, 'ELF header'):
            executable_section(self.data[:51], self.address)

    def test_section_flags_address_and_bounds(self):
        self.reject(0x128 + 8, 2, 'one executable section')
        self.data = fixture(self.address, self.original)
        self.reject(0x128 + 12, self.address + 2, 'one executable section')
        self.data = fixture(self.address, self.original)
        self.reject(0x128 + 16, len(self.data), 'section bounds')

    def test_load_permissions_size_and_mapping(self):
        self.reject(52 + 24, 4, 'section must be file-backed')
        self.data = fixture(self.address, self.original)
        self.reject(52 + 20, 1, 'load bounds')
        self.data = fixture(self.address, self.original)
        self.reject(52 + 8, self.address + 2, 'section must be file-backed')
        self.data = fixture(self.address, self.original)
        self.reject(52 + 4, 0x7e, 'section must be file-backed')

    def test_load_alignment(self):
        self.reject(52 + 28, 3, 'load alignment')
        self.data = fixture(self.address, self.original)
        self.reject(52 + 28, 4096, 'load alignment')
        for value in (0, 1, 2):
            self.data = fixture(self.address, self.original)
            struct.pack_into('<I', self.data, 52 + 28, value)
            self.assertEqual(executable_section(self.data, self.address), self.original)

    def test_module_import_by_name(self):
        result = subprocess.run([sys.executable, '-c', 'import verify_compiled; exit(0 if callable(verify_compiled.run) else 1)'],
                                cwd=Path(__file__).parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_candidate_sections_rejected(self):
        struct.pack_into('<H', self.data, 48, 3)
        self.data.extend(bytes(40))
        self.data[0x150:0x178] = self.data[0x128:0x150]
        with self.assertRaisesRegex(ValueError, 'one executable section'):
            executable_section(self.data, self.address)


if __name__ == '__main__':
    unittest.main()
