import unittest
import verify


class EvidenceTests(unittest.TestCase):
    def test_image(self):
        data = verify.IMAGE.read_bytes()
        verify.verify(data)
        for changed in (data[:-1], bytes([data[0] ^ 1]) + data[1:]):
            with self.assertRaises(ValueError):
                verify.verify(changed)

    def test_each_window_mutation_and_truncation(self):
        data = verify.IMAGE.read_bytes()
        for start, expected in verify.WINDOWS.items():
            offset = start - verify.BASE
            verify.check_window(data, start, expected)
            for i in range(len(expected)):
                with self.subTest(start=hex(start), byte=i):
                    changed = bytearray(data)
                    changed[offset + i] ^= 1
                    with self.assertRaises(ValueError):
                        verify.check_window(changed, start, expected)
            for length in range(len(expected)):
                with self.subTest(start=hex(start), length=length):
                    with self.assertRaises(ValueError):
                        verify.check_window(data[:offset + length], start, expected)

    def test_signed_calculations(self):
        for bits in (12, 20, 21):
            for raw, expected in ((0, 0), (1, 1), ((1 << (bits - 1)) - 1, (1 << (bits - 1)) - 1),
                                  (1 << (bits - 1), -(1 << (bits - 1))), ((1 << bits) - 1, -1)):
                self.assertEqual(verify.signed(raw, bits), expected)
            for raw in (-1, 1 << bits):
                with self.assertRaises(ValueError):
                    verify.signed(raw, bits)
        self.assertEqual(verify.store_address(0xb0b0, verify.WINDOWS[0xb0b0][:8]), 0x2000beeb)
        for pc, rd, delta in verify.EDGES:
            start = next(s for s, b in verify.WINDOWS.items() if s <= pc and pc + 4 <= s + len(b))
            raw = verify.WINDOWS[start][pc-start:pc-start+4]
            self.assertEqual(verify.decode_jal(raw), (rd, delta))
            self.assertEqual(pc + delta, 0xb0b0)
        for raw in (b'', b'\0' * 4):
            with self.assertRaises(ValueError):
                verify.decode_jal(raw)


if __name__ == '__main__':
    unittest.main()
