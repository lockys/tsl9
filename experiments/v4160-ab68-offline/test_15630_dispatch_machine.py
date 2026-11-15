#!/usr/bin/env python3
"""Bounded instruction decoder for 15630; successful byte RAM only.

Compressed encodings are recognized exactly; faults, asynchronous effects,
provider behavior and actual device execution are not modeled.
"""
import hashlib
import random
import unittest
import test_155d0_entry_order as entry
import test_15630_dispatch_table as model

MASK = 0xffffffff


def run(code, memory, s2):
    regs = [0] * 32
    regs[18] = s2 & MASK
    pc = 0x15630
    events = []
    for _ in range(10):
        off = pc - 0x15630
        chunk = code[off:off + 2]
        if len(chunk) != 2:
            raise ValueError('truncated')
        half = int.from_bytes(chunk, 'little')
        if half & 3 != 3:
            if half == 0x090a:
                regs[18] = (regs[18] << 2) & MASK
            elif half == 0x993a:
                regs[18] = (regs[18] + regs[14]) & MASK
            elif half == 0x97ba:
                regs[15] = (regs[15] + regs[14]) & MASK
            elif half == 0x8782:
                return regs[15] & ~1, events
            else:
                raise ValueError('unsupported compressed instruction')
            pc += 2
            continue
        chunk = code[off:off + 4]
        if len(chunk) != 4:
            raise ValueError('truncated')
        word = int.from_bytes(chunk, 'little')
        op, rd, f, rs1 = word & 127, (word >> 7) & 31, (word >> 12) & 7, (word >> 15) & 31
        imm = (word >> 20) & 4095
        imm -= 4096 if imm & 2048 else 0
        if op == 0x13 and rd:
            if f == 0:
                regs[rd] = (regs[rs1] + imm) & MASK
            elif f == 7:
                regs[rd] = regs[rs1] & (imm & MASK)
            else:
                raise ValueError('unsupported immediate')
        elif op == 0x17 and rd:
            regs[rd] = (pc + (word & 0xfffff000)) & MASK
        elif op == 3 and f == 2 and rd:
            address = (regs[rs1] + imm) & MASK
            value = sum(memory[(address + i) & MASK] << (8 * i) for i in range(4))
            regs[rd] = value
            events.append(('read32', address, value))
        elif op == 0x63 and f == 6:
            rs2 = (word >> 20) & 31
            disp = (((word >> 31) & 1) << 12 | ((word >> 7) & 1) << 11 |
                    ((word >> 25) & 63) << 5 | ((word >> 8) & 15) << 1)
            if disp & 4096:
                disp -= 8192
            if regs[rs1] < regs[rs2]:
                return (pc + disp) & MASK, events
        else:
            raise ValueError('unsupported instruction')
        pc += 4
    raise ValueError('instruction budget')


class DispatchMachine(unittest.TestCase):
    def test_actual_table_and_synthetic_words(self):
        image = entry.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), entry.SHA)
        code = image[0x15630 - 0x8000:0x15650 - 0x8000]
        table = image[model.BASE - 0x8000:model.BASE - 0x8000 + 1012]
        self.assertEqual(code, model.CODE)
        rng = random.Random(0x15630)
        for content in (table, bytes(rng.randrange(256) for _ in range(1012))):
            memory = {model.BASE + i: byte for i, byte in enumerate(content)}
            for high in (0, 0x12340000, 0xffffff00):
                for low in range(256):
                    value = high | low
                    index, address, target = model.dispatch(code, content, value)
                    actual, events = run(code, memory, value)
                    self.assertEqual(actual, target)
                    expected = [] if address is None else [('read32', address, int.from_bytes(content[index * 4:index * 4 + 4], 'little'))]
                    self.assertEqual(events, expected)

    def test_guard_and_target_mutations(self):
        code = model.CODE
        mem = {model.BASE + i: 0 for i in range(1012)}
        changed = bytearray(code)
        changed[6] ^= 0x10  # threshold 252 -> 253
        self.assertEqual(run(code, mem, 253), (0x1578c, []))
        with self.assertRaises(KeyError):  # mutated guard reads beyond the table
            run(changed, mem, 253)
        changed = bytearray(code)
        changed[20] ^= 1  # unrecognized compressed shift
        with self.assertRaises(ValueError):
            run(changed, mem, 0)
        with self.assertRaises(KeyError):
            run(code, {}, 0)
        with self.assertRaises(ValueError):
            run(code[:-1], mem, 0)


if __name__ == '__main__':
    unittest.main()
