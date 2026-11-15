#!/usr/bin/env python3
"""Limited 155fc instruction decoder versus the separate order projection.

Compressed loads and stack adjustment use exact encodings. Memory must be
ordinary successful synthetic byte RAM; this is not a full CPU or device.
"""
import random
import unittest
import test_155fc_tail_order as oracle

MASK = 0xffffffff


def run(code, sp, gp, a0, memory):
    regs = {0: 0, 2: sp & MASK, 3: gp & MASK, 10: a0 & MASK}
    events = []
    pc = 0x155fc
    for _ in range(7):
        off = pc - 0x155fc
        raw = code[off:off + 2]
        if len(raw) != 2:
            raise ValueError('truncated')
        half = int.from_bytes(raw, 'little')
        if half in (0x4422, 0x40b2, 0x4492, 0x4902):
            rd, disp = {0x4422: (8, 8), 0x40b2: (1, 12), 0x4492: (9, 4), 0x4902: (18, 0)}[half]
            addr = (regs[2] + disp) & MASK
            value = sum(memory[(addr + i) & MASK] << (8 * i) for i in range(4))
            regs[rd] = value
            events.append(('read32', addr, value))
            pc += 2
        elif half == 0x0141:
            regs[2] = (regs[2] + 16) & MASK
            pc += 2
        elif half & 3 == 3:
            raw = code[off:off + 4]
            if len(raw) != 4:
                raise ValueError('truncated')
            ins = int.from_bytes(raw, 'little')
            opcode = ins & 127
            if opcode == 0x23 and (ins >> 12) & 7 == 0:
                rs1, rs2 = (ins >> 15) & 31, (ins >> 20) & 31
                if rs1 not in regs or rs2 not in regs:
                    raise ValueError('unsupported register')
                imm = ((ins >> 25) << 5) | ((ins >> 7) & 31)
                imm -= 4096 if imm & 2048 else 0
                address = (regs[rs1] + imm) & MASK
                value = regs[rs2] & 255
                memory[address] = value
                events.append(('write8', address, value))
                pc += 4
            elif opcode == 0x6f and ((ins >> 7) & 31) == 0:
                imm = (((ins >> 31) & 1) << 20 | ((ins >> 12) & 255) << 12 |
                       ((ins >> 20) & 1) << 11 | ((ins >> 21) & 1023) << 1)
                imm -= 1 << 21 if imm & (1 << 20) else 0
                return regs[2], tuple(regs[r] for r in (8, 1, 9, 18)), regs[10], (pc + imm) & MASK, events
            else:
                raise ValueError('unsupported instruction')
        else:
            raise ValueError('unsupported instruction')
    raise ValueError('budget exceeded')


class Decoder(unittest.TestCase):
    def test_projection_and_aliases(self):
        image = oracle.entry.BIN.read_bytes()
        import hashlib
        self.assertEqual(hashlib.sha256(image).hexdigest(), oracle.entry.SHA)
        code = image[0x155fc - 0x8000:0x1560e - 0x8000]
        self.assertEqual(code, oracle.CODE)
        rng = random.Random(0x155fc)
        for i in range(2048):
            sp = (0xfffffff8 if i % 17 == 0 else rng.getrandbits(32))
            addr = (sp + (i % 20)) & MASK
            gp = (addr - 358) & MASK
            a0 = rng.getrandbits(32)
            one = {(sp + n) & MASK: rng.randrange(256) for n in range(24)}
            two = one.copy()
            self.assertEqual(run(code, sp, gp, a0, one), oracle.project(two, sp, gp, a0))
            self.assertEqual(one, two)

    def test_mutants(self):
        mem = {0x1000 + i: i + 1 for i in range(24)}
        gp = 0x1000 - 358
        expected = run(oracle.CODE, 0x1000, gp, 9, mem.copy())
        swapped = oracle.CODE[2:4] + oracle.CODE[:2] + oracle.CODE[4:]
        self.assertNotEqual(run(swapped, 0x1000, gp, 9, mem.copy()), expected)
        changed = bytearray(oracle.CODE)
        changed[8] ^= 0x80  # store immediate: 358 -> 359
        self.assertNotEqual(run(changed, 0x1000, gp, 9, mem.copy()), expected)
        with self.assertRaises(ValueError):
            run(b'\x00\x00', 0x1000, gp, 9, mem.copy())
        with self.assertRaises(ValueError):
            run(oracle.CODE[:-1], 0x1000, gp, 9, mem.copy())


if __name__ == '__main__':
    unittest.main()
