import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import verify


class EvidenceTests(unittest.TestCase):
    def test_cli_normal_and_optimized(self):
        script = Path(verify.__file__)
        with tempfile.TemporaryDirectory() as directory:
            altered = Path(directory) / 'altered.bin'
            data = bytearray(verify.DEFAULT.read_bytes())
            data[0] ^= 1
            altered.write_bytes(data)
            missing = Path(directory) / 'missing.bin'
            try:
                missing.read_bytes()
            except OSError as exc:
                missing_error = str(exc)
            for flags in ([], ['-O']):
                with self.subTest(flags=flags):
                    command = [sys.executable, *flags, str(script)]
                    result = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    for args, error in (([str(altered)], 'image SHA-256 mismatch'),
                                        ([str(missing)], missing_error),
                                        ([str(altered), str(missing)], 'usage: verify.py [image.bin]')):
                        with self.subTest(args=args):
                            result = subprocess.run(command + args, capture_output=True, text=True)
                            self.assertEqual(result.returncode, 1)
                            self.assertEqual(result.stdout, '')
                            self.assertEqual(result.stderr, f'FAIL: {error}\n')

    def test_branch_decode_and_negative_cases_without_image_hash(self):
        w = verify.WINDOW
        self.assertEqual(verify.decode_branch(w), (14, 0x18ee0))
        pos = verify.BRANCH - verify.START
        def flip(bit):
            changed = bytearray(w)
            changed[pos + bit // 8] ^= 1 << (bit % 8)
            return changed

        for bit in (0, 1, 13, 14, 15):
            with self.subTest(opcode_bit=bit):
                changed = flip(bit)
                with self.assertRaisesRegex(ValueError, '^not C\\.BNEZ$'):
                    verify.decode_branch(changed)
                with self.assertRaisesRegex(ValueError, '^not C\\.BNEZ$'):
                    verify.check_window(changed)
        for bit, register in ((7, 15), (8, 12), (9, 10)):
            with self.subTest(register_bit=bit):
                changed = flip(bit)
                self.assertEqual(verify.decode_branch(changed), (register, 0x18ee0))
                with self.assertRaisesRegex(ValueError, '^branch register/target mismatch$'):
                    verify.check_window(changed)
        for bit, target in ((2, 0x18ec0), (3, 0x18ee2), (4, 0x18edc),
                            (5, 0x18ea0), (6, 0x18e60), (10, 0x18ed8),
                            (11, 0x18ed0), (12, 0x18fe0)):
            with self.subTest(immediate_bit=bit):
                changed = flip(bit)
                self.assertEqual(verify.decode_branch(changed), (14, target))
                with self.assertRaisesRegex(ValueError, '^branch register/target mismatch$'):
                    verify.check_window(changed)
        with self.assertRaises(ValueError):
            verify.decode_branch(b'')
        changed = bytearray(w)
        changed[0] ^= 1
        with self.assertRaisesRegex(ValueError, 'window bytes'):
            verify.check_window(changed)

    def test_image_hash_independent_of_window(self):
        data = bytearray(verify.DEFAULT.read_bytes())
        data[0] ^= 1
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            verify.verify(data)
        with self.assertRaisesRegex(ValueError, 'length'):
            verify.verify(data[:-1])


if __name__ == '__main__':
    unittest.main()
