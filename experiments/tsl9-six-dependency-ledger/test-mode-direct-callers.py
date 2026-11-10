"""Offline mutation tests using only permitted image regions."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('scanner', Path(__file__).with_name('check-mode-direct-callers.py'))
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class ScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with scanner.IMAGE.open('rb') as f:
            cls.regions = {}
            for lo, hi in scanner.RANGES:
                f.seek(lo-scanner.BASE)
                cls.regions[lo] = f.read(hi-lo)

    def reader(self, changes=()):
        def read(addr, size):
            for lo, data in self.regions.items():
                if lo <= addr and addr+size <= lo+len(data):
                    result = bytearray(data[addr-lo:addr-lo+size])
                    for location in changes:
                        if addr <= location < addr+size:
                            result[location-addr] ^= 1
                    return bytes(result)
            raise AssertionError('excluded read')
        return read

    def test_original(self):
        self.assertEqual(tuple(scanner.verify(self.reader())), scanner.EXPECTED)

    def test_each_fixed_window_mutation(self):
        for addr in scanner.WINDOWS:
            with self.subTest(addr=hex(addr)), self.assertRaises(ValueError):
                scanner.verify(self.reader((addr,)))

    def test_transfer_destination_mutation(self):
        with self.assertRaises(ValueError):
            scanner.verify(self.reader((0xa226,)))

    def test_short_read(self):
        with self.assertRaises(ValueError):
            scanner.verify(lambda addr, size: self.reader()(addr, size)[:-1])


if __name__ == '__main__':
    unittest.main()
