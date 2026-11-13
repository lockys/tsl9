#!/usr/bin/env python3
import unittest
from unittest.mock import patch
import verify as v


def fixtures():
    return {pc: bytes.fromhex(raw) for pc, raw in v.RAW.items()}


def mutate(windows, pc, xor):
    result = dict(windows)
    start = max(a for a in result if a <= pc)
    data = bytearray(result[start])
    offset = pc - start
    if offset >= len(data):
        raise ValueError('address outside window')
    for i, b in enumerate(xor):
        data[offset + i] ^= b
    result[start] = bytes(data)
    return result


class EvidenceTests(unittest.TestCase):
    def test_reference(self):
        v.verify(v.IMAGE.read_bytes())
        v.check_semantics(fixtures())

    def test_direct_semantic_mutations(self):
        # No whole-image or raw-byte guard is invoked here. Mutations hit
        # opcode, register, funct fields, signed immediates and all edge types.
        cases = [
            (0x102bc, b'\x01'),             # lbu opcode
            (0x102bc, b'\x80'),             # lbu rd
            (0x102bc, b'\x00\x80'),        # lbu rs1
            (0x102bc, b'\x00\x00\x10'),  # load immediate
            (0x102c0, b'\x04'),             # c.andi immediate
            (0x102c2, b'\x04'),             # c.beqz displacement
            (0x102c8, b'\x00\x10'),        # bgeu funct3
            (0x102c8, b'\x00\x01'),        # B displacement
            (0x102d0, b'\x04'),             # c.bnez displacement
            (0x102d8, b'\x00\x00\x10'),  # JAL displacement
            (0x102de, b'\x80'),             # c.li rd
            (0x102e0, b'\x80'),             # JAL rd
            (0x102e6, b'\x00\x00\x10'),
            (0xac0a, b'\x00\x00\x40'),    # 354 -> 358
            (0xac0e, b'\x04'),              # branch displacement
            (0xac10, b'\x80'),              # compressed branch register
            (0xac10, b'\x20'),              # compressed branch displacement
            (0xac16, b'\x04'),              # compressed jump displacement
            (0xac6c, b'\x00\x00\x10'),    # tail JAL displacement
            (0xd060, b'\x00\x00\x10'),    # addi immediate
            (0xd064, b'\x04'),              # c.li immediate
            (0xd066, b'\x00\x00\x10'),    # sub rs2
            (0xd06a, b'\x00\x00\x10'),    # sb source
            (0xd06e, b'\x80'),              # sb immediate
            (0xd072, b'\x00\x80'),          # sb base
            (0xd076, b'\x00\x10'),          # sb funct3
            (0xd07a, b'\x80'),              # ret register
            (0xb0b0, b'\x80'),              # auipc rd
            (0xb0b4, b'\x00\x00\x10'),    # sb source
            (0xb0b8, b'\x80'),              # ret register
        ]
        for pc, mask in cases:
            with self.subTest(pc=hex(pc), mask=mask.hex()):
                with self.assertRaises(ValueError):
                    v.check_semantics(mutate(fixtures(), pc, mask))

    def test_every_window_truncation_and_extra(self):
        for start, raw in fixtures().items():
            for length in range(len(raw)):
                windows = fixtures()
                windows[start] = raw[:length]
                with self.subTest(start=hex(start), length=length):
                    with self.assertRaises(ValueError):
                        v.check_semantics(windows)
            windows = fixtures()
            windows[start] += b'\x00'
            with self.assertRaises(ValueError):
                v.check_semantics(windows)

    def test_decoder_pc_and_signed_branches(self):
        size, ins = v.decode(bytes.fromhex('efa0bf92'), 0x102e0)
        self.assertEqual((size, ins), (4, ('jal', 1, 0xac0a)))
        self.assertEqual(v.decode(bytes.fromhex('91a8'), 0xac16), (2, ('jal', 0, 0xac6a)))
        self.assertEqual(v.decode(bytes.fromhex('d5d7'), 0xac68), (2, ('beq', 15, 0, 0xac14)))
        self.assertEqual(v.decode(bytes.fromhex('89e7'), 0xac0e), (2, ('bne', 15, 0, 0xac18)))
        self.assertNotEqual(v.decode(bytes.fromhex('efa0bf92'), 0x102e2)[1][-1], 0xac0a)
        for fragment in (b'', b'\x03', b'\x03\x00', b'\x03\x00\x00'):
            with self.assertRaises(ValueError):
                v.decode(fragment, 0)

    def test_image_identity_and_window_guards(self):
        image = v.IMAGE.read_bytes()
        with self.assertRaises(ValueError):
            v.verify(image[:-1])
        wrong = bytearray(image)
        wrong[0] ^= 1
        with self.assertRaises(ValueError):
            v.verify(wrong)
        # Make hash pass, independently exercise the real verify window path.
        class Digest:
            def hexdigest(self):
                return v.SHA256
        for start in v.RAW:
            altered = bytearray(image)
            altered[start - v.BASE] ^= 1
            with self.subTest(start=hex(start)), patch.object(v.hashlib, 'sha256', return_value=Digest()):
                with self.assertRaises(ValueError):
                    v.verify(altered)
            # Separately prove the raw pin is active, not just semantics.
            with self.subTest(raw_pin=hex(start)), patch.object(v.hashlib, 'sha256', return_value=Digest()), patch.object(v, 'check_semantics'):
                with self.assertRaisesRegex(ValueError, 'raw mismatch'):
                    v.verify(altered)
        for start, data in fixtures().items():
            with self.subTest(start=hex(start)):
                with self.assertRaises(ValueError):
                    v.extract(image[:start - v.BASE + len(data) - 1])


if __name__ == '__main__':
    unittest.main()
