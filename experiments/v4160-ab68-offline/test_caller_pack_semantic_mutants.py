#!/usr/bin/env python3
"""Check decoder behavior after deliberately replacing its identity pin.

These synthetic instruction mutations test the projection, not the firmware.
They do not establish device behavior or complete CPU semantics.
"""
import unittest
from unittest.mock import patch

import caller_pack_projection as p


class SemanticMutants(unittest.TestCase):
    def test_original_witness(self):
        mem, events = p.run(p.CODE, 0x13, 0, {42: 0x40, 43: 0x12, 44: 0xf3, 45: 0x66})
        self.assertEqual(events, [('read', 43, 0x12), ('write', 43, 0x92),
                                  ('read', 44, 0xf3), ('write', 44, 0xf9)])
        self.assertEqual(mem[42], 0x40)
        self.assertEqual(mem[45], 0x66)

    def test_supported_mutations_change_observable_behavior(self):
        original = p.CODE
        initial = {42: 0x40, 43: 0x12, 44: 0xf3, 45: 0x66}
        # ANDI mask 1->2, first SB offset 43->42, second SB offset 44->45.
        cases = (
            (2, 0x30, {42: 0x40, 43: 0x12, 44: 0xf9, 45: 0x66},
             [('read', 43, 0x12), ('write', 43, 0x12), ('read', 44, 0xf3), ('write', 44, 0xf9)]),
            (22, 0x80, {42: 0x92, 43: 0x12, 44: 0xf9, 45: 0x66},
             [('read', 43, 0x12), ('write', 42, 0x92), ('read', 44, 0xf3), ('write', 44, 0xf9)]),
            (34, 0x80, {42: 0x40, 43: 0x92, 44: 0xf3, 45: 0xf9},
             [('read', 43, 0x12), ('write', 43, 0x92), ('read', 44, 0xf3), ('write', 45, 0xf9)]),
        )
        for offset, mask, expected_mem, expected_events in cases:
            changed = bytearray(original)
            changed[offset] ^= mask
            with self.subTest(offset=offset), patch.object(p, 'CODE', bytes(changed)):
                self.assertEqual(p.run(bytes(changed), 0x13, 0, initial),
                                 (expected_mem, expected_events))

    def test_unknown_compressed_opcode_is_rejected_even_when_pinned(self):
        changed = bytearray(p.CODE)
        changed[12] ^= 4
        with patch.object(p, 'CODE', bytes(changed)):
            with self.assertRaisesRegex(ValueError, 'compressed instruction'):
                p.run(bytes(changed), 0x13, 0, {43: 0x12, 44: 0xf3})


if __name__ == '__main__':
    unittest.main()
