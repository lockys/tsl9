import importlib.util
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rfinit', ROOT / 'scripts/check-rf-3538-init.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class RFInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = m.HEX.read_bytes()
        cls.mem = runpy.run_path(str(ROOT / 'analysis/v131-startup-source/check.py'))['parse'](cls.raw)

    def test_actual(self):
        r = m.verify(self.raw)
        self.assertEqual(r['copy_ranges'], [(0x20000040, 0x20002e74), (0x20002e70, 0x20002efc)])
        self.assertEqual(r['zero_range'], (0x20002ef8, 0x20003618))
        self.assertEqual(r['copy_overlaps'], [False, False])
        self.assertTrue(r['zero_overlaps'])
        self.assertFalse(r['rf_overlaps'])
        self.assertEqual(r['missing_source'], [0x6eb2c, 0x6eb30])

    def test_raw_instruction_mutations(self):
        for pc in (0x40280, 0x402a2, 0x402a8, 0x6de5e, 0x6de7a, 0x64bd2, 0x64be4, 0x64bf2):
            with self.subTest(pc=hex(pc)):
                mem = self.mem.copy()
                mem[pc] ^= 1
                with self.assertRaises((ValueError, AssertionError)):
                    m.inspect(mem)
        mem = self.mem.copy()
        del mem[0x64bd2]
        with self.assertRaises(ValueError):
            m.inspect(mem)
        mem = self.mem.copy()
        mem[0x6eb2c] = 0  # fabricated missing ROM is not admitted
        with self.assertRaises(ValueError):
            m.inspect(mem)

    def test_identity_and_boundaries(self):
        raw = bytearray(self.raw)
        raw[20] ^= 1
        with self.assertRaises(ValueError): m.verify(raw)
        with self.assertRaises(ValueError): m.verify(self.raw[:-1])
        self.assertFalse(m.overlap((0x2000353c, 0x20003540), m.TARGET))
        self.assertFalse(m.overlap((0x20003534, 0x20003538), m.TARGET))
        self.assertTrue(m.overlap((0x20003537, 0x20003539), m.TARGET))

if __name__ == '__main__': unittest.main()
