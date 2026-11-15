#!/usr/bin/env python3
"""155d0 entry ordering, synthetic byte RAM; not a CPU or device model."""
import hashlib
import unittest
from pathlib import Path

BIN = (Path(__file__).resolve().parents[2] / 'firmware-downloads' /
       'legacy-options-2026-10-20' / 'BINs' / 'ID-2966-V4.1.60-decoded.bin')
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE = bytes.fromhex('411126c2938441059c4006c622c483c747004ac0a18b81cb')
MASK = 0xffffffff


def store(mem, address, value):
    for i in range(4):
        mem[(address + i) & MASK] = (value >> (8 * i)) & 255


def load(mem, address):
    return sum(mem[(address + i) & MASK] << (8 * i) for i in range(4))


def entry(mem, gp, sp, s1, ra, s0, s2):
    """Instruction-order projection; missing reads raise KeyError."""
    frame = (sp - 16) & MASK
    store(mem, frame + 4, s1)
    pointer = load(mem, (gp + 84) & MASK)
    store(mem, frame + 12, ra)
    store(mem, frame + 8, s0)
    byte = mem[(pointer + 4) & MASK]
    store(mem, frame, s2)
    return pointer, byte & 8, 0x155f6 if not byte & 8 else 0x155e8


class EntryOrder(unittest.TestCase):
    def test_original_bytes(self):
        image = BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), SHA)
        self.assertEqual(image[0x155d0 - 0x8000:0x155e8 - 0x8000], CODE)

    def test_flag_values(self):
        for byte in range(256):
            mem = {0x2004: byte}
            store(mem, 0x1054, 0x2000)
            pointer, flag, pc = entry(mem, 0x1000, 0x3010, 1, 2, 3, 4)
            self.assertEqual((pointer, flag, pc),
                             (0x2000, byte & 8, 0x155e8 if byte & 8 else 0x155f6))

    def test_saved_s1_can_replace_pointer_before_load(self):
        mem = {0x2004: 0, 0x3004: 8}
        store(mem, 0x1054, 0x2000)
        # sp-16+4 equals gp+84: first stack save overwrites the pointer.
        pointer, flag, pc = entry(mem, 0x1000, 0x1060, 0x3000, 2, 3, 4)
        self.assertEqual((pointer, flag, pc), (0x3000, 8, 0x155e8))

    def test_saved_ra_can_change_flag_before_byte_load(self):
        mem = {}
        store(mem, 0x1054, 0x3000)
        # sp-16+12 equals pointer+4: saved ra supplies byte tested.
        pointer, flag, pc = entry(mem, 0x1000, 0x3008, 1, 8, 3, 4)
        self.assertEqual((pointer, flag, pc), (0x3000, 8, 0x155e8))

    def test_saved_words_and_flag_aliases(self):
        mem = {0x2004: 8}
        store(mem, 0x1054, 0x2000)
        entry(mem, 0x1000, 0x4010, 0x11223344, 0x55667788, 0x99aabbcc, 0xddeeff00)
        self.assertEqual([load(mem, 0x4000 + x) for x in (4, 12, 8, 0)],
                         [0x11223344, 0x55667788, 0x99aabbcc, 0xddeeff00])
        # The s0 store precedes the flag read.
        mem = {}
        store(mem, 0x1054, 0x3000)
        self.assertEqual(entry(mem, 0x1000, 0x300c, 1, 2, 8, 4)[2], 0x155e8)
        # The s2 store follows the flag read and cannot change that decision.
        mem = {0x3004: 0}
        store(mem, 0x1054, 0x3000)
        self.assertEqual(entry(mem, 0x1000, 0x3014, 1, 2, 3, 8)[2], 0x155f6)
        self.assertEqual(load(mem, 0x3004), 8)

    def test_missing_byte_is_not_assumed_zero(self):
        mem = {}
        store(mem, 0x1054, 0x2000)
        with self.assertRaises(KeyError):
            entry(mem, 0x1000, 0x3010, 1, 2, 3, 4)
        self.assertEqual([load(mem, 0x3000 + x) for x in (4, 12, 8)], [1, 2, 3])
        self.assertNotIn(0x3000, mem)


if __name__ == '__main__':
    unittest.main()
