import unittest
from decode_user_memory_mode import decode, reset_extent_comparison

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

    def test_hypothetical_reset_extent(self):
        for mode in range(8):
            with self.subTest(mode=mode):
                expected = (0, 0) if mode < 2 else ((2380, 2392) if mode < 4 else (18764, 18776))
                self.assertEqual(reset_extent_comparison(mode)["overflow_bytes_range"], expected)
        self.assertEqual(reset_extent_comparison(0)["ram_end_exclusive"], 0x20010000)
        self.assertEqual(reset_extent_comparison(2)["ram_end_exclusive"], 0x2000C000)
        self.assertEqual(reset_extent_comparison(4)["ram_end_exclusive"], 0x20008000)
