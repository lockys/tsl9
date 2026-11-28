"""Reject corrupted UUID ownership in actual fresh C/C++ ELF structures."""
import argparse
import copy
import struct
from pathlib import Path
import unittest

import check


class OwnershipTests(unittest.TestCase):
    builds = []

    def check_mutation(self, mutate=None):
        for elf in self.builds:
            with self.subTest(mode=elf._mode):
                value = copy.deepcopy(elf)
                if mutate is None:
                    check.diagnostic_header(value)
                    check.uuid_owner(value)
                else:
                    mutate(value)
                    with self.assertRaises(ValueError):
                        check.diagnostic_header(value)
                        check.uuid_owner(value)

    def test_actual(self):
        self.check_mutation()

    def test_missing_symbol(self):
        self.check_mutation(lambda e: setattr(e, 'symbols', [s for s in e.symbols if s['name'] != 'tsl9_gatt_write_UUID_1ab44']))

    def test_duplicate_symbol(self):
        def mutate(e):
            e.symbols.append(copy.copy(next(s for s in e.symbols if s['name'] == 'tsl9_gatt_write_UUID_1ab44')))
        self.check_mutation(mutate)

    def test_symbol_extent(self):
        def mutate(e):
            next(s for s in e.symbols if s['name'] == 'tsl9_gatt_write_UUID_1ab44')['size'] = 4
        self.check_mutation(mutate)

    def test_symbol_owner(self):
        def mutate(e):
            next(s for s in e.symbols if s['name'] == 'tsl9_gatt_write_UUID_1ab44')['index'] = 0
        self.check_mutation(mutate)

    def test_overlap(self):
        def mutate(e):
            next(s for s in e.sections if s['address'] == 0x1ab46)['address'] = 0x1ab45
        self.check_mutation(mutate)

    def test_wrong_uuid(self):
        def mutate(e):
            section = next(s for s in e.sections if s['address'] == 0x1ab44)
            raw = bytearray(e.raw)
            raw[section['offset']] ^= 1
            e.raw = bytes(raw)
        self.check_mutation(mutate)

    def test_obsolete_owner(self):
        def mutate(e):
            symbol = copy.copy(next(s for s in e.symbols if s['name'] == 'tsl9_gatt_write_UUID_1ab44'))
            symbol['name'] = 'tsl9_opaque_gap_0001ab44'
            e.symbols.append(symbol)
        self.check_mutation(mutate)

    def test_nonzero_entry(self):
        def mutate(e):
            raw = bytearray(e.raw)
            struct.pack_into('<I', raw, 24, 0x8000)
            e.raw = bytes(raw)
        self.check_mutation(mutate)

    def test_loadable_header(self):
        def mutate(e):
            raw = bytearray(e.raw)
            phoff = struct.unpack_from('<I', raw, 28)[0]
            struct.pack_into('<I', raw, phoff, 1)
            e.raw = bytes(raw)
        self.check_mutation(mutate)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-root', type=Path, required=True)
    args = parser.parse_args()
    for mode in ('c', 'cpp'):
        elf = check.ELF(args.build_root / 'build' / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf'))
        elf._mode = mode
        OwnershipTests.builds.append(elf)
    unittest.main(argv=['test_ownership'], verbosity=2)
