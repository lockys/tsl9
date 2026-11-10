import unittest
import verify as v


class Replay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = v.IMAGE.read_bytes()

    def test_pin_and_local_witnesses(self):
        v.verify(self.data)
        for pc in (0xcedc, 0xcef6, 0xcf0a, 0xcf20, 0xcf3e, 0xcf44, 0xcf4e, 0xcf5a, 0xcf78, 0xcf7a, 0xd06e):
            data = bytearray(self.data)
            data[pc-v.BASE] ^= 1
            with self.subTest(pc=hex(pc)), self.assertRaises(ValueError):
                v.verify(data, pin=False)
        data = bytearray(self.data)
        data[0] ^= 1
        with self.assertRaises(ValueError):
            v.verify(data)

    def test_boundaries_and_gates(self):
        self.assertIsNone(v.read_address(0, 255, 183, 0))
        self.assertEqual(v.read_address(1, 1, 183, 0), 0x1a079)
        for phase in (0, 255):
            for mode, nibble, address in ((182, 7, 0x1abdf), (182, 8, 0x1abe0),
                                          (183, 0, 0x1abe8), (184, 7, 0x1abff),
                                          (184, 8, 0x1ac00)):
                self.assertEqual(v.read_address(1, phase, mode, (nibble-1) & 255), address)
        for mode in (0, 1, 2, 3, 4, 5):
            for record in range(256):
                self.assertFalse(0x1abe0 <= v.read_address(1, 255, mode, record) < 0x1ac00)
        with self.assertRaises(ValueError):
            v.read_address(1, 256, 0, 0)

    def test_exhaustive_pairs(self):
        hits = {(mode, n) for mode in range(256) for n in range(16)
                if 0x1abe0 <= v.read_address(1, 0, mode, (n-1) & 255) < 0x1ac00}
        self.assertEqual(hits, {(182, n) for n in range(8, 16)} |
                         {(183, n) for n in range(16)} | {(184, n) for n in range(8)})


if __name__ == '__main__':
    unittest.main()
