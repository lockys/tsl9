import unittest
from unittest.mock import patch

import verify as v


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = v.IMAGE.read_bytes()

    def test_original_and_window_lengths(self):
        self.assertEqual({pc: len(data) for pc, data in v.WINDOWS.items()},
                         {0x155d0: 128, 0x16266: 48, 0xb0b0: 10, 0x1a9f4: 12})
        v.verify(self.image)
        v.check_windows(self.image)
        v.check_math(self.image)
        self.assertEqual(v.table_base(self.image), 0x1a6f4)

    def test_each_window_byte_and_bit_directly(self):
        for pc, expected in v.WINDOWS.items():
            for i in range(len(expected)):
                for bit in range(8):
                    altered = bytearray(self.image)
                    altered[pc - v.BASE + i] ^= 1 << bit
                    with self.subTest(pc=pc, byte=i, bit=bit):
                        with self.assertRaisesRegex(ValueError, 'window mismatch'):
                            v.check_window(altered, pc, expected)
                        with self.assertRaisesRegex(ValueError, 'window mismatch'):
                            v.check_windows(altered)

    def test_hash_bypassed_verify_reaches_each_window_guard(self):
        # 保持長度並強制回報原 SHA，驗證 verify 的局部 guard 本身生效。
        for pc in v.WINDOWS:
            altered = bytearray(self.image)
            altered[pc - v.BASE] ^= 1
            with self.subTest(pc=pc), patch.object(v, 'sha256') as digest:
                digest.return_value.hexdigest.return_value = v.SHA
                with self.assertRaisesRegex(ValueError, f'window mismatch: {pc:#x}'):
                    v.verify(altered)
                digest.assert_called_once()

    def test_truncation_and_addresses(self):
        for pc, expected in v.WINDOWS.items():
            off = pc - v.BASE
            for i in range(len(expected)):
                with self.subTest(pc=pc, length=i), self.assertRaises(ValueError):
                    v.check_window(self.image[:off + i], pc, expected)
            for delta in (-2, -1, 1, 2):
                with self.subTest(pc=pc, delta=delta), self.assertRaises(ValueError):
                    v.check_window(self.image, pc + delta, expected)
        for pc, size in ((v.BASE - 1, 1), (v.BASE, -1),
                         (v.BASE + len(self.image), 1)):
            with self.subTest(pc=pc, size=size), self.assertRaises(ValueError):
                v.read_at(self.image, pc, size)
        for pc in (0x1563a, 0x1563b, 0x1563d, 0x1563e, 0x15640):
            with self.subTest(pc=pc), self.assertRaises(ValueError):
                v.check_math(self.image, pc)

    def test_instruction_fields_and_table_words(self):
        # 每個 AUIPC/ADDI opcode、rd、rs1、funct3 和立即數位元。
        for pc in (0x1563c, 0x15640):
            for bit in range(32):
                altered = bytearray(self.image)
                altered[pc - v.BASE + bit // 8] ^= 1 << (bit % 8)
                with self.subTest(pc=pc, bit=bit), self.assertRaises(ValueError):
                    v.check_math(altered)
        for pc in (0x1a9f4, 0x1a9f8, 0x1a9fc):
            for bit in range(32):
                altered = bytearray(self.image)
                altered[pc - v.BASE + bit // 8] ^= 1 << (bit % 8)
                with self.subTest(pc=pc, bit=bit), self.assertRaises(ValueError):
                    v.check_math(altered)
        with self.assertRaises(ValueError):
            v.check_math(self.image[:0x1a9fc - v.BASE + 3])
        self.assertEqual(v.signed(0x800, 12), -2048)
        self.assertEqual(v.signed(0x7ff, 12), 2047)
        self.assertEqual(v.signed(0x80000, 20), -524288)
        self.assertEqual(v.signed(0x7ffff, 20), 524287)

    def test_identity(self):
        altered = bytearray(self.image)
        altered[0] ^= 1
        for candidate in (altered, self.image[:-1], self.image + b'\x00'):
            with self.subTest(length=len(candidate)), self.assertRaisesRegex(ValueError, 'length or SHA'):
                v.verify(candidate)


if __name__ == '__main__':
    unittest.main()
