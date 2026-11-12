import unittest

import survey


def jal(offset, rd):
    u = offset & 0x1fffff
    return (0x6f | rd << 7 | ((u >> 20) & 1) << 31 |
            ((u >> 1) & 0x3ff) << 21 | ((u >> 11) & 1) << 20 |
            ((u >> 12) & 0xff) << 12)


def cj(offset, subtype):
    u = offset & 0xfff
    return (subtype << 13 | 1 | ((u >> 11) & 1) << 12 |
            ((u >> 4) & 1) << 11 | ((u >> 8) & 3) << 9 |
            ((u >> 10) & 1) << 8 | ((u >> 6) & 1) << 7 |
            ((u >> 7) & 1) << 6 | ((u >> 1) & 7) << 3 |
            ((u >> 5) & 1) << 2)


# Exact image bytes and destinations independently checked with r2; not generated
# by jal() or by scan(). Offsets are target minus instruction PC.
R2_JAL_FIXTURES = (
    (0x102e6, bytes.fromhex('ef a0 bf dc'), 1, -21046, 0xb0b0),
    (0x16272, bytes.fromhex('6f 40 ff e3'), 0, -45506, 0xb0b0),
    (0x16282, bytes.fromhex('6f 40 ff e2'), 0, -45522, 0xb0b0),
    (0x16292, bytes.fromhex('6f 40 ff e1'), 0, -45538, 0xb0b0),
)


class SurveyTests(unittest.TestCase):
    def test_r2_jal_literals(self):
        for pc, raw, rd, offset, target in R2_JAL_FIXTURES:
            with self.subTest(pc=hex(pc)):
                self.assertEqual(survey.decode_jal(int.from_bytes(raw, 'little')), (rd, offset))
                self.assertEqual(pc + offset, target)
                self.assertEqual(list(survey.scan(raw, pc, target)),
                                 [(pc, raw.hex(), f'JAL rd=x{rd}', offset)])

    def test_scan_rejects_odd_base(self):
        for data in (b'', b'\x00', b'\x00\x00', b'\x00\x00\x00\x00'):
            with self.subTest(data=data), self.assertRaisesRegex(ValueError, 'aligned'):
                list(survey.scan(data, 0x1001, 0x1000))

    def test_all_c_offsets_and_subtypes(self):
        for offset in range(-2048, 2048, 2):
            for subtype, name in ((1, 'C.JAL'), (5, 'C.J')):
                self.assertEqual(survey.decode_c(cj(offset, subtype)), (name, offset))

    def test_all_jal_offsets(self):
        for offset in range(-1048576, 1048576, 2):
            rd = (offset // 2) & 31
            self.assertEqual(survey.decode_jal(jal(offset, rd)), (rd, offset))
        for rd in range(32):
            self.assertEqual(survey.decode_jal(jal(-2, rd)), (rd, -2))

    def test_mutations(self):
        for offset in (-2048, -2, 0, 2, 2046):
            for subtype in (1, 5):
                word = cj(offset, subtype)
                for bit in range(16):
                    mutated = word ^ (1 << bit)
                    decoded = survey.decode_c(mutated)
                    if bit in (0, 1, 13, 14):
                        self.assertIsNone(decoded)
                    elif bit == 15:
                        self.assertEqual(decoded, ('C.J' if subtype == 1 else 'C.JAL', offset))
                    else:
                        self.assertNotEqual(decoded[1], offset)
        for offset in (-1048576, -2, 0, 2, 1048574):
            word = jal(offset, 1)
            for bit in range(32):
                decoded = survey.decode_jal(word ^ (1 << bit))
                if bit < 7:
                    self.assertIsNone(decoded)
                elif bit < 12:
                    self.assertEqual(decoded, (1 ^ (1 << (bit - 7)), offset))
                else:
                    self.assertNotEqual(decoded[1], offset)

    def test_scan_overlap_and_edges(self):
        data = b'\xff\xff' + jal(-2, 0).to_bytes(4, 'little') + cj(-6, 1).to_bytes(2, 'little')
        hits = list(survey.scan(data, 0x1000, 0x1000))
        self.assertEqual(hits, [(0x1002, jal(-2, 0).to_bytes(4, 'little').hex(), 'JAL rd=x0', -2),
                                (0x1006, cj(-6, 1).to_bytes(2, 'little').hex(), 'C.JAL', -6)])
        self.assertEqual(list(survey.scan(jal(0, 1).to_bytes(4, 'little')[:2], 0x1000, 0x1000)), [])
        # A JAL can begin in the upper half of a preceding 32-bit pattern.
        raw = b'\x13\x00' + jal(0, 5).to_bytes(4, 'little')
        self.assertEqual(list(survey.scan(raw, 0x1000, 0x1002))[0][2], 'JAL rd=x5')

    def test_image_and_mutations(self):
        data = survey.IMAGE.read_bytes()
        survey.validate(data)
        self.assertEqual(list(survey.scan(data)), [
            (0x102e6, 'efa0bfdc', 'JAL rd=x1', -21046),
            (0x16272, '6f40ffe3', 'JAL rd=x0', -45506),
            (0x16282, '6f40ffe2', 'JAL rd=x0', -45522),
            (0x16292, '6f40ffe1', 'JAL rd=x0', -45538),
        ])
        for pc, raw, _, _, _ in R2_JAL_FIXTURES:
            self.assertEqual(data[pc - survey.BASE:pc - survey.BASE + len(raw)], raw)
        for pos in range(survey.TARGET - survey.BASE, survey.TARGET - survey.BASE + len(survey.WINDOW)):
            changed = bytearray(data)
            changed[pos] ^= 1
            with self.assertRaises(ValueError):
                survey.validate(changed)
        for changed in (data[:-1], bytes([data[0] ^ 1]) + data[1:]):
            with self.assertRaises(ValueError):
                survey.validate(changed)


if __name__ == '__main__':
    unittest.main()
