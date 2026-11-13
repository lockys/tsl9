"""Bounded synthetic immediate and base-register coverage for the raw scanner."""
import unittest

from scan import scan
from test_scan import pair


class MatrixTests(unittest.TestCase):
    def test_all_12bit_immediates_for_byte_accesses(self):
        for opcode in (3, 0x23):
            for encoded in range(4096):
                immediate = encoded if encoded < 2048 else encoded - 4096
                address = (0x10000 + immediate) & 0xffffffff
                hits = list(scan(pair(imm=encoded, opcode=opcode), base=0x10000, target=address))
                self.assertEqual([(h[5], h[6]) for h in hits], [(immediate, address)])

    def test_all_load_base_register_pairs(self):
        for rd in range(32):
            for rs1 in range(32):
                hits = list(scan(pair(rd=rd, rs1=rs1), base=0x1000, target=0x1000))
                self.assertEqual([hit[4] for hit in hits], [rd] if rd != 0 and rd == rs1 else [])

    def test_all_store_base_register_pairs(self):
        for rd in range(32):
            for rs1 in range(32):
                hits = list(scan(pair(rd=rd, rs1=rs1, opcode=0x23), base=0x1000, target=0x1000))
                self.assertEqual([hit[4] for hit in hits], [rd] if rd != 0 and rd == rs1 else [])


if __name__ == '__main__':
    unittest.main()
