import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('scan', Path(__file__).with_name('scan.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def u(op, rd, imm):
    return (imm & 0xfffff000) | rd << 7 | op


def s(rs1, rs2, imm, f=0, op=0x23):
    imm &= 0xfff
    return (imm >> 5) << 25 | rs2 << 20 | rs1 << 15 | f << 12 | (imm & 31) << 7 | op


def pair(a, b):
    return a.to_bytes(4, 'little') + b.to_bytes(4, 'little')


class Tests(unittest.TestCase):
    def test_image_and_sites(self):
        data = m.IMAGE.read_bytes()
        result = m.report(data)
        self.assertTrue(all(result['known_store_sites_present'].values()))
        self.assertEqual([(h['materializer'], h['store'], h['source_register'], h['width'], h['address']) for h in result['candidates']],
                         [(0xa870, 0xa874, 0, 1, m.TARGET), (0xa8b8, 0xa8bc, 15, 1, m.TARGET),
                          (0xa8dc, 0xa8e0, 15, 1, m.TARGET), (0xa90c, 0xa910, 15, 1, m.TARGET)])
        self.assertTrue(result['local_scan_complete'])
        self.assertFalse(result['global_writer_complete'])
        for bad in (data[:-1], data + b'\0', bytes([data[0] ^ 1]) + data[1:]):
            with self.assertRaises(ValueError):
                m.report(bad)

    def test_exact_fields_and_overlap(self):
        # BASE + 0x20004000 - 0x12b = BED5
        a = u(0x17, 14, 0x20004000)
        b = s(14, 15, -0x12b)
        hit = m.scan(pair(a, b))
        self.assertEqual(hit, [dict(kind='auipc', encoding='standard', materializer=0x8000,
                                    store=0x8004, base_register=14, source_register=15,
                                    immediate=-0x12b, width=1, address=m.TARGET)])
        for mutant in (u(0x13, 14, 0x20004000), u(0x17, 0, 0x20004000),
                       u(0x17, 13, 0x20004000), u(0x17, 14, 0x20005000)):
            self.assertEqual(m.scan(pair(mutant, b)), [])
        for mutant in (s(13,15,-0x12b), s(14,15,-0x12a), s(14,15,-0x12b,3), s(14,15,-0x12b,0,0x03)):
            self.assertEqual(m.scan(pair(a, mutant)), [])
        self.assertEqual(m.scan(pair(a, s(14, 3, -0x12c, 1)))[0]['address'], m.TARGET - 1)
        self.assertEqual(m.scan(pair(a, s(14, 3, -0x12e, 2)))[0]['width'], 4)
        self.assertEqual(m.scan(pair(a, s(14, 3, -0x12f, 2))), [])
        self.assertEqual(m.scan(pair(a, s(14, 3, -0x12b)))[0]['source_register'], 3)

    def test_absolute_and_bounds(self):
        a = u(0x37, 10, 0x2000c000)
        b = s(10, 4, -0x12b)
        self.assertEqual(m.scan(pair(a, b))[0]['kind'], 'lui')
        self.assertEqual(m.scan(pair(a, b)[:-1]), [])
        self.assertEqual(m.scan(b'\0\0' + pair(a, b))[0]['materializer'], 0x8002)
        self.assertEqual(m.scan(pair(a, s(0, 4, -1))), [])
        self.assertEqual(m.store32(s(0, 4, -1)), (0, 4, -1, 1))
        self.assertTrue(m.overlaps(m.TARGET - 3, 4))
        self.assertFalse(m.overlaps(m.TARGET - 4, 4))

    def test_compressed_fields(self):
        # c.sw x9, 4(x10)
        h = 6 << 13 | 2 << 7 | 1 << 6 | 1 << 2
        self.assertEqual(m.store16(h), (10, 9, 4, 4))
        self.assertIsNone(m.store16(h ^ (1 << 13)))
        self.assertIsNone(m.store16(h | 1))
        # LUI x10, 0x2000c000 + 0x40 = 0x2000c040 (negative example)
        self.assertEqual(m.scan(u(0x37, 10, 0x2000c000).to_bytes(4, 'little') + h.to_bytes(2, 'little')), [])
        # AUIPC at 0x8e94 + 0x20003000 + 0x40 = BED4, overlapping BED5.
        h64 = 6 << 13 | 2 << 7 | 1 << 5 | 1 << 2
        image = bytes(0xe94) + u(0x17, 10, 0x20003000).to_bytes(4, 'little') + h64.to_bytes(2, 'little')
        hit = m.scan(image)
        self.assertEqual(len(hit), 1)
        self.assertEqual((hit[0]['encoding'], hit[0]['address'], hit[0]['width']), ('compressed', m.TARGET - 1, 4))
        self.assertEqual(m.scan(image[:-1]), [])


if __name__ == '__main__':
    unittest.main()
