import contextlib
import io
import runpy
import unittest
from unittest.mock import patch
from pathlib import Path

check = runpy.run_path(str(Path(__file__).with_name('check.py')))
parse, coverage = check['parse'], check['coverage']

def record(kind, address=0, data=b''):
    r = bytes([len(data), address >> 8, address & 255, kind]) + data
    return ':' + (r + bytes([-sum(r) & 255])).hex().upper() + '\n'

class EvidenceTests(unittest.TestCase):
    def test_real_evidence(self):
        with contextlib.redirect_stdout(io.StringIO()): check['main']()

    def test_source_absence_is_not_extraction_omission(self):
        source = {1: 0, 2: 255, 3: 7}
        self.assertEqual(coverage(source, {1: 0}, 1, 5), ([4], [2, 3]))
        self.assertEqual(coverage(source, source, 1, 5), ([4], []))
        self.assertEqual(coverage({**source, 4: 9}, source, 1, 5), ([], [4]))

    def test_parser_rejects_damaged_records(self):
        eof = record(1)
        good = record(0, 0, b'abc') + eof
        self.assertEqual(parse(good.encode()), {0: 97, 1: 98, 2: 99})
        for data in (good.replace('616263', '616264'), good[:-len(eof)],
                     record(0, 0, b'a') * 2 + eof, good + eof):
            with self.subTest(data=data), self.assertRaises(ValueError): parse(data.encode())

    def test_identity_rejects_mutation(self):
        original = Path.read_bytes
        def changed(path):
            b = original(path)
            return b.replace(b':', b';', 1) if path.name == 'wchble_rom.hex' else b
        with patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(ValueError, 'hash mismatch'):
            check['main']()

    def test_inclusive_branch_mutation_rejected(self):
        raw = Path(__file__).with_name('wchble_rom.hex').read_bytes()
        mem = parse(raw)
        main = bytearray(mem[p] for p in range(0x40000, 0x6ea66))
        gate = runpy.run_path(str(Path(__file__).parents[1] / 'resident-entry-reference-2026-10-21/source/inspect-source.py'))['gate']
        gate(main)
        main[0x40280 - 0x40000] ^= 0x10
        with self.assertRaises(ValueError): gate(main)

if __name__ == '__main__': unittest.main()
