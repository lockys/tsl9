"""Offline numeric W-path checks; this is not an instruction emulator or Flash driver."""
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
BOOT = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
SHA = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
WINDOWS = {
    (0x2202, 0x2298): '8dd69cae662926db78eb5fc62593dc1e055112a1ad17352e744985be55256c0d',
    (0x20e6, 0x2126): '1e6b681c7656f8ba30dfd5e3ed764964362645ce0edc4c2b9f002eb2c1d2561c',
    (0x3016, 0x3044): '40e81eda78577543dd451a59487376d58352cb623c796194e0fcc9c12b23995d',
    (0x3044, 0x30a8): '8cd6ddd7edd2d5a0adb776d396c8cb499d64ce974f38df7e651f9af720114dd8',
}
MASK = 0xffffffff


def digest(b):
    return hashlib.sha256(b).hexdigest()


def check_windows(raw):
    return all(digest(raw[a-0x1000:b-0x1000]) == expected
               for (a, b), expected in WINDOWS.items())


def trace(high, low, payload, length=1026, active=True):
    """Conditional numeric requests, assuming successful loads and normal returns."""
    if not 0 <= high <= 255 or not 0 <= low <= 255 or not 0 <= payload <= MASK:
        raise ValueError('byte/address outside input domain')
    if not active or length != 1026:
        return None
    # 2210 loads low first, 2214 high second; the instructions swap back.
    page = (high << 8) | low
    dest = ((0x20020 + page) << 10) & MASK
    if ((dest + 0xf7ff8000) & MASK) > 0x17f00:
        return None
    source = (payload + 2) & MASK
    aligned = source & ~3
    calls = [((dest + i) & MASK, (aligned + i) & MASK) for i in range(0, 1024, 256)]
    return page, source, aligned, calls


class RangeChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = BOOT.read_bytes()

    def test_exact_source(self):
        self.assertEqual(len(self.raw), 12288)
        self.assertEqual(digest(self.raw), SHA)
        self.assertEqual(int.from_bytes(self.raw[0x38:0x3c], 'little'), 0x1000)
        self.assertTrue(check_windows(self.raw))

    def test_mutation_rejected_without_whole_file_hash(self):
        for a, _ in WINDOWS:
            mutant = bytearray(self.raw)
            mutant[a - 0x1000] ^= 1
            self.assertFalse(check_windows(mutant), hex(a))

    def test_exhaustive_unsigned_page_and_call_ranges(self):
        for page in range(65536):
            t = trace(page >> 8, page & 255, 0x200090aa)
            self.assertEqual(t is not None, page <= 95, hex(page))
            if t:
                p, source, aligned, calls = t
                self.assertEqual((p, source, aligned), (page, 0x200090ac, 0x200090ac))
                self.assertEqual(calls, [(0x08008000 + page*1024 + i, aligned+i)
                                         for i in (0, 256, 512, 768)])
                # Each helper aligns its address down to 256; 64 word stores.
                for dest, _ in calls:
                    self.assertEqual(dest & 255, 0)
                    self.assertEqual((dest & ~255) + 252 + 3, dest + 255)

    def test_boundaries_and_negative_guards(self):
        self.assertEqual(trace(0, 0, 0)[3][0][0], 0x08008000)
        self.assertEqual(trace(0, 95, 0)[3][-1][0] + 255, 0x0801ffff)
        for high, low in [(0, 96), (1, 0), (255, 255), (95, 0)]:
            self.assertIsNone(trace(high, low, 0))
        for n in (0, 1025, 1027, 0xffffffff):
            self.assertIsNone(trace(0, 0, 0, n))
        self.assertIsNone(trace(0, 0, 0, active=False))
        with self.assertRaises(ValueError):
            trace(0, 256, 0)

    def test_source_wrap_and_alignment_are_numeric_only(self):
        for payload in (0xfffffffc, 0xfffffffd, 0xfffffffe, 0xffffffff, 0, 1, 2, 3):
            _, source, aligned, calls = trace(0, 0, payload)
            self.assertEqual(source, (payload + 2) & MASK)
            self.assertEqual(aligned, source & 0xfffffffc)
            self.assertEqual([s for _, s in calls], [(aligned+i) & MASK for i in (0, 256, 512, 768)])
        self.assertEqual(trace(0, 0, 0xfffffffd)[3][-1][1], 0x2fc)
        self.assertEqual(trace(0, 0, 0xfffffffe)[1:3], (0, 0))


if __name__ == '__main__':
    unittest.main(verbosity=2)
