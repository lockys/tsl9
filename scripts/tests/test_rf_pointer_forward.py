import runpy
import unittest
from pathlib import Path

scan = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scan-rf-pointer-forward.py'))['scan']


def word(w):
    return w.to_bytes(4, 'little')


def addi(rd, rs, imm):
    return word(((imm & 4095) << 20) | (rs << 15) | (rd << 7) | 0x13)


def sw(rs, base, imm):
    return word(((imm >> 5 & 127) << 25) | (rs << 20) | (base << 15) | (2 << 12) | ((imm & 31) << 7) | 0x23)


class ForwardTests(unittest.TestCase):
    def run_scan(self, data):
        return scan(data, 0x40000, [(0x40000, 0x40000 + len(data))])['hits']

    def test_nonadjacent_alias(self):
        data = word(0x200032b7) + addi(6, 5, 0x500) + addi(7, 0, 2) + sw(7, 6, 0x38)
        self.assertTrue(any(h['start'] == '0x40000' and h['store_pc'] == '0x4000c' for h in self.run_scan(data)))

    def test_kill_and_branch(self):
        prefix = word(0x200032b7) + addi(6, 5, 0x500)
        for barrier in (word(0xffffffff), word(0x00000063), addi(6, 0, 0)):
            self.assertFalse(self.run_scan(prefix + barrier + sw(7, 6, 0x38)))

    def test_budget(self):
        data = word(0x200032b7) + addi(6, 5, 0x500) + sw(7, 6, 0x38)
        self.assertFalse(scan(data, 0x40000, [(0x40000, 0x4000c)], 2)['hits'])


if __name__ == '__main__':
    unittest.main()
