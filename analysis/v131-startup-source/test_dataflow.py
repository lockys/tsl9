#!/usr/bin/env python3
import contextlib
import io
import runpy
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
a = runpy.run_path(str(HERE / 'dataflow.py'))
s = a['source']

class DataflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (HERE / 'wchble_rom.hex').read_bytes()
        assert s['digest'](raw) == s['HEX_SHA']
        mem = s['parse'](raw)
        cls.main = bytes(mem[p] for p in range(0x40000, 0x6ea66))

    def test_original(self):
        self.assertFalse(a['audit'](self.main)['other_readers_excluded'])
        with contextlib.redirect_stdout(io.StringIO()): a['main']()

    def test_instruction_mutations_rejected(self):
        # Bypass hash intentionally: exercise the semantic/window gate itself.
        for pc in (0x6de5e, 0x40286, 0x4028c, 0x402a8, 0x409fe, 0x40a14, 0x40a22, 0x40a24, 0x40a34):
            with self.subTest(pc=hex(pc)):
                mutant = bytearray(self.main)
                mutant[pc - 0x40000] ^= 1
                with self.assertRaises(ValueError): a['audit'](mutant)

    def test_each_single_byte_can_affect_guard_and_target(self):
        rows = a['byte_witnesses']()
        self.assertEqual([r['byte'] for r in rows], list(range(4)))
        self.assertTrue(all(r['zero_guard_differs'] and r['jalr_target_differs'] for r in rows))

    def test_hash_rejected(self):
        original = s['HEX_SHA']
        try:
            s['HEX_SHA'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'hash mismatch'): a['main']()
        finally:
            s['HEX_SHA'] = original

if __name__ == '__main__': unittest.main()
