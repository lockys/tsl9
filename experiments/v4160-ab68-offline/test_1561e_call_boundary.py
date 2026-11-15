#!/usr/bin/env python3
"""Decode call setup at 1561e; stop before 9124, whose effects are unknown."""
import hashlib
import unittest
import test_155d0_entry_order as entry

CODE = bytes.fromhex('81465146814517050000130565f0ef309faf')
MASK = 0xffffffff


def decode(code):
    if len(code) != 18 or code[:6] != bytes.fromhex('814651468145'):
        raise ValueError('unsupported compressed setup')
    regs = [0] * 32
    regs[13], regs[12], regs[11] = 0, 20, 0
    auipc = int.from_bytes(code[6:10], 'little')
    if auipc & 127 != 0x17 or (auipc >> 7) & 31 != 10:
        raise ValueError('unsupported auipc')
    regs[10] = (0x15624 + (auipc & 0xfffff000)) & MASK
    addi = int.from_bytes(code[10:14], 'little')
    if (addi & 127, (addi >> 7) & 31, (addi >> 12) & 7, (addi >> 15) & 31) != (0x13, 10, 0, 10):
        raise ValueError('unsupported addi')
    imm = (addi >> 20) & 4095
    imm -= 4096 if imm & 2048 else 0
    regs[10] = (regs[10] + imm) & MASK
    jal = int.from_bytes(code[14:18], 'little')
    if jal & 127 != 0x6f or (jal >> 7) & 31 != 1:
        raise ValueError('unsupported call')
    disp = (((jal >> 31) & 1) << 20 | ((jal >> 12) & 255) << 12 |
            ((jal >> 20) & 1) << 11 | ((jal >> 21) & 1023) << 1)
    if disp & (1 << 20):
        disp -= 1 << 21
    return tuple(regs[10:14]), (0x1562c + disp) & MASK, 0x15630


class CallBoundary(unittest.TestCase):
    def test_original_and_setup(self):
        image = entry.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), entry.SHA)
        self.assertEqual(image[0x1561e - 0x8000:0x15630 - 0x8000], CODE)
        self.assertEqual(decode(CODE), ((0x1552a, 0, 20, 0), 0x9124, 0x15630))

    def test_mutations(self):
        changed = bytearray(CODE)
        changed[12] ^= 0x10
        self.assertNotEqual(decode(changed)[0][0], decode(CODE)[0][0])
        changed = bytearray(CODE)
        changed[14] ^= 0x80
        with self.assertRaises(ValueError):
            decode(changed)
        changed = bytearray(CODE)
        changed[16] ^= 0x10
        self.assertNotEqual(decode(changed)[1], decode(CODE)[1])
        with self.assertRaises(ValueError):
            decode(CODE[:-1])


if __name__ == '__main__':
    unittest.main()
