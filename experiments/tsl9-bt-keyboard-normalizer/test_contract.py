"""Cross-check three bounded branch models; not an instruction emulator."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


eight = load('keyboard_eight', 'tsl9-bt-keyboard-local/test_local.py')
five = load('keyboard_five', 'tsl9-bt-keyboard-s4-5/test_branch.py')
two = load('keyboard_two', 'tsl9-bt-keyboard-s4-two/test_static.py')


class NormalizerContract(unittest.TestCase):
    def test_equivalent_values(self):
        value8 = eight.eight_byte_path(bytes([0x33, 0, 0x44, 0, 0, 0, 0, 0]), bytes([0x11, 0x22]))
        exit5, value5 = five.model(5, bytes([0x44, 0, 0, 0, 0]), bytes([0x11, 0x22, 0x33]))
        exit2, value2 = two.model(2, bytes([0x42, 2]), bytes([0x11, 0x22, 0x33]), 0)
        self.assertEqual((value8, value5, value2), (0x11223344,) * 3)
        self.assertEqual((exit5, exit2), (0x11c64, '0x11c78'))

    def test_rejection_boundaries(self):
        self.assertIsNone(eight.eight_byte_path(bytes([1, 1, 0, 0, 0, 0, 0, 0]), bytes(2)))
        self.assertEqual(five.model(5, bytes(5), bytes(3)), (0x1240c, None))
        self.assertEqual(two.model(2, bytes([1, 3]), bytes(3), 0), ('exit', None))
        self.assertEqual(two.model(2, bytes(2), bytes(3), 0), ('exit', 0))
        # The 8-byte branch's value zero is rejected by the subsequent 0x11c60 check.
        self.assertEqual(eight.eight_byte_path(bytes(8), bytes(2)), 0)

    def test_all_other_s4_values_follow_rejection_path(self):
        data = two.APP.read_bytes()
        for pc in (0x11cde, 0x11dd0, 0x11e18):
            word = int.from_bytes(data[pc-0x8000:pc-0x8000+4], 'little')
            self.assertEqual(((word >> 12) & 7, (word >> 15) & 31, (word >> 20) & 31), (1, 20, 15))
        for length in range(256):
            if length not in (2, 5, 8):
                self.assertEqual(five.model(length, b'', b''), (0x11e16, None))
                self.assertEqual(two.model(length, b'', b'', 0), ('exit', None))

    def test_wrap_is_local_to_low_byte(self):
        self.assertEqual(two.model(2, bytes([255, 2]), bytes([1, 2, 3]), 0), ('0x11c78', 0x01020301))

if __name__ == '__main__':
    unittest.main()
