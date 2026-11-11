import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('header_window', ROOT / 'scripts/check-rf-tx-header-window.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class HeaderWindowTests(unittest.TestCase):
    def test_hand_encoded_operands(self):
        # c.lw x15, 124(x9); sb x31,-2048(x0); qk.c.sb x15,31(x15).
        self.assertEqual(m.decode_load(bytes.fromhex('fc5c')), (15, 9, 124))
        self.assertEqual(m.decode_sb(bytes.fromhex('2300f081')), (31, 0, -2048))
        self.assertEqual(m.decode_qk_sb(bytes.fromhex('fcbf')), (15, 15, 31))
        for fn, raw in ((m.decode_load, '0000'), (m.decode_sb, '23000000ff'),
                        (m.decode_qk_sb, '0000')):
            with self.assertRaises(ValueError):
                fn(bytes.fromhex(raw))

    def test_fixed_window_and_every_single_bit_mutation(self):
        window = bytes.fromhex('085063080c0c2300750104b1')
        self.assertEqual(m.check_window(window), ((10, 8, 32), (23, 10, 0), (9, 10, 1)))
        for i in range(len(window)):
            for bit in range(8):
                changed = bytearray(window)
                changed[i] ^= 1 << bit
                with self.subTest(i=i, bit=bit), self.assertRaises(ValueError):
                    m.check_window(changed)
        for bad in (window[:-1], window + b'\0'):
            with self.assertRaises(ValueError):
                m.check_window(bad)

    def test_pinned_image(self):
        image = m.IMAGE.read_bytes()
        self.assertEqual(m.check_image(image), ((10, 8, 32), (23, 10, 0), (9, 10, 1)))
        changed = bytearray(image)
        changed[m.START - 0x40000] ^= 1
        with self.assertRaises(ValueError):
            m.check_image(changed)


if __name__ == '__main__':
    unittest.main()
