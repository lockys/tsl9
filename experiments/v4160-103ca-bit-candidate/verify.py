"""Offline fixture identity and abstract event tests, not C or ISA execution."""
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
CANDIDATE = Path(__file__).with_name('candidate.c')
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
IMAGE_BLOB = 'e6cd0db8bd7d460a16967a5df9eadb42b04fa00d'
CANDIDATE_BLOB = 'b5924e60c20d64bd36a4198616db80de8c60709a'
START = 0x103ca - 0x8000
WINDOW = bytes.fromhex('83 c7 74 00 03 c7 21 05 85 83 85 8b 63 01 f7 02 22 44 b2 40 92 44 23 89 f1 04 41 01 6f 30 90 06')


def blob_id(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def check_window(data):
    if data[START:START + len(WINDOW)] != WINDOW:
        raise ValueError('instruction window mismatch')


def check_image(data):
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA256 or blob_id(data) != IMAGE_BLOB:
        raise ValueError('firmware identity mismatch')
    check_window(data)


def check_candidate(data):
    if blob_id(data) != CANDIDATE_BLOB:
        raise ValueError('candidate blob mismatch')


def model(p7, old):
    value = (p7 >> 1) & 1
    return value, old != value


class Verify(unittest.TestCase):
    def test_fixtures_and_mutations(self):
        data = IMAGE.read_bytes()
        candidate = CANDIDATE.read_bytes()
        check_image(data)
        check_candidate(candidate)
        for old, new in ((b'>> 1', b'>> 2'), (b'!=', b'=='), (b'& 1u', b'& 0u')):
            self.assertEqual(candidate.count(old), 1)
            with self.assertRaises(ValueError):
                check_candidate(candidate.replace(old, new))
        with self.assertRaises(ValueError):
            check_candidate(candidate + b'\0')
        for bad in (data[:-1], data + b'\0', bytes([data[0] ^ 1]) + data[1:]):
            with self.assertRaises(ValueError):
                check_image(bad)
        for i in range(len(WINDOW)):
            for bit in range(8):
                bad = bytearray(data)
                bad[START + i] ^= 1 << bit
                with self.assertRaises(ValueError):
                    check_window(bad)
        with self.assertRaises(ValueError):
            check_window(data[:START + len(WINDOW) - 1])
        bad = bytearray(data)
        bad[START - 1] ^= 1
        check_window(bad)
        with self.assertRaises(ValueError):
            check_image(bad)

    def test_all_second_reads_and_old_bytes(self):
        for p7 in range(256):
            for old in range(256):
                expected_value = (p7 // 2) % 2
                self.assertEqual(model(p7, old), (expected_value, old != expected_value))

    def test_previous_read_is_not_reused(self):
        # A preceding load can have seen 0 while the 0x103ca load sees 2.
        earlier_p7, second_p7 = 0, 2
        self.assertNotEqual(earlier_p7, second_p7)
        self.assertEqual(model(second_p7, 0), (1, True))
        self.assertEqual(model(second_p7, 1), (1, False))
        self.assertEqual(model(second_p7, 0x81), (1, True))


if __name__ == '__main__':
    unittest.main()
