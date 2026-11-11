import runpy
import unittest

m = runpy.run_path('scripts/check-rf-3534-config.py')

class ConfigWindowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = m['base']['IMAGE'].read_bytes()
        cls.header = m['base']['HEADER'].read_bytes()

    def test_positive(self):
        result = m['verify'](self.image, self.header)
        self.assertTrue(result['conditional_alias_not_initialization'])
        self.assertNotEqual(result['pointer_word'], result['config_allocator_word'])

    def test_each_window_mutation_rejected_without_full_image_hash(self):
        for start, end in m['WINDOWS']:
            for pc in (start, end - 1):
                with self.subTest(pc=hex(pc)):
                    image = bytearray(self.image)
                    image[pc - 0x40000] ^= 1
                    with self.assertRaises(ValueError):
                        m['verify_windows'](image)

    def test_truncation_and_full_image_identity(self):
        with self.assertRaises(ValueError):
            m['verify_windows'](self.image[:0x24f03])
        image = bytearray(self.image)
        image[0] ^= 1
        self.assertTrue(m['verify_windows'](image))
        with self.assertRaises(ValueError):
            m['verify'](image, self.header)

if __name__ == '__main__':
    unittest.main()
