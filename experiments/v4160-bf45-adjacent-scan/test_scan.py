import hashlib
import unittest
from unittest.mock import patch

import scan as scanner
from scan import BASE, REFERENCE, SHA256, TARGET, scan


def pair(upper=0, imm=0, rd=1, rs1=1, opcode=3, funct3=0):
    auipc = (upper & 0xfffff000) | (rd << 7) | 0x17
    imm &= 0xfff
    if opcode == 0x23:
        access = ((imm >> 5) << 25) | (rs1 << 15) | (funct3 << 12) | ((imm & 31) << 7) | opcode
    else:
        access = (imm << 20) | (rs1 << 15) | (funct3 << 12) | opcode
    return auipc.to_bytes(4, "little") + access.to_bytes(4, "little")


class ScanTests(unittest.TestCase):
    def test_width_and_unsigned_loads(self):
        for opcode, funct3, width in ((3, 0, 1), (3, 4, 1), (3, 1, 2), (3, 5, 2),
                                      (3, 2, 4), (0x23, 0, 1), (0x23, 1, 2), (0x23, 2, 4)):
            with self.subTest(opcode=opcode, funct3=funct3):
                data = pair(opcode=opcode, funct3=funct3)
                for delta in range(width):
                    self.assertEqual(len(list(scan(data, base=0x1000, target=0x1000 + delta))), 1)
                self.assertEqual(list(scan(data, base=0x1000, target=0x1000 + width)), [])
                self.assertEqual(list(scan(data, base=0x1000, target=0x0fff)), [])

    def test_signed_immediates_and_wrap(self):
        hit = list(scan(pair(upper=0xfffff000, imm=-1, funct3=2), base=0x1000, target=0))
        self.assertEqual((hit[0][5], hit[0][6], hit[0][7]), (-1, 0xffffffff, 4))
        hit = list(scan(pair(imm=-2, opcode=0x23, funct3=1), base=1, target=0))
        self.assertEqual((hit[0][5], hit[0][6]), (-2, 0xffffffff))
        for opcode in (3, 0x23):
            for immediate in (2047, -2048):
                with self.subTest(opcode=opcode, immediate=immediate):
                    address = (0x10000 + immediate) & 0xffffffff
                    hits = list(scan(pair(imm=immediate, opcode=opcode), base=0x10000, target=address))
                    self.assertEqual([(h[5], h[6]) for h in hits], [(immediate, address)])

    def test_negatives_and_last_halfword_offset(self):
        self.assertEqual(list(scan(pair(rd=0, rs1=0), base=0, target=0)), [])
        self.assertEqual(list(scan(pair(rd=1, rs1=2), base=0, target=0)), [])
        self.assertEqual(list(scan(pair(opcode=0x13), base=0, target=0)), [])
        self.assertEqual(list(scan(pair(funct3=3), base=0, target=0)), [])
        self.assertEqual(list(scan(pair(opcode=0x23, funct3=4), base=0, target=0)), [])
        invalid_first = bytearray(pair()); invalid_first[0] = 0x13
        self.assertEqual(list(scan(invalid_first, base=0, target=0)), [])
        for length in range(8):
            self.assertEqual(list(scan(pair()[:length], base=0, target=0)), [])
        self.assertEqual(list(scan(b'\x00\x00' + pair(), base=0, target=2))[0][0], 2)

    def test_multiple_halfword_offsets_and_odd_negative(self):
        data = pair(imm=0) + b'\x00\x00' + pair(imm=-10) + b'\x00\x00' + pair(imm=-20)
        self.assertEqual([hit[0] for hit in scan(data, base=0x1000, target=0x1000)], [0, 10, 20])
        self.assertEqual(list(scan(b'\x00' + pair(), base=0x1000, target=0x1001)), [])

    def test_cli_rejects_changed_and_missing_reference(self):
        data = REFERENCE.read_bytes()
        for changed in (data[:-1], bytes([data[0] ^ 1]) + data[1:]):
            with self.subTest(length=len(changed)):
                with patch.object(scanner.Path, 'read_bytes', return_value=changed), patch('builtins.print') as output:
                    with self.assertRaisesRegex(ValueError, 'reference pin mismatch'):
                        scanner.main()
                    output.assert_not_called()
        with patch.object(scanner.Path, 'read_bytes', side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                scanner.main()

    def test_pinned_reference(self):
        data = REFERENCE.read_bytes()
        self.assertEqual(len(data), 76800)
        self.assertEqual(hashlib.sha256(data).hexdigest(), SHA256)
        results = list(scan(data))
        self.assertEqual(len(results), 3)
        hits = {hit[1]: hit for hit in results}
        self.assertEqual(set(hits), {0xd000, 0xd00c, 0xd048})
        for pc, raw, mnemonic, rd, immediate in (
            (0xd000, '97f7ff1f83c757f4', 'lbu', 15, -187),
            (0xd00c, '97f7ff1fa38ca7f2', 'sb', 15, -199),
            (0xd048, '17f5ff1f0345d5ef', 'lbu', 10, -259),
        ):
            hit = hits[pc]
            self.assertEqual((hit[0], hit[2].hex(), hit[3], hit[4], hit[5], hit[6], hit[7]),
                             (pc - BASE, raw, mnemonic, rd, immediate, TARGET, 1))


if __name__ == '__main__':
    unittest.main()
