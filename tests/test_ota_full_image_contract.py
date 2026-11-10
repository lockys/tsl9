"""Offline fixed-image comparison and synthetic APK-side page/envelope checks.

This does not execute the APK, BOOT or firmware and never contacts a device.
"""
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
CANDIDATE = ROOT / 'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin'
SHA_OFFICIAL = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SHA_CANDIDATE = '28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89'
SIZE = 76800


def pinned_image(path, digest):
    data = path.read_bytes()
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('image size or pinned digest mismatch')
    if data[0] != 0x6f:
        raise ValueError('first byte mismatch')
    return data


def pages(image):
    if len(image) != SIZE:
        raise ValueError('image size')
    return [i.to_bytes(2, 'big') + image[i * 1024:(i + 1) * 1024] for i in range(75)]


def check_pages(items, count, byte_count, checksum):
    # Fixed 1026-byte page profile for this comparison, not an APK-wide requirement.
    if len(items) != count or sum(map(len, items)) != byte_count:
        raise ValueError('page count or bytes')
    if any(len(p) != 1026 or int.from_bytes(p[:2], 'big') != i for i, p in enumerate(items)):
        raise ValueError('page size or index')
    if sum(map(sum, items)) % 65536 != checksum:
        raise ValueError('page checksum')


def frame(command, payload):
    length = len(payload).to_bytes(2, 'big')
    body = bytes([command]) + length + payload
    return b'\x55\x7f' + body + bytes([sum(body) & 255])


def check_frame(raw):
    if len(raw) < 6 or raw[:2] != b'\x55\x7f':
        raise ValueError('header')
    size = int.from_bytes(raw[3:5], 'big')
    if len(raw) != size + 6 or sum(raw[2:-1]) & 255 != raw[-1]:
        raise ValueError('length or checksum')
    return raw[2], raw[5:-1]


class FullImageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.official = pinned_image(OFFICIAL, SHA_OFFICIAL)
        cls.candidate = pinned_image(CANDIDATE, SHA_CANDIDATE)

    def test_full_image_difference_and_pages(self):
        differences = [i for i, (a, b) in enumerate(zip(self.official, self.candidate)) if a != b]
        expected = [(0x8a7f, 0x8a81), (0x8ad3, 0x8ad5), (0x8b11, 0x8b12),
                    (0x8b13, 0x8b5c), (0x8b5d, 0x8b6c)]
        self.assertEqual(differences, [addr - 0x8000 for lo, hi in expected for addr in range(lo, hi)])
        for image, checksum in ((self.official, 31872), (self.candidate, 32058)):
            chunks = pages(image)
            check_pages(chunks, 75, 76950, checksum)
            self.assertEqual(b''.join(p[2:] for p in chunks), image)
            for page in chunks:
                self.assertEqual(check_frame(frame(87, page)), (87, page))
        self.assertEqual([i for i, (a, b) in enumerate(zip(pages(self.official), pages(self.candidate))) if a != b], [2])

    def test_negative_synthetic_mutations(self):
        chunks = pages(self.candidate)
        checksum = 32058
        for changed in (chunks[:-1], chunks + [chunks[-1]], [chunks[1], chunks[0]] + chunks[2:],
                        [chunks[0][:-1]] + chunks[1:]):
            with self.assertRaises(ValueError):
                check_pages(changed, 75, 76950, checksum)
        changed = chunks.copy()
        page = bytearray(changed[0]); page[2] ^= 1; changed[0] = bytes(page)
        with self.assertRaises(ValueError):
            check_pages(changed, 75, 76950, checksum)
        wire = frame(87, chunks[0])
        for bad in (wire[:-1], b'\x54' + wire[1:], wire[:-1] + bytes([wire[-1] ^ 1])):
            with self.assertRaises(ValueError):
                check_frame(bad)

    def test_pins_reject_modified_image(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'image.bin'
            for image in (self.candidate[:-1], bytes([self.candidate[0] ^ 1]) + self.candidate[1:],
                          self.candidate[:-1] + bytes([self.candidate[-1] ^ 1])):
                path.write_bytes(image)
                with self.assertRaises(ValueError):
                    pinned_image(path, SHA_CANDIDATE)

    def test_additive_checksum_is_not_integrity(self):
        chunks = pages(self.candidate)
        changed = chunks.copy()
        page = bytearray(changed[0])
        # Two distinct byte positions, preserving the sum without wraparound.
        up = next(i for i in range(2, len(page)) if page[i] < 255)
        down = next(i for i in range(2, len(page)) if i != up and page[i] > 0)
        page[up] += 1; page[down] -= 1; changed[0] = bytes(page)
        check_pages(changed, 75, 76950, 32058)
        self.assertNotEqual(changed, chunks)


if __name__ == '__main__':
    unittest.main()
