"""Failure and alias witnesses for the bounded slice; no compiled C invocation."""
import unittest
from pathlib import Path

from oracle import BASE, Slice

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'


class OracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = IMAGE.read_bytes()
        cls.oracle = Slice(cls.image)

    def run_slice(self, **changes):
        values = dict(initial=bytes([0xa5]) * 140000, origin=BASE - 100, base_index=100,
                      source_index=110, bank=0, length=3, command=4, entry_a6=7)
        values.update(changes)
        return self.oracle.run(**values)

    def test_forward_alias(self):
        memory, r, e = self.run_slice()
        self.assertEqual(memory[111:114], bytes([3, 3, 3]))
        self.assertEqual(r[4], 16)
        self.assertEqual(e, {'reads': 3, 'writes': 7, 'write_start_index': 106, 'write_end_index': 114})

    def test_zero_preserves_a6(self):
        self.assertEqual(self.run_slice(length=0, entry_a6=0xdeadbeef)[1][6], 0xdeadbeef)

    def test_bank_extent_thresholds(self):
        for bank in (0, 1):
            for n in (1051, 1052):
                end = self.run_slice(bank=bank, length=n, source_index=70000)[2]['write_end_index']
                self.assertEqual(end <= 100 + (bank + 1) * 1062, n <= 1051)

    def test_invalid_domain(self):
        for change in ({'bank': 2}, {'length': 65536}, {'origin': BASE},
                       {'source_index': 139999, 'length': 3}, {'initial': bytes(108)},
                       {'command': 1 << 32}, {'entry_a6': -1}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_slice(**change)

    def test_budget(self):
        with self.assertRaisesRegex(ValueError, 'budget'):
            self.run_slice(budget=1)

    def test_unsupported_instruction(self):
        altered = bytearray(self.image)
        altered[0xace:0xad2] = bytes.fromhex('ffffffff')
        oracle = Slice(altered)
        with self.assertRaisesRegex(ValueError, 'unsupported RV32'):
            oracle.run(bytes(1000), BASE - 100, 100, 300, 0, 1, 1, 7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
