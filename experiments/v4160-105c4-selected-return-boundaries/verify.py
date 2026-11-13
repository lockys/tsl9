#!/usr/bin/env python3
"""Bounded static checks of selected-link return boundaries; no firmware execution."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
WINDOWS = {
    0x105ce: '8280',
    0x107d6: '829605cd83470400',
    0x10846: '82972a8411cd',
    0x10956: 'eff07fee2dc1',
    0x10bbe: '6ff09fc0',
    0x10bf6: 'e1b7',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def direct(pc, code):
    """Decode only the selected JAL, C.J and C.BEQZ instruction classes."""
    need(pc % 2 == 0 and len(code) in (2, 4), 'instruction width or alignment')
    v = int.from_bytes(code, 'little')
    if len(code) == 4:
        need(v & 127 == 0x6f, 'not JAL')
        imm = ((v >> 31 & 1) << 20 | (v >> 12 & 255) << 12 |
               (v >> 20 & 1) << 11 | (v >> 21 & 1023) << 1)
        return ('jal', v >> 7 & 31, (pc + signed(imm, 21)) & 0xffffffff)
    need(v & 3 == 1, 'not compressed quadrant 1')
    f = v >> 13 & 7
    if f == 5:
        imm = ((v >> 12 & 1) << 11 | (v >> 11 & 1) << 4 | (v >> 9 & 3) << 8 |
               (v >> 8 & 1) << 10 | (v >> 7 & 1) << 6 | (v >> 6 & 1) << 7 |
               (v >> 3 & 7) << 1 | (v >> 2 & 1) << 5)
        return ('cj', 0, (pc + signed(imm, 12)) & 0xffffffff)
    need(f == 6, 'not C.BEQZ')
    imm = ((v >> 12 & 1) << 8 | (v >> 10 & 3) << 3 | (v >> 5 & 3) << 6 |
           (v >> 3 & 3) << 1 | (v >> 2 & 1) << 5)
    return ('cbeqz', 8 + (v >> 7 & 7), (pc + signed(imm, 9)) & 0xffffffff)


def at(image, pc, n):
    start = pc - BASE
    need(start >= 0 and start + n <= len(image), 'out of bounds')
    return image[start:start + n]


def anchors(image):
    for pc, text in WINDOWS.items():
        b = bytes.fromhex(text)
        need(at(image, pc, len(b)) == b, 'anchor %#x' % pc)
    for pc, count, expected in (
        (0x10956, 4, ('jal', 1, 0x1083c)),
        (0x10bbe, 4, ('jal', 0, 0x107c6)),
        (0x10bf6, 2, ('cj', 0, 0x10bbe)),
        (0x107d8, 2, ('cbeqz', 10, 0x10810)),
        (0x1084a, 2, ('cbeqz', 10, 0x10866)),
        (0x1095a, 2, ('cbeqz', 10, 0x109bc)),
    ):
        need(direct(pc, at(image, pc, count)) == expected, 'edge %#x' % pc)
    # Fixed compressed bytes show the particular indirect instructions, not their targets.
    for pc, mask, expected in ((0x105ce, 0xf07f, 0x8002),
                               (0x107d6, 0xf07f, 0x9002),
                               (0x10846, 0xf07f, 0x9002)):
        h = int.from_bytes(at(image, pc, 2), 'little')
        need(h & mask == expected, 'indirect opcode %#x' % pc)
    need((int.from_bytes(at(image, 0x105ce, 2), 'little') >> 7 & 31) == 1, 'return register')
    need((int.from_bytes(at(image, 0x107d6, 2), 'little') >> 7 & 31) == 13, 'first call register')
    need((int.from_bytes(at(image, 0x10846, 2), 'little') >> 7 & 31) == 15, 'second call register')
    # Link values and not-taken successors follow from the verified instruction widths.
    calls = ((0x107d6, 2), (0x10846, 2), (0x10956, 4))
    branches = (0x107d8, 0x1084a, 0x1095a)
    return {'selected_return_sites': [hex(pc + width) for pc, width in calls],
            'conditional_branch_successors': {
                hex(pc): [hex(direct(pc, at(image, pc, 2))[2]), hex(pc + 2)] for pc in branches}}


def verify(image):
    need(len(image) == 76800, 'image length')
    need(hashlib.sha256(image).hexdigest() == SHA, 'image SHA-256')
    return anchors(image)


class Tests(unittest.TestCase):
    def test_reference(self):
        verify(IMAGE.read_bytes())

    def test_each_anchor_byte_mutation(self):
        image = IMAGE.read_bytes()
        for pc, text in WINDOWS.items():
            for i in range(len(bytes.fromhex(text))):
                altered = bytearray(image)
                altered[pc - BASE + i] ^= 1
                with self.subTest(pc=pc, byte=i), self.assertRaisesRegex(ValueError, '^anchor %#x$' % pc):
                    anchors(altered)
                with self.assertRaisesRegex(ValueError, '^image SHA-256$'):
                    verify(altered)

    def test_image_identity(self):
        image = IMAGE.read_bytes()
        with self.assertRaisesRegex(ValueError, '^image length$'):
            verify(image[:-1])
        altered = bytearray(image); altered[0] ^= 1
        with self.assertRaisesRegex(ValueError, '^image SHA-256$'):
            verify(altered)

    def test_decoder_rejects_other_forms(self):
        for pc, code in ((0x1000, b'\0\0'), (0x1000, b'\x13\0\0\0'), (0x1001, b'\x01\xa0')):
            with self.subTest(pc=pc, code=code), self.assertRaises(ValueError):
                direct(pc, code)
        self.assertEqual(direct(0x10bf6, bytes.fromhex('e1b7')), ('cj', 0, 0x10bbe))
        self.assertEqual(direct(0x10956, bytes.fromhex('eff07fee')), ('jal', 1, 0x1083c))
        self.assertEqual(direct(0x107d8, bytes.fromhex('05cd')), ('cbeqz', 10, 0x10810))

    def test_synthetic_branch_boundaries(self):
        # Independently decoded with rasm2 at PC 0x8000; includes both signs.
        for code, delta in (('01d0', -256), ('7ddc', -2), ('09c0', 2), ('7dcc', 254)):
            with self.subTest(code=code):
                self.assertEqual(direct(0x8000, bytes.fromhex(code)), ('cbeqz', 8, 0x8000 + delta))
        self.assertEqual(direct(0, bytes.fromhex('7ddc')), ('cbeqz', 8, 0xfffffffe))
        with self.assertRaisesRegex(ValueError, '^not C.BEQZ$'):
            direct(0x8000, bytes.fromhex('7dfc'))
        self.assertEqual(direct(0x8000, bytes.fromhex('e1b7')), ('cj', 0, 0x7fc8))
        self.assertEqual(direct(0x8000, bytes.fromhex('eff07fee')), ('jal', 1, 0x7ee6))


def main():
    if sys.argv[1:] == ['--test']:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() and result.testsRun == 5 else 1
    if sys.argv[1:] == ['--inspect']:
        try:
            report = verify(IMAGE.read_bytes())
            print(json.dumps({'image_sha256': SHA, 'assumed_base': hex(BASE), **report,
                'limits': 'Static selected windows only; return requires normal callee return. No reachability, ABI, complete control flow or firmware execution proof.'}, indent=2))
            return 0
        except (OSError, ValueError) as exc:
            print('FAIL: ' + str(exc), file=sys.stderr)
            return 1
    print('usage: verify.py --inspect | --test', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
