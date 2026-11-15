#!/usr/bin/env python3
"""Boundary and mutation checks for the restricted caller fragment."""
import unittest
import caller_pack_projection as p


class PackProjection(unittest.TestCase):
    def test_events_and_wrapping(self):
        sp = 0xffffffd5
        mem, events = p.run(p.CODE, 0x13, sp, {0: 0x12, 1: 0xf3})
        self.assertEqual(events, [('read', 0, 0x12), ('write', 0, 0x92),
                                  ('read', 1, 0xf3), ('write', 1, 0xf9)])
        self.assertEqual(mem, {0: 0x92, 1: 0xf9})

    def test_truncated_and_all_byte_mutations_rejected(self):
        with self.assertRaisesRegex(ValueError, 'instruction bytes'):
            p.run(p.CODE[:-1], 0, 0, {})
        for i in range(len(p.CODE)):
            mutated = bytearray(p.CODE)
            mutated[i] ^= 1
            with self.subTest(offset=i), self.assertRaisesRegex(ValueError, 'instruction bytes'):
                p.run(bytes(mutated), 0, 0, {})

    def test_missing_memory_fails(self):
        with self.assertRaises(KeyError):
            p.run(p.CODE, 0, 0, {})


if __name__ == '__main__':
    unittest.main()
