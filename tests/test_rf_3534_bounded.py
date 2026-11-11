import runpy
import unittest
from pathlib import Path

m = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/check-rf-3534-bounded.py'))


class Scan3534(unittest.TestCase):
    def test_pinned_result_and_mutations(self):
        image = m['direct']['IMAGE'].read_bytes()
        header = m['alias']['HEADER'].read_bytes()
        result = m['verify'](image, header)
        self.assertEqual([(x['access_pc'], x['kind']) for x in result['adjacent']],
                         [('0x53a00', 'load'), ('0x57cf6', 'load')])
        self.assertEqual(result['forward']['hits'], [])
        for pos in (0, 0x53a00 - 0x40000, len(image) - 1):
            changed = bytearray(image)
            changed[pos] ^= 1
            with self.assertRaises(ValueError):
                m['verify'](changed, header)
        with self.assertRaises(ValueError):
            m['verify'](image[:-1], header)
        with self.assertRaises(ValueError):
            m['verify'](image, header + b'x')

    def test_synthetic_store_and_negative(self):
        lui = (0x20003737).to_bytes(4, 'little')
        imm = 0x534
        sw = ((imm >> 5) << 25 | 15 << 20 | 14 << 15 | 2 << 12 | (imm & 31) << 7 | 0x23).to_bytes(4, 'little')
        scan = m['direct']['scan']
        self.assertEqual(scan(lui + sw)[0]['kind'], 'store')
        self.assertEqual(scan(lui + sw[:-1]), [])
        self.assertEqual(scan((0x20004737).to_bytes(4, 'little') + sw), [])
        f = m['forward']['scan']
        self.assertTrue(f(lui + sw, 0x40000, [(0x40000, 0x40008)])['hits'])
        self.assertEqual(f(lui + sw, 0x40000, [(0x40000, 0x40004)])['hits'], [])


if __name__ == '__main__':
    unittest.main()
