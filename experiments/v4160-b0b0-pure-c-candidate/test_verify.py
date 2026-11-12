import unittest

import verify as v


class DataChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = v.IMAGE.read_bytes()
        cls.candidate = (v.HERE / 'leaf.c').read_bytes()

    def test_valid(self):
        v.verify(self.image, self.candidate)

    def test_image_identity_rejected(self):
        for image in (self.image[:-1], self.image + b'\0', b'',
                      bytes([self.image[0] ^ 1]) + self.image[1:]):
            with self.subTest(length=len(image)), self.assertRaises(ValueError):
                v.verify(image, self.candidate)

    def test_candidate_identity_rejected(self):
        for candidate in (b'', self.candidate[:-1], self.candidate + b' ',
                          self.candidate.replace(b'(uint8_t)value', b'(uint8_t)(value + 1)')):
            with self.subTest(candidate=candidate[-25:]), self.assertRaises(ValueError):
                v.verify(self.image, candidate)

    def test_window_independently_rejected(self):
        for i in range(len(v.WINDOW)):
            changed = bytearray(self.image)
            changed[v.OFFSET + i] ^= 1
            with self.subTest(byte=i), self.assertRaises(ValueError):
                v.check_window(changed)
        for n in range(len(v.WINDOW)):
            with self.subTest(length=n), self.assertRaises(ValueError):
                v.check_window(self.image[:v.OFFSET + n])


if __name__ == '__main__':
    unittest.main()
