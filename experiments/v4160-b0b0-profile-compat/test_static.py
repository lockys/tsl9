"""Fixed-byte checks only: no compiler, ELF reader, C execution or ISA simulation."""
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
OWNER = ROOT / 'experiments/tsl9-record-helpers/src/record_helpers.v1.c'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
OWNER_SHA = 'deebd11bf4d9f852eade96fb581004ae2edbbbc14e3fbd11c5811bcd64e9e2f6'
LEAF_SHA = '87e2f32124ff79e6e034845c0edb9ed33dc9b3dc96a491cf46eab279433a8884'
REFERENCE_SHA = 'e3f6cec8c02b5619561c69f571f2b440db3d1b264b672e0f7520483a03dcf7eb'
PC, BASE, DEST = 0xb0b0, 0x8000, 0x2000beeb
BASELINE = bytes.fromhex('b7c50020a385a5ee8280')
MEDANY = bytes.fromhex('97150020a38da5e28280')
REFERENCE = bytes.fromhex('97170020a38da7e28280')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_window(data):
    start = PC - BASE
    if len(data) < start + len(REFERENCE) or data[start:start + len(REFERENCE)] != REFERENCE:
        raise ValueError('reference window mismatch')


def check_image(data):
    if len(data) != 76800 or digest(data) != IMAGE_SHA:
        raise ValueError('reference image identity mismatch')
    check_window(data)


def check_fields(data, first_opcode, register, upper, offset):
    """Decode only the U-type, S-type and fixed c.ret fields used here."""
    if len(data) != 10:
        raise ValueError('length')
    u = int.from_bytes(data[:4], 'little')
    s = int.from_bytes(data[4:8], 'little')
    imm = ((s >> 25) << 5) | ((s >> 7) & 31)
    imm = imm - 4096 if imm & 0x800 else imm
    fields = (u & 0x7f, (u >> 7) & 31, u & 0xfffff000,
              s & 0x7f, (s >> 12) & 7, (s >> 15) & 31,
              (s >> 20) & 31, imm, data[8:])
    expected = (first_opcode, register, upper, 0x23, 0, register, 10, offset, b'\x82\x80')
    if fields != expected:
        raise ValueError('instruction fields mismatch')


def check_bytes(data, expected):
    if data != expected:
        raise ValueError('recorded text mismatch')


class StaticChecks(unittest.TestCase):
    def test_pinned_inputs(self):
        self.assertEqual(digest((HERE / 'leaf.c').read_bytes()), LEAF_SHA)
        self.assertEqual(digest(OWNER.read_bytes()), OWNER_SHA)
        self.assertEqual(digest(REFERENCE), REFERENCE_SHA)
        check_image(IMAGE.read_bytes())

    def test_recorded_text_fields(self):
        for data, opcode, reg, upper, offset in (
            (BASELINE, 0x37, 11, 0x2000c000, -0x115),
            (MEDANY, 0x17, 11, 0x20001000, -0x1c5),
            (REFERENCE, 0x17, 15, 0x20001000, -0x1c5),
        ):
            with self.subTest(data=data.hex()):
                check_fields(data, opcode, reg, upper, offset)
                self.assertEqual((upper + (PC if opcode == 0x17 else 0) + offset) & 0xffffffff, DEST)
        self.assertNotEqual(BASELINE, REFERENCE)
        self.assertNotEqual(MEDANY, REFERENCE)

    def test_direct_negative_checks(self):
        # Exercise byte and field checkers directly, not behind whole-file hashes.
        for data, opcode, reg, upper, offset in (
            (BASELINE, 0x37, 11, 0x2000c000, -0x115),
            (MEDANY, 0x17, 11, 0x20001000, -0x1c5),
            (REFERENCE, 0x17, 15, 0x20001000, -0x1c5),
        ):
            for i in range(len(data)):
                for bit in range(8):
                    bad = bytearray(data)
                    bad[i] ^= 1 << bit
                    with self.assertRaises(ValueError):
                        check_bytes(bad, data)
                    with self.assertRaises(ValueError):
                        check_fields(bad, opcode, reg, upper, offset)
            for bad in (data[:-1], data + b'\0'):
                with self.assertRaises(ValueError):
                    check_bytes(bad, data)
                with self.assertRaises(ValueError):
                    check_fields(bad, opcode, reg, upper, offset)
        image = IMAGE.read_bytes()
        start = PC - BASE
        for i in range(len(REFERENCE)):
            for bit in range(8):
                bad = bytearray(image)
                bad[start + i] ^= 1 << bit
                with self.assertRaises(ValueError):
                    check_window(bad)
        with self.assertRaises(ValueError):
            check_window(image[:start + len(REFERENCE) - 1])
        bad = bytearray(image)
        bad[start - 1] ^= 1
        check_window(bad)
        with self.assertRaises(ValueError):
            check_image(bad)
        for bad in (image[:-1], image + b'\0'):
            with self.assertRaises(ValueError):
                check_image(bad)


if __name__ == '__main__':
    unittest.main()
