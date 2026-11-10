import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('scan', Path(__file__).with_name('scan.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = m.IMAGE.read_bytes()

    def test_fixed_candidates(self):
        p, s = m.verified(self.image)
        self.assertEqual([x[0] for x in p], [0xcefa, 0xcfe0, 0xd05c, 0xd0fa])
        self.assertEqual([(x[0], x[2]) for x in s], [(0xd000, 0xd010), (0xd05c, 0xd06e), (0xd0c4, 0xd0c8)])

    def test_hash_and_truncation(self):
        altered = bytearray(self.image)
        for addr in (0xd06e, 0xd0c8, 0xd0fa, 0x14056):
            altered[addr - m.BASE] ^= 1
            with self.assertRaises(ValueError): m.verified(altered)
            altered[addr - m.BASE] ^= 1
        with self.assertRaises(ValueError): m.verified(self.image[:-1])

    def test_mutated_store_and_pointer_are_detected_by_raw_scan(self):
        data = bytearray(self.image)
        data[0xd06e - m.BASE] ^= 1  # SB opcode
        self.assertNotIn((0xd05c, 0xd060, 0xd06e, 15, m.MODE, 1), m.scan(data)[1])
        data = bytearray(self.image)
        data[0xd0fe - m.BASE] ^= 1  # ADDI opcode
        self.assertNotIn((0xd0fa, 0xd0fe, 10, m.MODE - 1), m.scan(data)[0])

    def test_synthetic_pair_and_gap(self):
        data = bytearray(len(self.image))
        # lui a5,0x2000c; sb a0,-199(a5) => 0x2000bf39
        pair = bytes.fromhex('b7c70020a38ca7f2')
        start = 0x9000
        data[start-m.BASE:start-m.BASE+8] = pair
        self.assertIn((start, start, start+4, 15, m.MODE, 1), m.scan(data)[1])
        data[start-m.BASE:start-m.BASE+8] = bytes(8)
        start = 0x14054  # pair would cross excluded boundary
        data[start-m.BASE:start-m.BASE+8] = pair
        self.assertFalse(m.scan(data)[1])


if __name__ == '__main__': unittest.main()
