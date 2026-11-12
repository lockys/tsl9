"""Static byte pins only; never compiles or runs C."""
import hashlib
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
PINS = {
    HERE / "../v4160-18ec4-candidate/candidate.c": "e1d2826c9bed81029380766c46a8a774e09d342b615593f40dba8519db25d99d",
    HERE / "harness.c": "93c0a2e10e3fb2b70071a590736e3f18f5c17f9ad860fe5ee54261bf4e2212c9",
}


def matches(data, expected):
    return hashlib.sha256(data).hexdigest() == expected


def check_path(path, expected):
    try:
        return matches(path.read_bytes(), expected)
    except OSError:
        return False


class PinTests(unittest.TestCase):
    def test_pins(self):
        for path, digest in PINS.items():
            with self.subTest(path=path):
                self.assertTrue(check_path(path, digest))

    def test_mutations_rejected(self):
        for path, digest in PINS.items():
            with self.subTest(path=path):
                data = path.read_bytes()
                self.assertTrue(data)
                changed = bytes([data[0] ^ 1]) + data[1:]
                self.assertFalse(matches(changed, digest))

    def test_missing_path_rejected(self):
        self.assertFalse(check_path(HERE / "missing-directory" / "missing.c", "0" * 64))


if __name__ == "__main__":
    unittest.main()
