#!/usr/bin/env python3
"""Tests decoder checks independently of firmware files and compiler tooling."""
import unittest
import decode_semantics as model


class DecoderTests(unittest.TestCase):
    def test_original_fields_and_widths(self):
        for pc, (funct3, offset, code) in model.LEAVES.items():
            with self.subTest(pc=hex(pc)):
                self.assertEqual(model.decode(code, funct3, offset, code),
                                 (2 if pc == 0x10402 else 1, offset))

    def test_unpinned_bytes_rejected(self):
        for pc, (funct3, offset, code) in model.LEAVES.items():
            for index in range(6):
                altered = bytearray(code)
                altered[index] ^= 1
                with self.subTest(pc=hex(pc), index=index), self.assertRaises(ValueError):
                    model.decode(bytes(altered), funct3, offset, code)

    def test_fields_rejected_even_when_modified_bytes_are_pinned(self):
        # Deliberately change the expected bytes too: this exercises the field
        # checks, not merely the outer exact-byte identity check.
        for pc, (funct3, offset, code) in model.LEAVES.items():
            word = int.from_bytes(code[:4], 'little')
            cases = {
                'opcode': word ^ 1,
                'rd': word ^ (1 << 7),
                'funct3': word ^ (1 << 12),
                'rs1': word ^ (1 << 15),
                'immediate': word ^ (1 << 20),
            }
            for name, altered_word in cases.items():
                altered = altered_word.to_bytes(4, 'little') + code[4:]
                with self.subTest(pc=hex(pc), field=name), self.assertRaises(ValueError):
                    model.decode(altered, funct3, offset, altered)
            altered = code[:4] + bytes.fromhex('0180')
            with self.subTest(pc=hex(pc), field='return'), self.assertRaises(ValueError):
                model.decode(altered, funct3, offset, altered)

    def test_halfword_is_little_endian_and_unsigned(self):
        spec = model.LEAVES[0x10402]
        code = spec[2]
        self.assertEqual(model.project(code, spec, 0x20004000,
                                       {0x20004050: 0x34, 0x20004051: 0x80}), 0x8034)

    def test_byte_and_modular_address_projection(self):
        spec = model.LEAVES[0x10408]
        self.assertEqual(model.project(spec[2], spec, 0xffffffae, {0: 0x80}), 0x80)
        spec = model.LEAVES[0x10402]
        self.assertEqual(model.project(spec[2], spec, 0xffffffaf,
                                       {0xffffffff: 0x34, 0: 0x12}), 0x1234)
        # The final example is mathematical only and may trap on real hardware.


if __name__ == '__main__':
    unittest.main()
