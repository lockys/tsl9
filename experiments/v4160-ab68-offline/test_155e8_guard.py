#!/usr/bin/env python3
"""Offline 0x155e8 guard projection; not a complete CPU or device model."""
import hashlib
import unittest
from pathlib import Path

BIN = (Path(__file__).resolve().parents[2] / 'firmware-downloads' /
       'legacy-options-2026-10-20' / 'BINs' / 'ID-2966-V4.1.60-decoded.bin')
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE = bytes.fromhex('9307650093f7f70f0947636df718')
MASK = 0xffffffff


def run(code, a0):
    if len(code) != 14:
        raise ValueError('invalid instruction window length')
    regs = [0] * 32
    regs[10] = a0 & MASK
    for offset in (0, 4):
        word = int.from_bytes(code[offset:offset + 4], 'little')
        opcode, rd = word & 127, (word >> 7) & 31
        funct3, rs1 = (word >> 12) & 7, (word >> 15) & 31
        imm = (word >> 20) & 4095
        imm -= 4096 if imm & 2048 else 0
        if opcode != 0x13 or rd == 0:
            raise ValueError('unsupported instruction')
        if funct3 == 0:
            regs[rd] = (regs[rs1] + imm) & MASK
        elif funct3 == 7:
            regs[rd] = regs[rs1] & (imm & MASK)
        else:
            raise ValueError('unsupported ALU operation')
    if code[8:10] != b'\x09\x47':
        raise ValueError('unsupported compressed instruction')
    regs[14] = 2
    branch = int.from_bytes(code[10:14], 'little')
    if branch & 127 != 0x63 or (branch >> 12) & 7 != 6:
        raise ValueError('unsupported branch')
    rs1, rs2 = (branch >> 15) & 31, (branch >> 20) & 31
    disp = (((branch >> 31) & 1) << 12 | ((branch >> 7) & 1) << 11 |
            ((branch >> 25) & 63) << 5 | ((branch >> 8) & 15) << 1)
    if disp & 4096:
        disp -= 8192
    pc = ((0x155f2 + disp) & MASK) if regs[rs1] < regs[rs2] else 0x155f6
    return regs[15], regs[14], pc


class Guard(unittest.TestCase):
    def test_original_identity(self):
        image = BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), SHA)
        self.assertEqual(image[0x155e8 - 0x8000:0x155f6 - 0x8000], CODE)

    def test_all_low_bytes_and_upper_bits(self):
        for high in (0, 0x100, 0x12340000, 0xffffff00):
            for low in range(256):
                value = high | low
                n = (value + 6) & 255
                self.assertEqual(run(CODE, value), (n, 2, 0x1578c if n > 2 else 0x155f6))
        self.assertEqual([i for i in range(256) if run(CODE, i)[2] == 0x155f6], [250, 251, 252])

    def test_semantic_mutants_and_rejection(self):
        altered = bytearray(CODE)
        altered[2] ^= 0x10  # ADDI +6 -> +7
        self.assertNotEqual(run(altered, 250), run(CODE, 250))
        altered = bytearray(CODE)
        altered[11] ^= 0x10  # BLTU -> BGEU, deliberately unsupported
        with self.assertRaises(ValueError):
            run(altered, 250)
        altered = bytearray(CODE)
        altered[10] ^= 0x80  # branch immediate changes destination
        self.assertNotEqual(run(altered, 0)[2], run(CODE, 0)[2])
        with self.assertRaises(ValueError):
            run(CODE[:-1], 0)


if __name__ == '__main__':
    unittest.main()
