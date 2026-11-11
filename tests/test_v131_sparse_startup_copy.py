import runpy
import unittest
from pathlib import Path

model = runpy.run_path('scripts/v131_sparse_startup_copy.py')
provenance = runpy.run_path('scripts/check-rf-copy-provenance.py')
helper = runpy.run_path('experiments/tsl9-copy-instruction-interpreter/interpreter.py')


class SparseStartupCopyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = Path('analysis/v131-startup-source/wchble_rom.hex').read_bytes()
        image = provenance['bulk']['base']['base']['IMAGE'].read_bytes()
        header = provenance['bulk']['base']['base']['HEADER'].read_bytes()
        provenance['check'](image, header, raw)
        cls.source = provenance['sparse']['parse'](raw)

    def test_first_copy_supplies_exact_interpreter_mapping(self):
        result = model['copy'](self.source, {}, 'first')
        self.assertEqual((result['status'], result['words_copied']), ('copied', 2957))
        mapping = result['memory']
        body = bytes(mapping[helper['BASE'] + i] for i in range(58))
        self.assertEqual(body, helper['BODY'])
        self.assertEqual(len(body), 58)

    def test_missing_first_source_stops_before_word_write(self):
        for missing in (0x402b0, 0x405a2, 0x405a3, 0x430e0):
            with self.subTest(missing=hex(missing)):
                source = self.source.copy()
                del source[missing]
                offset = (missing - 0x402b0) // 4 * 4
                target = 0x20000040 + offset
                result = model['copy'](source, {target: 0x99}, 'first')
                self.assertEqual((result['status'], result['address'], result['words_copied']),
                                 ('missing-source', missing, offset // 4))
                self.assertEqual(result['memory'][target], 0x99)
                self.assertNotIn(target + 1, result['memory'])

    def test_second_copy_missing_last_word_not_first_copy_failure(self):
        first = model['copy'](self.source, {}, 'first')
        second = model['copy'](self.source, first['memory'], 'second')
        self.assertEqual((second['status'], second['address'], second['words_copied']),
                         ('missing-source', 0x6eb2c, 34))
        self.assertNotIn(0x20002ef8, second['memory'])
        self.assertEqual(bytes(second['memory'][helper['BASE'] + i] for i in range(58)),
                         helper['BODY'])
        for i in range(4):
            source = self.source.copy()
            source.update((0x6eb2c + j, 0xa0 + j) for j in range(4) if j != i)
            result = model['copy'](source, {}, 'second')
            self.assertEqual((result['status'], result['address'], result['words_copied']),
                             ('missing-source', 0x6eb2c + i, 34))
            self.assertNotIn(0x20002ef8, result['memory'])


if __name__ == '__main__':
    unittest.main()
