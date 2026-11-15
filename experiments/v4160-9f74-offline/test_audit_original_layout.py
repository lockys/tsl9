#!/usr/bin/env python3
import struct
import unittest
from pathlib import Path
import audit_original_layout as audit

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / 'experiments/tsl9-original-layout/build/rom-dependencies-v1'

class AuditTest(unittest.TestCase):
    def setUp(self):
        self.image = audit.refs.BIN.read_bytes()
        self.path = ARTIFACTS / 'c/NONLOADABLE-ORIGINAL-LAYOUT.elf'
        if not self.path.exists():
            self.skipTest('retained diagnostic ELF is not available')
        self.elf = self.path.read_bytes()

    def offsets(self, data):
        h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
        return [struct.unpack_from('<IIIIIIIIII', data, h[6] + i*40) for i in range(h[12])]

    def mutate_at_va(self, addr):
        b = bytearray(self.elf)
        found = [s for s in self.offsets(b) if s[2]&2 and s[1]!=8 and s[3] <= addr < s[3]+s[5]]
        self.assertEqual(len(found), 1)
        b[found[0][4]+addr-found[0][3]] ^= 1
        return bytes(b)

    def test_positive_and_scope(self):
        result = audit.audit(self.elf, self.image)
        self.assertEqual(result['present'], ['0xa356'])
        self.assertEqual(result['absent'], ['0xa0b8', '0xa1b8'])
        self.assertEqual(result['load_segments'], 0)

    def test_leaf_and_reference_mutations_rejected(self):
        for addr in (0x9f74, 0xa356):
            with self.subTest(addr=addr), self.assertRaises(ValueError):
                audit.audit(self.mutate_at_va(addr), self.image)

    def test_owner_value_mutation_rejected(self):
        b = bytearray(self.elf)
        sections = self.offsets(b)
        changes = 0
        for s in sections:
            if s[1] != 2:
                continue
            st = sections[s[6]]
            strings = b[st[4]:st[4]+st[5]]
            for pos in range(s[4], s[4]+s[5], 16):
                name, value, size, info, other, index = struct.unpack_from('<IIIBBH', b, pos)
                if audit.string(strings, name) == audit.OWNER:
                    struct.pack_into('<I', b, pos+4, value+2)
                    changes += 1
        self.assertEqual(changes, 1)
        with self.assertRaises(ValueError):
            audit.audit(bytes(b), self.image)

    def test_corrupt_header_and_image_rejected(self):
        b = bytearray(self.elf); b[4] = 2
        with self.assertRaises(ValueError):
            audit.audit(bytes(b), self.image)
        bad = bytearray(self.image); bad[0] ^= 1
        with self.assertRaises(ValueError):
            audit.audit(self.elf, bytes(bad))

if __name__ == '__main__':
    unittest.main()
