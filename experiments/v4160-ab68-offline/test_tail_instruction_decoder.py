#!/usr/bin/env python3
"""Finite instruction projection of the two 0x103da/0x103f8 tails.

Compressed instructions are recognized by exact encoding, not a general RVC
interpreter. Memory accesses must succeed; faults and asynchronous effects are
outside this test. The original image is read only.
"""
import hashlib
import random
import unittest

import caller_threshold_projection as prefix
import test_post_threshold_tail_order as oracle

MASK = 0xffffffff


def execute(code, pc, sp, gp, a5, memory):
    regs = {1: 0, 2: sp & MASK, 3: gp & MASK, 8: 0, 9: 0, 15: a5 & MASK}
    events = []
    start = pc
    for _ in range(8):
        off = pc - start
        half = int.from_bytes(code[off:off + 2], 'little')
        if len(code[off:off + 2]) != 2:
            raise ValueError('truncated instruction')
        if half in (0x4422, 0x40b2, 0x4492):
            rd, offset = {0x4422: (8, 8), 0x40b2: (1, 12), 0x4492: (9, 4)}[half]
            address = (regs[2] + offset) & MASK
            value = sum(memory[(address + i) & MASK] << (8 * i) for i in range(4))
            regs[rd] = value
            events.append(('read32', address, value))
            pc += 2
        elif half == 0x0141:  # c.addi sp,16
            regs[2] = (regs[2] + 16) & MASK
            pc += 2
        elif half == 0x8082:  # c.jr ra
            return regs[2], (regs[8], regs[1], regs[9]), regs[1] & ~1, events
        elif half & 3 == 3:
            raw = code[off:off + 4]
            if len(raw) != 4:
                raise ValueError('truncated instruction')
            ins = int.from_bytes(raw, 'little')
            opcode = ins & 127
            if opcode == 0x23 and (ins >> 12) & 7 == 0:
                rs1, rs2 = (ins >> 15) & 31, (ins >> 20) & 31
                imm = ((ins >> 25) << 5) | ((ins >> 7) & 31)
                if imm & 0x800:
                    imm -= 0x1000
                if rs1 not in regs or rs2 not in regs:
                    raise ValueError('unsupported register')
                address = (regs[rs1] + imm) & MASK
                value = regs[rs2] & 255
                memory[address] = value
                events.append(('write8', address, value))
                pc += 4
            elif opcode == 0x6f and (ins >> 7) & 31 == 0:
                imm = (((ins >> 31) & 1) << 20 | ((ins >> 12) & 255) << 12 |
                       ((ins >> 20) & 1) << 11 | ((ins >> 21) & 1023) << 1)
                if imm & (1 << 20):
                    imm -= 1 << 21
                return regs[2], (regs[8], regs[1], regs[9]), (pc + imm) & MASK, events
            else:
                raise ValueError('unsupported instruction')
        else:
            raise ValueError('unsupported instruction')
    raise ValueError('instruction budget exhausted')


class DecoderComparison(unittest.TestCase):
    def test_original_tails_against_model(self):
        image = prefix.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), prefix.SHA)
        self.assertEqual(image[0x103da - 0x8000:0x103ea - 0x8000], oracle.TAIL)
        self.assertEqual(image[0x103f8 - 0x8000:0x10402 - 0x8000], oracle.RETURN)
        rng = random.Random(0x103da)
        for changed, start, end in ((True, 0x103da, 0x103ea), (False, 0x103f8, 0x10402)):
            code = image[start - 0x8000:end - 0x8000]
            for i in range(1024):
                sp = (0xfffffff8 if i % 17 == 0 else rng.getrandbits(32))
                address = (sp + (4, 8, 12, 20)[i % 4]) & MASK
                gp = (address - 82) & MASK
                memory = {(sp + n) & MASK: rng.randrange(256) for n in range(24)}
                bit = rng.getrandbits(32)
                one, two = memory.copy(), memory.copy()
                self.assertEqual(execute(code, start, sp, gp, bit, one),
                                 oracle.model(sp, gp, bit, two, changed))
                self.assertEqual(one, two)

    def test_mutants_change_observable_behavior(self):
        memory = {0x100 + i: i + 1 for i in range(32)}
        expected = execute(oracle.TAIL, 0x103da, 0x100, 0x100 - 82, 7, memory.copy())
        # Swap the two compressed restore instructions: register assignment and order change.
        altered = oracle.TAIL[2:4] + oracle.TAIL[:2] + oracle.TAIL[4:]
        self.assertNotEqual(execute(altered, 0x103da, 0x100, 0x100 - 82, 7, memory.copy()), expected)
        # SB offset 82 -> 83 changes the observed destination.
        altered = bytearray(oracle.TAIL)
        altered[6] ^= 0x80
        self.assertNotEqual(execute(altered, 0x103da, 0x100, 0x100 - 82, 7, memory.copy()), expected)
        with self.assertRaises(ValueError):
            execute(b'\x00\x00', 0x103da, 0x100, 0, 0, memory.copy())


if __name__ == '__main__':
    unittest.main()
