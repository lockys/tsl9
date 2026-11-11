import runpy
import unittest

m = runpy.run_path('scripts/check-rf-3534-bulk.py')

class BulkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = m['base']['base']['IMAGE'].read_bytes()
        cls.header = m['base']['base']['HEADER'].read_bytes()

    def test_original(self):
        self.assertTrue(m['verify'](self.image, self.header)['helper_effects_unverified'])

    def test_each_instruction_mutation_independent_of_image_hash(self):
        for pc, raw in m['INSNS'].items():
            for i in range(len(raw)//2):
                with self.subTest(pc=hex(pc), byte=i):
                    data = bytearray(self.image)
                    data[pc - 0x40000 + i] ^= 1
                    with self.assertRaises(ValueError):
                        m['verify_instructions'](data)

    def test_interval_boundaries(self):
        hit = m['overlaps']
        self.assertFalse(hit(0x20003540, 32))
        self.assertFalse(hit(0x20003533, 1))
        self.assertTrue(hit(0x20003533, 2))
        self.assertTrue(hit(0x20003537, 1))
        self.assertFalse(hit(0x20003538, 1))
        self.assertFalse(hit(0x20003534, 0))
        with self.assertRaises(ValueError):
            hit(0xffffffff, 2)

    def test_truncation(self):
        with self.assertRaises(ValueError):
            m['verify_instructions'](self.image[:0x24e25])

if __name__ == '__main__':
    unittest.main()
