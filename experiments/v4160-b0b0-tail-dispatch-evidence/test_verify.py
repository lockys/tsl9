import unittest
import verify as v


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = v.IMAGE.read_bytes()

    def test_original(self):
        v.verify(self.image)
        v.check_windows(self.image)
        v.check_math(self.image)

    def test_each_window_byte_and_truncation(self):
        for pc, expected in v.WINDOWS.items():
            off = pc - v.BASE
            for i in range(len(expected)):
                altered = bytearray(self.image)
                altered[off + i] ^= 1
                with self.subTest(pc=pc, byte=i), self.assertRaises(ValueError):
                    v.check_windows(altered)
            for i in range(len(expected)):
                with self.subTest(pc=pc, truncation=i), self.assertRaises(ValueError):
                    v.check_windows(self.image[:off + i])

    def test_identity(self):
        altered = bytearray(self.image)
        altered[0] ^= 1
        with self.assertRaises(ValueError):
            v.verify(altered)
        with self.assertRaises(ValueError):
            v.verify(self.image[:-1])

    def test_math_rejects_bad_base_and_table(self):
        for pc in (0x1563c, 0x15640, 0x1a9f4, 0x1a9f8, 0x1a9fc):
            altered = bytearray(self.image)
            altered[pc - v.BASE] ^= 4
            with self.subTest(pc=pc), self.assertRaises(ValueError):
                v.check_math(altered)
        with self.assertRaises(ValueError):
            v.check_math(self.image[:0x1a9fc - v.BASE + 3])


if __name__ == '__main__':
    unittest.main()
