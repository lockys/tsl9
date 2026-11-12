"""Static original-byte checks and independent abstract examples; never runs C/ISA."""
from pathlib import Path
from hashlib import sha256
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
START, END = 0x8ace, 0x8b0a
RAW = bytes.fromhex('93076042 b307f602 97260020 9386666b 6177 134757f5 9375f40f 9907 b697 2390e700 2382b700 13578400 ce95 a381e700 2e97 23813701 1377f70f 8145')
MASK = 0xffffffff


def validate_raw(raw):
    if raw != RAW:
        raise ValueError('original instruction window changed')
    validate_operands(raw)


def validate_operands(raw):
    if len(raw) != len(RAW):
        raise ValueError('window length')
    def word(off):
        return int.from_bytes(raw[off:off+4], 'little')
    mul = word(4)
    if (mul & 127, (mul >> 7) & 31, (mul >> 12) & 7,
        (mul >> 15) & 31, (mul >> 20) & 31, mul >> 25) != (0x33, 15, 0, 12, 15, 1):
        raise ValueError('mul operands')
    auipc, addi = word(8), word(12)
    if (auipc & 0xfff, addi & 0x707f, (addi >> 7) & 31, (addi >> 15) & 31,
        (addi >> 20) & 0xfff) != (0x697, 0x13, 13, 13, 1718):
        raise ValueError('address operands')
    if (START + 8 + (auipc & 0xfffff000) + 1718) & MASK != 0x2000b18c:
        raise ValueError('address value')
    for off, funct, src, disp in ((30, 1, 14, 0), (34, 0, 11, 4),
                                  (44, 0, 14, 3), (50, 0, 19, 2)):
        w = word(off)
        imm = ((w >> 25) << 5) | ((w >> 7) & 31)
        if (w & 127, (w >> 12) & 7, (w >> 15) & 31,
            (w >> 20) & 31, imm) != (0x23, funct, 15, src, disp):
            raise ValueError('store operands')


def abstract(bank, length, command):
    if bank not in (0, 1) or not 0 <= length <= MASK or not 0 <= command <= MASK:
        raise ValueError('outside cut preconditions')
    d = (0x2000b18c + bank * 1062 + 6) & MASK
    events = [(d, 2, 0x7f55), (d+4, 1, length & 255),
              (d+3, 1, (length >> 8) & 255), (d+2, 1, command & 255)]
    return events, ((length >> 8) + (length & 255) + command) & 255


class Checks(unittest.TestCase):
    def test_original_window(self):
        self.assertEqual(IMAGE.stat().st_size, 76800)
        with IMAGE.open('rb') as f:
            f.seek(START - 0x8000)
            raw = f.read(END - START)
        validate_raw(raw)
        for i in range(len(raw)):
            altered = bytearray(raw)
            altered[i] ^= 1
            with self.assertRaises(ValueError):
                validate_raw(altered)
        with self.assertRaises(ValueError):
            validate_raw(raw[:-1])

    def test_operand_rejections_and_c_pin(self):
        validate_operands(RAW)
        for off in (4, 8, 12, 30, 34, 44, 50):
            changed = bytearray(RAW)
            changed[off] ^= 1
            with self.subTest(offset=off), self.assertRaises(ValueError):
                validate_operands(changed)
        with self.assertRaises(ValueError):
            validate_operands(RAW[:-1])
        source = Path(__file__).with_name('header.c').read_bytes()
        self.assertEqual(sha256(source).hexdigest(),
                         '3af38ed6ef017ef25f1c56fc5b5e076d65968a8d42acdd0cd8abbdb3ec3213fe')

    def test_explicit_event_vectors(self):
        events, seed = abstract(0, 0x1234, 0x1ff)
        self.assertEqual(events, [(0x2000b192, 2, 0x7f55), (0x2000b196, 1, 0x34),
                                  (0x2000b195, 1, 0x12), (0x2000b194, 1, 0xff)])
        self.assertEqual(seed, 0x45)
        self.assertEqual(abstract(1, 0xffffffff, 0xffffffff)[1], 0xfd)
        self.assertEqual(abstract(1, 0, 0)[0][0][0], 0x2000b5b8)
        for bad in (-1, 2, 0xffffffff):
            with self.assertRaises(ValueError): abstract(bad, 0, 0)

    def test_order_alias_difference(self):
        # Later copy source can alias the header. Pre-header snapshots are wrong.
        memory = bytearray([0xaa] * 12)
        before = memory[8]
        for addr, width, value in abstract(0, 0x1234, 0x45)[0]:
            offset = addr - 0x2000b18c
            memory[offset:offset+width] = value.to_bytes(width, 'little')
        self.assertEqual((before, memory[8]), (0xaa, 0x45))
        self.assertNotEqual(before, memory[8])
        # 16-bit loop test is not a post-call bound on full S0.
        self.assertTrue((0x10000 & 0xffff) < 0x10000)
        self.assertFalse(0x10000 < 0x10000)

if __name__ == '__main__':
    unittest.main()
