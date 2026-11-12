import unittest
from unittest.mock import patch
import verify as v

class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = v.IMAGE.read_bytes()

    def test_original(self):
        self.assertTrue(v.verify(self.image))

    def test_every_window_byte_mutated(self):
        for pc, window in v.WINDOWS.items():
            for n in range(len(window)):
                image = bytearray(self.image)
                image[pc - v.BASE + n] ^= 1
                with self.subTest(pc=hex(pc), offset=n):
                    with self.assertRaises(v.EvidenceError):
                        v.verify_windows(image)
                    with self.assertRaises(v.EvidenceError):
                        v.verify(image)

    def test_each_window_truncation(self):
        for pc, window in v.WINDOWS.items():
            for n in range(len(window)):
                with self.subTest(pc=hex(pc), length=n):
                    with self.assertRaises(v.EvidenceError):
                        v.verify_windows(self.image[:pc - v.BASE + n])
                    with self.assertRaises(v.EvidenceError):
                        v.verify(self.image[:pc - v.BASE + n])

    def test_outside_window_and_length(self):
        image = bytearray(self.image)
        image[0] ^= 1
        with self.assertRaises(v.EvidenceError):
            v.verify(image)
        with self.assertRaises(v.EvidenceError):
            v.verify(self.image + b'\0')

    def test_call_argument_instruction_bits(self):
        self.assertEqual(v.call_argument(self.image), 0x08077900)
        # Mutate each opcode, ADDI funct3, each register field, and c.mv.
        for pc, bit in [(0x12e70, 0), (0x12e70, 7),
                        (0x12e76, 0), (0x12e76, 12),
                        (0x12e76, 7), (0x12e76, 15), (0x12e74, 0)]:
            image = bytearray(self.image)
            image[pc - v.BASE + bit // 8] ^= 1 << (bit % 8)
            with self.subTest(pc=hex(pc), bit=bit):
                with self.assertRaises(v.EvidenceError):
                    v.call_argument(image)
        # Negative upper and ADDI immediate sign bits are decoded, not assumed.
        for pc, bit, expected in [(0x12e70, 31, 0x88077900),
                                  (0x12e76, 31, 0x08078100)]:
            image = bytearray(self.image)
            image[pc - v.BASE + bit // 8] ^= 1 << (bit % 8)
            with self.subTest(pc=hex(pc), bit=bit):
                self.assertEqual(v.call_argument(image), expected)
                # Exercise verify's arithmetic check independently of hash/windows.
                with patch.object(v, 'SHA256', v.hashlib.sha256(image).hexdigest()), \
                     patch.object(v, 'verify_windows'):
                    with self.assertRaisesRegex(v.EvidenceError, 'call argument'):
                        v.verify(image)

    def test_address_and_decoder_negatives(self):
        self.assertEqual(v.address(0, -1), 0xffffffff)
        self.assertEqual(v.address(0xffffffff, 1), 0)
        for base, offset in [(-1, 0), (0x100000000, 0), (0, 0x80000000), (0, -0x80000001)]:
            with self.assertRaises(v.EvidenceError):
                v.address(base, offset)
        with self.assertRaises(v.EvidenceError):
            v.word(self.image, v.BASE - 1)
        with self.assertRaises(v.EvidenceError):
            v.word(self.image, v.BASE + len(self.image) - 3)
        with self.assertRaises(v.EvidenceError):
            v.pair(self.image, 0x12e66)
        with self.assertRaises(v.EvidenceError):
            v.jal_target(self.image, 0x12ee2, 1)
        self.assertNotEqual(v.address(0x12e90, 0x1fff9000 + 1538), 0x2000c494)

if __name__ == '__main__':
    unittest.main()
