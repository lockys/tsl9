#!/usr/bin/env python3
"""Offline tests for d314 instruction fields and successful-read projection."""
import unittest
from unittest.mock import patch
import decode_semantics as model


class D314DecodeTests(unittest.TestCase):
    def test_original_and_length(self):
        self.assertEqual(model.decode(model.EXPECTED), 0x2000bf5c)
        for code in (model.EXPECTED[:-1], model.EXPECTED + b'\x00'):
            with self.subTest(length=len(code)), self.assertRaisesRegex(ValueError, 'length'):
                model.decode(code)

    def test_field_checks_independent_of_identity_pin(self):
        original = model.EXPECTED
        # Re-pin altered bytes, so failures exercise decoding rather than the
        # independent original-byte identity check.
        for field, offset, bit, reason in (
            ('auipc opcode', 0, 0, 'auipc'),
            ('auipc rd', 0, 7, 'auipc'),
            ('auipc immediate', 0, 12, 'address'),
            ('load opcode', 4, 0, 'lhu'),
            ('load rd', 4, 7, 'lhu'),
            ('load funct3', 4, 12, 'lhu'),
            ('load rs1', 4, 15, 'lhu'),
            ('load immediate', 4, 20, 'address'),
            ('sltu', 8, 0, 'sltu'),
            ('return', 12, 0, 'return'),
        ):
            data = bytearray(original)
            data[offset + bit // 8] ^= 1 << (bit % 8)
            altered = bytes(data)
            with self.subTest(field=field), patch.object(model, 'EXPECTED', altered):
                with self.assertRaisesRegex(ValueError, reason):
                    model.decode(altered)

    def test_exact_identity_is_independent_guard(self):
        # AUIPC +0x1000 and LHU immediate -0x1000 cannot be represented as
        # one signed 12-bit offset here, so change only a reserved output bit
        # in a controlled test by altering the expected identity instead.
        altered_pin = bytes([model.EXPECTED[0] ^ 1]) + model.EXPECTED[1:]
        with patch.object(model, 'EXPECTED', altered_pin):
            with self.assertRaisesRegex(ValueError, 'original instructions'):
                model.decode(bytes.fromhex('17f5ff1f035585c43335a0008280'))

    def test_all_halfword_values(self):
        for value in range(0x10000):
            self.assertEqual(model.project(value), int(value != 0))

    def test_out_of_range_or_non_integer_rejected(self):
        for value in (-1, 0x10000, 1.5, '1', None):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'halfword range'):
                model.project(value)


if __name__ == '__main__':
    unittest.main()
