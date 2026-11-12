import tempfile
import unittest
from pathlib import Path
import verify


class VerificationTests(unittest.TestCase):
    def test_source_identities_and_mutations(self):
        verify.check_sources()
        with tempfile.TemporaryDirectory(dir=verify.SOURCE_DIR) as tmp:
            directory = Path(tmp)
            originals = {name: (verify.SOURCE_DIR / name).read_bytes()
                         for name in verify.SOURCE_SHA256}
            for name, data in originals.items():
                (directory / name).write_bytes(data)
            verify.check_sources(directory)
            for name, data in originals.items():
                for bad in (data[:-1], data + b'\0', bytes([data[0] ^ 1]) + data[1:]):
                    with self.subTest(name=name, mutation=bad[:1], size=len(bad)):
                        (directory / name).write_bytes(bad)
                        with self.assertRaisesRegex(ValueError, name.replace('.', r'\.')):
                            verify.check_sources(directory)
                (directory / name).write_bytes(data)
            verify.check_sources(directory)
            for name in originals:
                (directory / name).unlink()
                with self.subTest(missing=name), self.assertRaises(FileNotFoundError):
                    verify.check_sources(directory)
                (directory / name).write_bytes(originals[name])

    def test_identity_and_negative_cases(self):
        data = verify.IMAGE.read_bytes()
        verify.check_image(data)
        for bad in (data[:-1], data + b'\0', bytes([data[0] ^ 1]) + data[1:]):
            with self.assertRaises(ValueError):
                verify.check_image(bad)
        for i in range(len(verify.WINDOW)):
            for bit in range(8):
                bad = bytearray(data)
                bad[verify.START + i] ^= 1 << bit
                with self.assertRaises(ValueError):
                    verify.check_window(bad)
                with self.assertRaises(ValueError):
                    verify.check_image(bad)
        with self.assertRaises(ValueError):
            verify.check_window(data[:verify.START + len(verify.WINDOW) - 1])
        bad = bytearray(data)
        bad[verify.START - 1] ^= 1
        verify.check_window(bad)
        with self.assertRaises(ValueError):
            verify.check_image(bad)


if __name__ == '__main__':
    unittest.main()
