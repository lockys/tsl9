import subprocess
import sys
import unittest

import verify


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = verify.IMAGE.read_bytes()

    def test_original(self):
        verify.verify(self.image)

    def test_every_window_bit(self):
        for i in range(len(verify.WINDOW)):
            for bit in range(8):
                changed = bytearray(self.image)
                changed[verify.START - verify.BASE + i] ^= 1 << bit
                with self.subTest(byte=i, bit=bit), self.assertRaises(ValueError):
                    verify.check_window(changed)

    def test_truncation_and_external_bit(self):
        for length in (0, verify.START - verify.BASE, verify.START - verify.BASE + len(verify.WINDOW) - 1, len(self.image) - 1):
            with self.subTest(length=length), self.assertRaises(ValueError):
                verify.verify(self.image[:length])
        changed = bytearray(self.image)
        changed[0] ^= 1
        verify.check_window(changed)
        with self.assertRaises(ValueError):
            verify.verify(changed)

    def test_decoder(self):
        for pc, target in verify.CALLS.items():
            off = pc - verify.BASE
            self.assertEqual(verify.decode_jal(pc, self.image[off:off + 4]), target)
        self.assertEqual(verify.decode_jal(0x1000, bytes.fromhex('eff0dfff')), 0xffc)
        for raw in (b'', b'\x6f\x00\x00', b'\x6f\x00\x00\x00'):
            with self.assertRaises(ValueError):
                verify.decode_jal(0, raw)

    def test_optimized_cli(self):
        result = subprocess.run([sys.executable, '-B', '-O', str(verify.__file__)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
