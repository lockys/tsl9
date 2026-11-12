import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('survey', Path(__file__).with_name('scan.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def store(offset, width=1, base=3, source=8, opcode=0x23):
    immediate = offset & 0xfff
    f = {1: 0, 2: 1, 4: 2}[width]
    word = ((immediate >> 5) << 25) | (source << 20) | (base << 15) | (f << 12) | ((immediate & 31) << 7) | opcode
    return word.to_bytes(4, 'little')


class SurveyTest(unittest.TestCase):
    def test_pinned_image(self):
        data = m.IMAGE.read_bytes()
        report = m.report(data)
        self.assertEqual(report['candidates'], [{'pc': 0x102b2, 'bytes': '23988104', 'source_register': 8, 'offset': 80, 'width': 2}])
        self.assertFalse(report['global_writers_complete'])
        for bad in (data[:-1], data + b'\0', bytes([data[0] ^ 1]) + data[1:]):
            with self.assertRaises(ValueError):
                m.report(bad)

    def test_width_boundaries(self):
        for width in (1, 2, 4):
            for offset in range(0x49, 0x55):
                with self.subTest(width=width, offset=offset):
                    expected = offset <= 0x51 and offset + width - 1 >= 0x50
                    self.assertEqual(bool(m.candidates(store(offset, width))), expected)
        self.assertFalse(m.candidates(store(-1, 4)))

    def test_raw_boundaries_and_mutations(self):
        example = bytes.fromhex('23988104')
        hits = m.candidates(example + b'\x00\x00' + example)
        self.assertEqual([h['pc'] for h in hits], [0x8000, 0x8006])
        self.assertFalse(m.candidates(store(-2048, 4)))
        self.assertFalse(m.candidates(store(2047, 4)))
        for f in range(3, 8):
            word = int.from_bytes(example, 'little')
            word = (word & ~(7 << 12)) | (f << 12)
            self.assertFalse(m.candidates(word.to_bytes(4, 'little')))
        word = int.from_bytes(example, 'little')
        accepted = {7, 12, 20, 21, 22, 23, 24}
        for bit in range(32):
            with self.subTest(bit=bit):
                mutated = (word ^ (1 << bit)).to_bytes(4, 'little')
                self.assertEqual(bool(m.candidates(mutated)), bit in accepted)

    def test_fields_and_alignment(self):
        self.assertFalse(m.candidates(store(80, 2, base=4)))
        self.assertFalse(m.candidates(store(80, 2, opcode=3)))
        self.assertFalse(m.candidates(store(80, 2)[:-1]))
        self.assertEqual(m.candidates(b'\0\0' + store(80, 2, source=9))[0]['pc'], 0x8002)
        self.assertEqual(m.candidates(store(80, 2, source=9))[0]['source_register'], 9)


if __name__ == '__main__':
    unittest.main()
