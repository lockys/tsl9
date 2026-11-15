#!/usr/bin/env python3
"""Limited decoder for 0x1560e guard, stopping before the external call.

No resident provider, instruction fetch faults, concurrency or device execution
is modeled. The full-width incoming a0 is preserved in s0.
"""
import hashlib
import unittest
import test_155d0_entry_order as entry

CODE = bytes.fromhex('1309f5ff1377f90f9d472a8463ebe700')
MASK = 0xffffffff


def run(code, a0):
    if len(code) != 16:
        raise ValueError('invalid window length')
    regs = [0] * 32
    regs[10] = a0 & MASK
    for offset in (0, 4):
        word = int.from_bytes(code[offset:offset + 4], 'little')
        op, rd, f, rs1 = word & 127, (word >> 7) & 31, (word >> 12) & 7, (word >> 15) & 31
        imm = (word >> 20) & 4095
        imm -= 4096 if imm & 2048 else 0
        if op != 0x13 or rd == 0:
            raise ValueError('unsupported instruction')
        if f == 0:
            regs[rd] = (regs[rs1] + imm) & MASK
        elif f == 7:
            regs[rd] = regs[rs1] & (imm & MASK)
        else:
            raise ValueError('unsupported operation')
    if code[8:12] != bytes.fromhex('9d472a84'):
        raise ValueError('unsupported compressed instruction')
    regs[15], regs[8] = 7, regs[10]
    branch = int.from_bytes(code[12:16], 'little')
    if branch & 127 != 0x63 or (branch >> 12) & 7 != 6:
        raise ValueError('unsupported branch')
    rs1, rs2 = (branch >> 15) & 31, (branch >> 20) & 31
    disp = (((branch >> 31) & 1) << 12 | ((branch >> 7) & 1) << 11 |
            ((branch >> 25) & 63) << 5 | ((branch >> 8) & 15) << 1)
    if disp & 4096:
        disp -= 8192
    pc = (0x1561a + disp) & MASK if regs[rs1] < regs[rs2] else 0x1561e
    return regs[18], regs[14], regs[8], pc


class DispatchGuard(unittest.TestCase):
    def test_identity(self):
        image = entry.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), entry.SHA)
        self.assertEqual(image[0x1560e - 0x8000:0x1561e - 0x8000], CODE)

    def test_full_width_inputs(self):
        for high in (0, 0x100, 0x12340000, 0xffffff00):
            for low in range(256):
                value = high | low
                sub = (value - 1) & MASK
                self.assertEqual(run(CODE, value),
                                 (sub, sub & 255, value, 0x15630 if (sub & 255) > 7 else 0x1561e))

    def test_semantic_mutations(self):
        altered = bytearray(CODE)
        altered[2] ^= 0x10  # addi -1 -> -2
        self.assertNotEqual(run(altered, 1), run(CODE, 1))
        altered = bytearray(CODE)
        altered[12] ^= 0x80  # branch displacement
        self.assertNotEqual(run(altered, 0)[3], run(CODE, 0)[3])
        altered = bytearray(CODE)
        altered[8] ^= 1
        with self.assertRaises(ValueError):
            run(altered, 1)
        with self.assertRaises(ValueError):
            run(CODE[:-1], 1)


if __name__ == '__main__':
    unittest.main()
