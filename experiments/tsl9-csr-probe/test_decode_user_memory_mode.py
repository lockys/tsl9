import unittest
from decode_user_memory_mode import decode

class UserMemoryModeTest(unittest.TestCase):
    def test_all_three_bit_values(self):
        expected = [(128, 64), (128, 64), (144, 48), (144, 48)] + [(160, 32)] * 4
        for mode, pair in enumerate(expected):
            with self.subTest(mode=mode):
                actual = decode(mode)
                self.assertEqual((actual["code_kib"], actual["ram_kib"]), pair)

    def test_invalid_values(self):
        for value in (-1, 8, True, None, "0", 1.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode(value)
