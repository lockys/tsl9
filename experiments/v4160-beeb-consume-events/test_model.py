import hashlib
from pathlib import Path
import unittest

from model import consume, SOURCE

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
# Independent literal fixed from the image, inclusive through the lbu at 0xaec8.
WINDOW = bytes.fromhex('9717002083c7d70499cb19478d07238ee10aa38ef10a97170020a38b070283c7c10bc1c7fd17238ef10a83c7d10b')


def check_window(image):
    if image[0xae9e - 0x8000:0xaecc - 0x8000] != WINDOW:
        raise ValueError('instruction window')


def check_image(image):
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667':
        raise ValueError('image identity')
    check_window(image)


class Tests(unittest.TestCase):
    def test_image_and_negatives(self):
        image = IMAGE.read_bytes()
        check_image(image)
        for i in range(len(WINDOW)):
            broken = bytearray(image)
            broken[0xae9e - 0x8000 + i] ^= 1
            with self.assertRaises(ValueError):
                check_window(broken)
            with self.assertRaises(ValueError):
                check_image(broken)
        for i in range(len(WINDOW)):
            with self.assertRaises(ValueError):
                check_window(image[:0xae9e - 0x8000 + i])
        with self.assertRaises(ValueError):
            check_image(image[:-1])
        self.assertNotEqual(WINDOW, bytes(len(WINDOW)))

    def test_zero_split_and_counts(self):
        gp = 0x1000
        for n in (0, 1, 255):
            with self.subTest(n=n):
                mem = {SOURCE: 0, gp + 188: n, gp + 189: 0xab}
                out, trace = consume(mem, gp)
                expected = [(0xaea2, 'read', SOURCE, 0), (0xaebc, 'read', gp + 188, n)]
                if n:
                    expected += [(0xaec4, 'write', gp + 188, n - 1), (0xaec8, 'read', gp + 189, 0xab)]
                self.assertEqual(trace, expected)
                self.assertEqual(out, '0xaecc' if n else '0xaf48')
                self.assertEqual(mem[gp + 188], n - 1 if n else 0)

    def test_nonzero_and_wrap_byte(self):
        gp = 0x1000
        for x in (1, 253, 254, 255):
            for n in (0, 1, 255):
                with self.subTest(x=x, n=n):
                    a, b = gp + 188, gp + 189
                    mem = {SOURCE: x, a: n, b: 42}
                    out, trace = consume(mem, gp)
                    self.assertEqual(out, '0xaecc')
                    self.assertEqual(trace, [(0xaea2, 'read', SOURCE, x), (0xaeac, 'write', a, 6), (0xaeb0, 'write', b, (x+3)&255), (0xaeb8, 'write', SOURCE, 0), (0xaebc, 'read', a, 6), (0xaec4, 'write', a, 5), (0xaec8, 'read', b, (x+3)&255)])
                    self.assertEqual(mem, {SOURCE: 0, a: 5, b: (x+3)&255})

    def test_aliases(self):
        # gp+188 aliases source: clearing source makes the later count zero.
        gp = SOURCE - 188
        mem = {SOURCE: 1, SOURCE + 1: 88}
        out, trace = consume(mem, gp)
        self.assertEqual(out, '0xaf48')
        self.assertEqual(trace, [(0xaea2, 'read', SOURCE, 1), (0xaeac, 'write', SOURCE, 6), (0xaeb0, 'write', SOURCE+1, 4), (0xaeb8, 'write', SOURCE, 0), (0xaebc, 'read', SOURCE, 0)])
        # gp+189 aliases source: the later read observes the clear.
        gp = SOURCE - 189
        mem = {SOURCE: 255, SOURCE - 1: 0}
        out, trace = consume(mem, gp)
        self.assertEqual(out, '0xaecc')
        self.assertEqual(trace, [(0xaea2, 'read', SOURCE, 255), (0xaeac, 'write', SOURCE-1, 6), (0xaeb0, 'write', SOURCE, 2), (0xaeb8, 'write', SOURCE, 0), (0xaebc, 'read', SOURCE-1, 6), (0xaec4, 'write', SOURCE-1, 5), (0xaec8, 'read', SOURCE, 0)])

    def test_zero_aliases_and_cross_boundary(self):
        mem = {SOURCE: 0, SOURCE + 1: 88}
        self.assertEqual(consume(mem, SOURCE - 188), ('0xaf48', [
            (0xaea2, 'read', SOURCE, 0), (0xaebc, 'read', SOURCE, 0)]))
        mem = {SOURCE: 0, SOURCE - 1: 1}
        self.assertEqual(consume(mem, SOURCE - 189), ('0xaecc', [
            (0xaea2, 'read', SOURCE, 0), (0xaebc, 'read', SOURCE - 1, 1),
            (0xaec4, 'write', SOURCE - 1, 0), (0xaec8, 'read', SOURCE, 0)]))
        mem = {SOURCE: 0, 0xffffffff: 1, 0: 9}
        self.assertEqual(consume(mem, 0xffffff43), ('0xaecc', [
            (0xaea2, 'read', SOURCE, 0), (0xaebc, 'read', 0xffffffff, 1),
            (0xaec4, 'write', 0xffffffff, 0), (0xaec8, 'read', 0, 9)]))

    def test_gp_wrap_and_invalid(self):
        mem = {SOURCE: 0, 187: 1, 188: 9}
        out, trace = consume(mem, 0xffffffff)
        self.assertEqual((out, trace), ('0xaecc', [(0xaea2, 'read', SOURCE, 0), (0xaebc, 'read', 187, 1), (0xaec4, 'write', 187, 0), (0xaec8, 'read', 188, 9)]))
        for gp in (-1, 0x100000000):
            with self.assertRaises(ValueError):
                consume({}, gp)
        with self.assertRaises(KeyError):
            consume({}, 0)
        with self.assertRaises(ValueError):
            consume({SOURCE: 256}, 0)


if __name__ == '__main__':
    unittest.main()
