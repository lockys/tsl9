"""Static checks only; the observed linked bytes are a recorded sample."""
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('leaf.c')
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SOURCE_SHA = '290336e8361500a563b725efed97714de0b293587fb79a3a2a762f2cc214d1ba'
BIN_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
REFERENCE = bytes.fromhex('97170020a38da7e28280')
OBSERVED = bytes.fromhex('97150020a38da5e28280')
PC = 0xb0b0


def decode(code, pc=PC):
    """Decode exactly AUIPC, SB, C.RET; retain fields for independent checks."""
    if len(code) != 10:
        raise ValueError('instruction sequence length')
    upper = int.from_bytes(code[:4], 'little')
    store = int.from_bytes(code[4:8], 'little')
    ret = int.from_bytes(code[8:], 'little')
    if upper & 0x7f != 0x17 or store & 0x7f != 0x23 or (store >> 12) & 7 != 0 or ret != 0x8082:
        raise ValueError('expected AUIPC, SB, C.RET')
    imm20 = upper >> 12
    offset = ((store >> 25) << 5) | ((store >> 7) & 31)
    offset -= 4096 if offset & 0x800 else 0
    rd = (upper >> 7) & 31
    rs1 = (store >> 15) & 31
    rs2 = (store >> 20) & 31
    if rd == 0 or rd != rs1:
        raise ValueError('AUIPC destination must be the SB base')
    signed_upper = imm20 - (1 << 20) if imm20 & (1 << 19) else imm20
    return {'auipc_opcode': upper & 0x7f, 'rd': rd, 'imm20': imm20,
            'sb_opcode': store & 0x7f, 'funct3': (store >> 12) & 7,
            'rs1': rs1, 'rs2': rs2, 'offset': offset,
            'ret': ret, 'address': (pc + (signed_upper << 12) + offset) & 0xffffffff}


def check_window(image):
    if image[PC - 0x8000:PC - 0x8000 + 10] != REFERENCE:
        raise ValueError('reference window')


def check_pins(source, image):
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA:
        raise ValueError('source SHA-256')
    if len(image) != 0x12c00 or hashlib.sha256(image).hexdigest() != BIN_SHA:
        raise ValueError('BIN length or SHA-256')
    check_window(image)


class StaticTests(unittest.TestCase):
    def test_pins(self):
        check_pins(SOURCE.read_bytes(), BIN.read_bytes())

    def test_decode_and_difference(self):
        expected = {'auipc_opcode': 0x17, 'rd': 15, 'imm20': 0x20001,
                    'sb_opcode': 0x23, 'funct3': 0, 'rs1': 15, 'rs2': 10,
                    'offset': -453, 'ret': 0x8082, 'address': 0x2000beeb}
        self.assertEqual(decode(REFERENCE), expected)
        expected.update(rd=11, rs1=11)
        self.assertEqual(decode(OBSERVED), expected)
        self.assertEqual([i for i, (a, b) in enumerate(zip(REFERENCE, OBSERVED)) if a != b], [1, 6])

    def test_invalid_encodings_and_lengths(self):
        for index, mask in ((0, 1), (4, 1), (5, 0x10), (8, 1), (1, 2), (6, 2)):
            altered = bytearray(REFERENCE)
            altered[index] ^= mask
            with self.subTest(index=index), self.assertRaises(ValueError):
                decode(altered)
        for code in (REFERENCE[:-1], REFERENCE + b'\0', b''):
            with self.subTest(length=len(code)), self.assertRaises(ValueError):
                decode(code)

    def test_valid_field_mutations_are_detected(self):
        for index, mask, field in ((2, 1, 'imm20'), (7, 2, 'offset'), (6, 0x10, 'rs2')):
            altered = bytearray(REFERENCE)
            altered[index] ^= mask
            with self.subTest(field=field):
                self.assertNotEqual(decode(altered)[field], decode(REFERENCE)[field])

    def test_window_guard(self):
        source, image = SOURCE.read_bytes(), BIN.read_bytes()
        altered = bytearray(image)
        altered[PC - 0x8000] ^= 1
        altered = bytes(altered)
        real_sha256 = hashlib.sha256

        def sha256_for_test(data):
            # Only substitute the BIN digest; source pinning remains real.
            return real_sha256(image if data == altered else data)

        with patch('hashlib.sha256', side_effect=sha256_for_test):
            with self.assertRaisesRegex(ValueError, '^reference window$'):
                check_pins(source, altered)
        truncated = image[:PC - 0x8000 + 9]
        with self.assertRaisesRegex(ValueError, '^reference window$'):
            check_window(truncated)

    def test_pin_mutations(self):
        source, image = SOURCE.read_bytes(), BIN.read_bytes()
        for s, b in ((source + b' ', image), (source, image[:-1]),
                     (source, bytes([image[0] ^ 1]) + image[1:])):
            with self.subTest(source_length=len(s), image_length=len(b)), self.assertRaises(ValueError):
                check_pins(s, b)


if __name__ == '__main__':
    unittest.main()
