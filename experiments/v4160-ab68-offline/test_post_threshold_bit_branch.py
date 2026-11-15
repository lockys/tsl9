#!/usr/bin/env python3
"""Decode 0x103ca..0x103da with stable synthetic byte-addressed RAM.

Stops before stack restores, stores, tail calls and return; not a CPU or device
proof. Ordered reads matter when input aliases GP-relative state.
"""
import hashlib
import unittest
from unittest.mock import patch

import caller_threshold_projection as prefix

START = 0x103ca
CODE = bytes.fromhex('83c7740003c721058583858b6301f702')
MASK = 0xffffffff


def project(code, s1, gp, memory):
    if code != CODE:
        raise ValueError('instruction identity')
    r = [0] * 32
    r[9], r[3] = s1 & MASK, gp & MASK
    events = []
    pc = START
    while pc < START + len(code):
        off = pc - START
        half = int.from_bytes(code[off:off + 2], 'little')
        if half == 0x8385:
            r[15] >>= 1
            pc += 2
            continue
        if half == 0x8b85:
            r[15] &= 1
            pc += 2
            continue
        if half & 3 != 3:
            raise ValueError('unknown compressed instruction')
        word = int.from_bytes(code[off:off + 4], 'little')
        op, rd, f3, rs1, rs2 = word & 127, (word >> 7) & 31, (word >> 12) & 7, (word >> 15) & 31, (word >> 20) & 31
        if op == 3 and f3 == 4:
            imm = word >> 20
            imm -= 4096 if imm & 2048 else 0
            addr = (r[rs1] + imm) & MASK
            r[rd] = memory[addr]
            events.append(('read', addr, r[rd]))
            pc += 4
        elif op == 0x63 and f3 == 0:
            imm = ((word >> 31) << 12) | (((word >> 7) & 1) << 11) | (((word >> 25) & 63) << 5) | (((word >> 8) & 15) << 1)
            imm -= 8192 if imm & 4096 else 0
            return ((pc + imm) & MASK if r[rs1] == r[rs2] else pc + 4), r[15], events
        else:
            raise ValueError('unknown instruction')
    raise ValueError('branch not reached')


class PostThresholdTests(unittest.TestCase):
    def test_original_identity_and_mutations(self):
        image = prefix.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), prefix.SHA)
        self.assertEqual(image[START-0x8000:START-0x8000+len(CODE)], CODE)
        for i in range(len(CODE)):
            changed = bytearray(CODE)
            changed[i] ^= 1
            with self.assertRaisesRegex(ValueError, 'instruction identity'):
                project(bytes(changed), 0, 0, {})

    def test_all_bytes_and_state(self):
        for value in range(256):
            for state in range(256):
                s1, gp = 0x100, 0xffffffae
                bit = (value >> 1) & 1
                expected = (0x103f8 if state == bit else 0x103da, bit,
                            [('read', 0x107, value), ('read', 0, state)])
                self.assertEqual(project(CODE, s1, gp, {0x107: value, 0: state}), expected)

    def test_semantic_mutations_beyond_identity_pin(self):
        # Vary the first LBU immediate and branch target with the identity pin
        # deliberately replaced; these test behavior, not just pin rejection.
        memory = {0x106: 0, 0x107: 2, 0x200: 1}
        good = project(CODE, 0x100, 0x1ae, memory)
        changed_load = bytearray(CODE)
        changed_load[2] ^= 0x10  # lbu a5,6(s1), not 7(s1)
        changed_branch = bytearray(CODE)
        changed_branch[12] ^= 0x80  # change BEQ destination
        for modified in (bytes(changed_load), bytes(changed_branch)):
            with self.subTest(code=modified.hex()), patch.dict(globals(), CODE=modified):
                self.assertNotEqual(project(modified, 0x100, 0x1ae, memory), good)

    def test_alias_and_missing_memory(self):
        # Both loads refer to address zero, including modular address wrap.
        for value in range(256):
            bit = (value >> 1) & 1
            result = project(CODE, 0xfffffff9, 0xffffffae, {0: value})
            self.assertEqual(result, (0x103f8 if value == bit else 0x103da,
                                      bit, [('read', 0, value), ('read', 0, value)]))
        with self.assertRaises(KeyError):
            project(CODE, 0x100, 0xffffffae, {0x107: 1})


if __name__ == '__main__':
    unittest.main()
