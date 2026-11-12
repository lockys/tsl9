import hashlib
import unittest
import validator as v


def flip(data, offset, mask):
    result = bytearray(data)
    result[offset] ^= mask
    return bytes(result)


class ValidatorTests(unittest.TestCase):
    def test_images(self):
        for kind, path, digest in v.IMAGES:
            data = (v.ROOT / path).read_bytes()
            v.check_image(data, kind, digest)
            for bad in (data[:-1], flip(data, 0, 1)):
                with self.assertRaises(ValueError):
                    v.check_image(bad, kind, digest)
            with self.assertRaises(ValueError):
                v.check_image(data[:-1], kind, hashlib.sha256(data[:-1]).hexdigest())

    def test_fields_directly(self):
        for kind in v.WINDOW:
            window = v.WINDOW[kind]
            v.check_window(v.PREFIX, window, kind)
            # Opcode, funct3, rs1, rs2 and each B-immediate field.
            for start in (0, 8):
                expected = ((1, 14, 10, 32, 0x8a96) if start == 0 else
                            (0, 14, 15, 24, 0x8a96) if kind == 'reference' else
                            (0, 15, 10, 24, 0x8a96))
                raw = window[start:start+4]
                pc = 0x8a76 + start
                for bit in (0, 12, 15, 20, 7, 8, 25, 31):
                    with self.subTest(kind=kind, start=start, bit=bit):
                        with self.assertRaises(ValueError):
                            v.check_branch(flip(raw, bit // 8, 1 << (bit % 8)), pc, expected)
            for offset in (0, 4, 6, 8):
                with self.assertRaises(ValueError):
                    v.check_window(v.PREFIX, flip(window, offset, 1), kind)
            with self.assertRaises(ValueError):
                v.check_window(flip(v.PREFIX, 0, 1), window, kind)
            with self.assertRaises(ValueError):
                v.check_window(flip(v.PREFIX, 4, 1), window, kind)
            with self.assertRaises(ValueError):
                v.check_window(v.PREFIX, window[:-1], kind)

    def test_domain(self):
        for value in (0, 1, 0xfffe, 0xffff, 0x10000, 0x80000000, 0xffffffff):
            self.assertTrue(v.check_domain(value, value, True))
        for a4, a0, edge in ((0xfffe, 0, True), (0, 0, False),
                             (-1, -1, True), (0x100000000, 0x100000000, True),
                             (True, 1, True), (0, 0, 1), (None, 0, True)):
            with self.assertRaises(ValueError):
                v.check_domain(a4, a0, edge)


if __name__ == '__main__':
    unittest.main()
