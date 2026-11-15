#!/usr/bin/env python3
"""Boundary and instruction-identity controls for the bounded branch model."""
import unittest
from unittest.mock import patch
import caller_threshold_branch as p


class BranchTests(unittest.TestCase):
    def test_image_and_mutations(self):
        image = p.prefix.BIN.read_bytes()
        p.verify_image(image)
        for base, code in p.SEGMENTS.items():
            for i in range(len(code)):
                changed = bytearray(image)
                changed[base - 0x8000 + i] ^= 1
                with patch.object(p.prefix, 'SHA', p.hashlib.sha256(changed).hexdigest()):
                    with self.assertRaisesRegex(ValueError, 'instruction identity'):
                        p.verify_image(changed)

    def test_boundaries(self):
        gp = 0xfffffecc
        for threshold, state, s0, expected in (
            (59, 0, 60, None), (60, 0, 60, None),
            (60, 0, 61, (0x167a6, 159)), (60, 2, 60, (0x167a6, 158)),
            (60, 2, 61, None), (255, 255, 0xffffffff, None),
        ):
            with self.subTest(threshold=threshold, state=state, s0=s0):
                pc, call, memory, events = p.run(threshold, state, s0, gp)
                self.assertEqual(call, expected)
                self.assertEqual(pc, 0x103c6 if expected else 0x103ca)
                if expected:
                    self.assertEqual(events, [('write', 0, 1 if state == 0 else 0)])
                    self.assertEqual(memory[0], 1 if state == 0 else 0)
                else:
                    self.assertEqual(events, [])
                    self.assertEqual(memory[0], state)

    def test_unsupported_instruction_and_bad_input(self):
        corrupt = dict(p.SEGMENTS)
        corrupt[0x103ae] = b'\x01\x00' + corrupt[0x103ae][2:]
        with patch.object(p, 'SEGMENTS', corrupt), self.assertRaisesRegex(ValueError, 'unsupported'):
            p.run(0, 0, 0, 0)
        for value in (-1, 256):
            with self.assertRaises(ValueError):
                p.run(value, 0, 0, 0)
            with self.assertRaises(ValueError):
                p.run(0, value, 0, 0)


if __name__ == '__main__':
    unittest.main()
