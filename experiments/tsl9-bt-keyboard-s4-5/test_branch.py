"""Offline image checks and a bounded, non-executing branch model."""
import hashlib
from pathlib import Path
import unittest

APP = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
WINDOW = bytes.fromhex('95476313fa0483c60900638a066283c719006396076283c729006392076283c73900639e076083c74900639a07608347290003471900a2074207ba97b697034709006207ba9781bd')

def check(b):
    if len(b) != 76800 or hashlib.sha256(b).hexdigest() != SHA:
        raise ValueError('image identity')
    check_window(b)

def check_window(b):
    if b[0x11dce-0x8000:0x11e16-0x8000] != WINDOW:
        raise ValueError('branch bytes')

def branch(b, pc):
    w = int.from_bytes(b[pc-0x8000:pc-0x8000+4], 'little')
    if w & 127 != 0x63:
        raise ValueError('not branch')
    imm = (w >> 31) << 12 | ((w >> 7) & 1) << 11 | ((w >> 25) & 63) << 5 | ((w >> 8) & 15) << 1
    return pc + (imm - 8192 if imm & 4096 else imm), (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31

def jump(b, pc):
    w = int.from_bytes(b[pc-0x8000:pc-0x8000+2], 'little')
    if w & 0xe003 != 0xa001: raise ValueError('not c.j')
    n = ((w >> 12) & 1) << 11 | ((w >> 11) & 1) << 4 | ((w >> 9) & 3) << 8 | ((w >> 8) & 1) << 10 | ((w >> 7) & 1) << 6 | ((w >> 6) & 1) << 7 | ((w >> 3) & 7) << 1 | ((w >> 2) & 1) << 5
    return pc + (n - 4096 if n & 2048 else n)

def model(s4, p, q):
    if s4 != 5: return (0x11e16, None)
    if len(p) < 5: raise ValueError('s3')
    if p[0] == 0 or any(p[1:5]): return (0x1240c, None)
    if len(q) < 3: raise ValueError('s2')
    return (0x11c64, q[0]<<24 | q[1]<<16 | q[2]<<8 | p[0])

class BranchTests(unittest.TestCase):
    def test_image_and_mutations(self):
        b = APP.read_bytes(); check(b)
        for pc in (0x11dce, 0x11dd8, 0x11df8, 0x11e14):
            c = bytearray(b); c[pc-0x8000] ^= 1
            with self.subTest(pc=pc), self.assertRaises(ValueError): check(c)
            with self.subTest(window_pc=pc), self.assertRaises(ValueError): check_window(c)
        with self.assertRaises(ValueError): check(b[:-1])
        self.assertNotEqual(b[0x11dce-0x8000:0x11e16-0x8000], WINDOW[:-1] + bytes([WINDOW[-1] ^ 1]))
    def test_edges(self):
        b = APP.read_bytes(); check(b)
        self.assertEqual(branch(b, 0x11dd0), (0x11e16, 1, 20, 15))
        self.assertEqual(branch(b, 0x11dd8), (0x1240c, 0, 13, 0))
        for pc in (0x11de0, 0x11de8, 0x11df0, 0x11df8):
            self.assertEqual(branch(b, pc), (0x1240c, 1, 15, 0))
        self.assertEqual(jump(b, 0x11e14), 0x11c64)
    def test_model_positive_negative(self):
        p = bytearray([0x12,0,0,0,0]); q = bytes([0xab,0xcd,0xef])
        self.assertEqual(model(5,p,q),(0x11c64,0xabcdef12))
        self.assertEqual(model(5,bytes([1,0,0,0,0]),bytes(3)),(0x11c64,1))
        self.assertEqual(model(4,b'',b''),(0x11e16,None))
        self.assertEqual(model(5,bytes(5),b''),(0x1240c,None))
        for i in range(1,5):
            t = bytearray(p); t[i] = 1
            with self.subTest(i=i): self.assertEqual(model(5,t,b''),(0x1240c,None))
        with self.assertRaises(ValueError): model(5,bytes(4),q)
        with self.assertRaises(ValueError): model(5,p,bytes(2))

if __name__ == '__main__': unittest.main()
