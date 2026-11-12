import unittest
import verify


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = verify.IMAGE.read_bytes()

    def test_original(self):
        verify.verify(self.image)

    def test_every_window_byte_mutated(self):
        for pc, window in verify.WINDOWS.items():
            for i in range(len(window)):
                data = bytearray(self.image)
                data[pc - verify.BASE + i] ^= 1
                with self.subTest(pc=hex(pc), byte=i):
                    with self.assertRaises(verify.VerificationError):
                        verify.check_windows(data)
                    with self.assertRaises(verify.VerificationError):
                        verify.verify(data)

    def test_truncation_and_outside_window(self):
        for pc, window in verify.WINDOWS.items():
            for end in range(pc - verify.BASE, pc - verify.BASE + len(window)):
                with self.assertRaises(verify.VerificationError):
                    verify.check_windows(self.image[:end])
                with self.assertRaises(verify.VerificationError):
                    verify.verify(self.image[:end])
        with self.assertRaises(verify.VerificationError):
            verify.verify(self.image[:-1])
        with self.assertRaises(verify.VerificationError):
            verify.verify(self.image + b'\0')
        data = bytearray(self.image)
        data[-1] ^= 1
        verify.check_windows(data)
        with self.assertRaises(verify.VerificationError):
            verify.verify(data)

    def test_independent_address_arithmetic(self):
        self.assertEqual(verify.address(self.image, 0xae9e), (0xae9e + 0x20001000 + 77) & 0xffffffff)
        self.assertEqual(verify.address(self.image, 0xaeb4, True), (0xaeb4 + 0x20001000 + 55) & 0xffffffff)
        self.assertEqual(verify.address(self.image, 0xae9e), 0x2000beeb)
        self.assertEqual(verify.address(self.image, 0xaeb4, True), 0x2000beeb)
        # Relocating the same bytes changes each result with its own AUIPC PC.
        data = bytearray(self.image)
        data[0x9000-verify.BASE:0x9008-verify.BASE] = self.image[0xae9e-verify.BASE:0xaea6-verify.BASE]
        self.assertEqual(verify.address(data, 0x9000), 0x2000a04d)
        with self.assertRaises(verify.VerificationError):
            verify.address(self.image[:0xaeba-verify.BASE], 0xaeb4, True)
        with self.assertRaises(verify.VerificationError):
            verify.address(self.image, 0xae9e, True)

if __name__ == '__main__':
    unittest.main()
