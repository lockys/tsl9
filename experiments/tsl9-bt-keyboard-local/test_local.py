"""Static byte-bound checks; models below do not execute firmware."""
import hashlib
from pathlib import Path
import unittest

APP = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS = {
    0x1238a: '03558400832a0a008329c400034aa400050542055286ce854181ef50bffe35e1',
    0x11cc8: '83270b002d46d6851795000013054590829731c5a1476318fa0e83c719006393077283c73900639f077083c74900639b077083c759006397077083c769006393077083c77900639f076e83c7090003c72900a207ba970347190042070dbf',
    0x11c56: 'ba97034709006207ba976386077a97a6ff1f83c6f63617a7ff1f1307c73563990650',
    0x11dce: '95476313fa04',
    0x1a5d4: '4254204b6579426f61726400',
}

def check(data):
    for pc, expected in WINDOWS.items():
        raw = bytes.fromhex(expected)
        if data[pc - 0x8000:pc - 0x8000 + len(raw)] != raw:
            raise ValueError(hex(pc))

def branch_target(data, pc):
    w = int.from_bytes(data[pc-0x8000:pc-0x8000+4], 'little')
    assert w & 0x7f == 0x63
    imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    return pc + (imm - 8192 if imm & 4096 else imm)

def compressed_jump(data, pc):
    raw = data[pc-0x8000:pc-0x8000+2]
    if len(raw) != 2:
        raise ValueError('truncated jump')
    w = int.from_bytes(raw, 'little')
    if w & 0xe003 != 0xa001:
        raise ValueError('not c.j')
    imm = ((w >> 12) & 1) << 11 | ((w >> 11) & 1) << 4 | ((w >> 9) & 3) << 8 | ((w >> 8) & 1) << 10 | ((w >> 7) & 1) << 6 | ((w >> 6) & 1) << 7 | ((w >> 3) & 7) << 1 | ((w >> 2) & 1) << 5
    return pc + (imm - 4096 if imm & 2048 else imm)

def eight_byte_path(payload, source):
    if len(payload) < 8 or len(source) < 2:
        raise ValueError('readable bytes required')
    if any(payload[i] for i in (1, 3, 4, 5, 6, 7)):
        return None
    return (source[0] << 24) | (source[1] << 16) | (payload[0] << 8) | payload[2]

class LocalTest(unittest.TestCase):
    def test_identity_and_windows(self):
        data = APP.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), SHA)
        check(data)
        for pc in WINDOWS:
            mutated = bytearray(data); mutated[pc - 0x8000] ^= 1
            with self.subTest(pc=hex(pc)), self.assertRaises(ValueError): check(mutated)
        with self.assertRaises(ValueError): check(data[:0x11d26-0x8000])

    def test_direct_edges(self):
        data = APP.read_bytes()
        for pc in (0x11ce6, 0x11cee, 0x11cf6, 0x11cfe, 0x11d06, 0x11d0e, 0x11c60):
            self.assertEqual(branch_target(data, pc), 0x1240c)
        self.assertEqual(branch_target(data, 0x11cde), 0x11dce)
        self.assertEqual(branch_target(data, 0x11c74), 0x12186)
        self.assertEqual(branch_target(data, 0x11dd0), 0x11e16)
        self.assertEqual(compressed_jump(data, 0x11d24), 0x11c56)
        with self.assertRaises(ValueError): compressed_jump(data, 0x11c60)

    def test_conditional_dataflow_model(self):
        self.assertEqual(eight_byte_path(bytes([0x12,0,0x34,0,0,0,0,0]), bytes([0xab,0xcd])), 0xabcd1234)
        self.assertEqual(eight_byte_path(bytes(8), bytes(4)), 0)
        for i in (1, 3, 4, 5, 6, 7):
            p = bytearray(8); p[i] = 1
            self.assertIsNone(eight_byte_path(p, bytes(4)))
        with self.assertRaises(ValueError): eight_byte_path(bytes(7), bytes(2))
        with self.assertRaises(ValueError): eight_byte_path(bytes(8), bytes(1))

if __name__ == '__main__': unittest.main()
