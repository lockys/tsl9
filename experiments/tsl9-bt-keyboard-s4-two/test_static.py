"""Offline byte-bound checks and a deliberately limited branch model."""
import hashlib
from pathlib import Path
import unittest

APP = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOWS = {
    0x11cc8: '83270b002d46d6851795000013054590829731c5a1476318fa0e',
    0x11dce: '95476313fa04',
    0x11e16: '8947631afa5e03c619006366ca5e834729008346190003c70900a207c2063297b6971377f70f29bd',
    0x11c56: 'ba97034709006207ba976386077a97a6ff1f83c6f63617a7ff1f1307c73563990650054797a6ff1fa38ce63417a7ff1f2325f73497a7ff1f2393073497a7ff1f23800734b7070400bc4f1306001e854517a5ff1f034525328297',
    0x1a5d4: '4254204b6579426f61726400',
}

def check(data):
    for pc, h in WINDOWS.items():
        b = bytes.fromhex(h)
        if data[pc-0x8000:pc-0x8000+len(b)] != b:
            raise ValueError(hex(pc))

def branch(data, pc):
    raw = data[pc-0x8000:pc-0x8000+4]
    if len(raw) != 4: raise ValueError('truncated')
    w = int.from_bytes(raw, 'little')
    if w & 127 != 99: raise ValueError('not branch')
    v = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
    return pc + (v - 8192 if v & 4096 else v)

def jump(data, pc):
    raw = data[pc-0x8000:pc-0x8000+2]
    if len(raw) != 2: raise ValueError('truncated')
    w = int.from_bytes(raw, 'little')
    if w & 0xe003 != 0xa001: raise ValueError('not c.j')
    v = ((w >> 12) & 1) << 11 | ((w >> 11) & 1) << 4 | ((w >> 9) & 3) << 8 | ((w >> 8) & 1) << 10 | ((w >> 7) & 1) << 6 | ((w >> 6) & 1) << 7 | ((w >> 3) & 7) << 1 | ((w >> 2) & 1) << 5
    return pc + (v - 4096 if v & 2048 else v)

def model(s4, payload, source, flag):
    if s4 != 2: return ('exit', None)
    if len(payload) < 2: raise ValueError('payload')
    if payload[1] > 2: return ('exit', None)
    if len(source) < 3: raise ValueError('source')
    value = source[0] << 24 | source[1] << 16 | source[2] << 8 | ((payload[0] + payload[1]) & 255)
    if not value: return ('exit', 0)
    return ('0x12186' if flag else '0x11c78', value)

class StaticTests(unittest.TestCase):
    def test_identity_and_negative_mutations(self):
        data = APP.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), SHA)
        check(data)
        for pc in WINDOWS:
            altered = bytearray(data); altered[pc-0x8000] ^= 1
            with self.subTest(pc=hex(pc)), self.assertRaises(ValueError): check(altered)
        with self.assertRaises(ValueError): check(data[:0x11e30-0x8000])

    def test_edges(self):
        data = APP.read_bytes()
        for pc, target in [(0x11cde,0x11dce),(0x11dd0,0x11e16),(0x11e18,0x1240c),(0x11e20,0x1240c),(0x11c60,0x1240c),(0x11c74,0x12186)]:
            self.assertEqual(branch(data, pc), target)
        self.assertEqual(jump(data, 0x11e3c), 0x11c56)
        with self.assertRaises(ValueError): jump(data, 0x11e20)

    def test_model(self):
        for n in range(3):
            self.assertEqual(model(2, bytes([255,n]), bytes([1,2,3]), 0), ('0x11c78', 0x01020300 | ((255+n)&255)))
        self.assertEqual(model(2, bytes([255,2]), bytes([1,2,3]), 1), ('0x12186',0x01020301))
        self.assertEqual(model(2, bytes([254,2]), bytes(3), 0), ('exit',0))
        self.assertEqual(model(2, bytes([0,3]), b'', 0), ('exit',None))
        self.assertEqual(model(3, b'', b'', 0), ('exit',None))
        with self.assertRaises(ValueError): model(2, b'\0', bytes(3), 0)
        with self.assertRaises(ValueError): model(2, bytes(2), bytes(2), 0)

if __name__ == '__main__': unittest.main()
