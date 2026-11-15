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
        self.elf = self.path.read_bytes() if self.path.exists() else None

    def require_older_elf(self):
        if self.elf is None:
            self.skipTest('retained diagnostic ELF is not available')

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
        self.require_older_elf()
        result = audit.audit(self.elf, self.image)
        self.assertEqual(result['present'], ['0xa356'])
        self.assertEqual(result['absent'], ['0xa0b8', '0xa1b8'])
        self.assertEqual(result['load_segments'], 0)

    def test_leaf_and_reference_mutations_rejected(self):
        self.require_older_elf()
        for addr in (0x9f74, 0xa356):
            with self.subTest(addr=addr), self.assertRaises(ValueError):
                audit.audit(self.mutate_at_va(addr), self.image)

    def test_owner_value_mutation_rejected(self):
        self.require_older_elf()
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

    def test_partial_section_overlaps_and_absent_sites_fail_closed(self):
        self.require_older_elf()
        for addr in (0x9f75, 0xa0b8, 0xa1b8, 0xa356):
            altered = bytearray(self.elf)
            header = struct.unpack_from('<16sHHIIIIIHHHHHH', altered)
            # Change the unused null section into a 2-byte allocated PROGBITS
            # interval: it intersects a complete leaf/site or a supposedly absent site.
            struct.pack_into('<IIIIIIIIII', altered, header[6], 0, 1, 2, addr, 0, 2, 0, 0, 1, 0)
            with self.subTest(addr=addr), self.assertRaises(ValueError):
                audit.audit(bytes(altered), self.image)

    def test_non_executable_and_invalid_section_types_rejected(self):
        self.require_older_elf()
        sections = self.offsets(self.elf)
        header = struct.unpack_from('<16sHHIIIIIHHHHHH', self.elf)
        shoff = header[6]
        for addr in (0x9f74, 0xa356):
            indices = [i for i, s in enumerate(sections) if s[2]&2 and s[3] <= addr < s[3]+s[5]]
            self.assertEqual(len(indices), 1)
            for field, value in ((4, 0), (8, sections[indices[0]][2] & ~4)):
                altered = bytearray(self.elf)
                struct.pack_into('<I', altered, shoff+indices[0]*40+field, value)
                with self.subTest(addr=addr, field=field), self.assertRaises(ValueError):
                    audit.audit(bytes(altered), self.image)
        symtabs = [s for s in sections if s[1] == 2]
        self.assertTrue(symtabs)
        for s in symtabs:
            altered = bytearray(self.elf)
            struct.pack_into('<I', altered, shoff+s[6]*40+4, 0)
            with self.subTest(string_index=s[6]), self.assertRaises(ValueError):
                audit.audit(bytes(altered), self.image)

    def test_safe_gap_all_references_and_mutations(self):
        base = ROOT / 'experiments/tsl9-original-layout/build/safe-gap-v2'
        paths = [base / lang / 'NONLOADABLE-ORIGINAL-LAYOUT.elf' for lang in ('c', 'cpp')]
        if not all(path.exists() for path in paths):
            self.skipTest('safe-gap diagnostic ELFs are not available')
        for path in paths:
            data = path.read_bytes()
            self.assertEqual(audit.audit(data, self.image, (0xa0b8, 0xa1b8, 0xa356), ())['present'],
                             ['0xa0b8', '0xa1b8', '0xa356'])
            with self.assertRaises(ValueError):
                audit.audit(data, self.image)  # fail closed for a different layout
            for addr in (0xa0b8, 0xa1b8, 0xa356):
                altered = bytearray(data)
                matches = [s for s in self.offsets(data) if s[2]&2 and s[1]!=8 and s[3] <= addr < s[3]+s[5]]
                self.assertEqual(len(matches), 1)
                s = matches[0]
                altered[s[4]+addr-s[3]] ^= 1
                with self.subTest(path=path, addr=addr), self.assertRaises(ValueError):
                    audit.audit(bytes(altered), self.image, (0xa0b8, 0xa1b8, 0xa356), ())

    def test_corrupt_header_and_image_rejected(self):
        self.require_older_elf()
        b = bytearray(self.elf); b[4] = 2
        with self.assertRaises(ValueError):
            audit.audit(bytes(b), self.image)
        bad = bytearray(self.image); bad[0] ^= 1
        with self.assertRaises(ValueError):
            audit.audit(self.elf, bytes(bad))

if __name__ == '__main__':
    unittest.main()
