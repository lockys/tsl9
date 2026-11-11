import runpy
import unittest

m = runpy.run_path('scripts/check-rf-copy-provenance.py')


class ProvenanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = m['bulk']['base']['base']['IMAGE'].read_bytes()
        cls.header = m['bulk']['base']['base']['HEADER'].read_bytes()
        cls.raw = (m['ROOT'] / 'analysis/v131-startup-source/wchble_rom.hex').read_bytes()
        cls.mem = m['sparse']['parse'](cls.raw)

    def test_original(self):
        self.assertEqual(m['check'](self.image, self.header, self.raw)['call_target'], '0x20000332')

    def test_raw_mutations_without_hash_gate(self):
        # Call, loader source, copy LBU, SB and loop branch respectively.
        for pc in (0x64e20, 0x6de46, 0x405c8, 0x405d2, 0x405d6):
            with self.subTest(pc=hex(pc)):
                image = bytearray(self.image)
                image[pc - 0x40000] ^= 1
                with self.assertRaises(ValueError):
                    m['check_raw'](image, self.mem)

    def test_sparse_missing_and_corruption(self):
        for pc in (0x405a2, 0x6eaa4):
            mem = self.mem.copy()
            del mem[pc]
            with self.subTest(pc=hex(pc)), self.assertRaises(ValueError):
                m['check_raw'](self.image, mem)
        mem = self.mem.copy()
        mem[0x6eb2c] = 0
        with self.assertRaises(ValueError):
            m['check_raw'](self.image, mem)
        with self.assertRaises(ValueError):
            m['check'](self.image, self.header, self.raw[:-1])


if __name__ == '__main__':
    unittest.main()
