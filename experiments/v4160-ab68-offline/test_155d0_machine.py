#!/usr/bin/env python3
"""Small decoder for the pinned 155d0 entry, not a complete RV32 CPU."""
import unittest
import test_155d0_entry_order as model

MASK = 0xffffffff


def run(code, mem, gp, sp, s1, ra, s0, s2):
    regs = [0] * 32
    regs[3], regs[2], regs[9], regs[1], regs[8], regs[18] = gp, sp, s1, ra, s0, s2
    pc = 0
    while pc < len(code):
        op = int.from_bytes(code[pc:pc + 2], 'little')
        if op & 3 != 3:
            # Only exact encodings used by this window are recognized.
            if op == 0x1141:
                regs[2] = (regs[2] - 16) & MASK
            elif op in (0xc226, 0xc606, 0xc422, 0xc04a):
                reg, offset = {0xc226: (9, 4), 0xc606: (1, 12),
                               0xc422: (8, 8), 0xc04a: (18, 0)}[op]
                model.store(mem, (regs[2] + offset) & MASK, regs[reg])
            elif op == 0x409c:
                regs[15] = model.load(mem, regs[9])
            elif op == 0x8ba1:
                regs[15] &= 8
            elif op == 0xcb81:
                if pc != 22:
                    raise ValueError('branch at wrong location')
                return regs, 0x155f6 if regs[15] == 0 else 0x155e8
            else:
                raise ValueError('unsupported compressed instruction')
            pc += 2
        else:
            if pc + 4 > len(code):
                raise ValueError('truncated word')
            word = int.from_bytes(code[pc:pc + 4], 'little')
            opcode, rd, funct3, rs1 = word & 127, (word >> 7) & 31, (word >> 12) & 7, (word >> 15) & 31
            imm = (word >> 20) & 4095
            imm -= 4096 if imm & 2048 else 0
            if opcode == 0x13 and funct3 == 0:
                regs[rd] = (regs[rs1] + imm) & MASK
            elif opcode == 0x03 and funct3 == 4:
                regs[rd] = mem[(regs[rs1] + imm) & MASK]
            else:
                raise ValueError('unsupported instruction')
            pc += 4
    raise ValueError('missing branch')


class EntryMachine(unittest.TestCase):
    def test_ordered_memory_and_registers(self):
        for mode in range(3):
            for byte in range(256):
                mem = {0x2004: byte, 0x3004: byte ^ 8}
                model.store(mem, 0x1054, 0x2000)
                sp = (0x4010, 0x1060, 0x2008)[mode]
                state = (0x1000, sp, 0x3000, byte, 0x12345678, 0x11223344)
                first, second = dict(mem), dict(mem)
                pointer, flag, pc = model.entry(first, *state)
                regs, actual_pc = run(model.CODE, second, *state)
                self.assertEqual((regs[15], regs[9], regs[2], actual_pc),
                                 (flag, 0x1054, (sp - 16) & MASK, pc))
                self.assertEqual(first, second)

    def test_mutants_not_silently_accepted(self):
        for pos in (0, 2, 8, 10, 12, 18, 20, 22):
            changed = bytearray(model.CODE)
            changed[pos] ^= 4
            mem = {0x2004: 8}
            model.store(mem, 0x1054, 0x2000)
            with self.subTest(pos=pos), self.assertRaises(ValueError):
                run(changed, mem, 0x1000, 0x4010, 1, 2, 3, 4)


if __name__ == '__main__':
    unittest.main()
