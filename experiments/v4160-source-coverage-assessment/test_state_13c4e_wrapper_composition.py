#!/usr/bin/env python3
"""Synthetic nested-wrapper ordering and assumption checks."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('composition', Path(__file__).with_name('state_13c4e_wrapper_composition.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
w, s = c.wrapper, c.state


class CompositionTest(unittest.TestCase):
    def setUp(self):
        self.codes = (s.gate.CODE, s.delta.CODE, s.tail.CODE)
        self.first, self.second = (0xffff, 1, 1), (0xfffe, 0, 0)
        self.mem = {}
        w.store32(self.mem, w.SLOT, 0x12345679)

    def run_path(self, gp, sp, resident):
        return c.run(self.codes, w.CODE, self.first, self.second, gp, sp,
                     0x12345678, self.mem, resident)

    def test_inner_saved_ra_can_replace_post_call_word(self):
        sp = 0x2000ff00
        gp = sp-20-340
        w.store32(self.mem, gp+340, 0)
        got = self.run_path(gp, sp, lambda target, frame, mem: (0, frame))
        self.assertEqual(w.load32(self.mem, gp+340), 0x13ca2)
        self.assertEqual((got[2], got[3]), ((gp+340, 0), 0x137c0))

    def test_resident_corrupts_outer_saved_ra_is_rejected(self):
        sp, gp = 0x2000ff00, 0x20004000
        w.store32(self.mem, gp+340, 0)
        def resident(target, frame, mem):
            w.store32(mem, sp-4, 0)
            return 0, frame
        with self.assertRaisesRegex(ValueError, 'outer saved return changed'):
            self.run_path(gp, sp, resident)

    def test_odd_inner_return_clears_low_bit(self):
        sp, gp = 0x2000ff00, 0x20004000
        w.store32(self.mem, gp+340, 0)
        def resident(target, frame, mem):
            w.store32(mem, frame+12, 0x13ca3)
            return 0, frame
        got = self.run_path(gp, sp, resident)
        _, reads = s.gate.oracle(self.first, self.second)
        self.assertEqual(got, (reads, [0x81b0], None, 0x9124,
                               (0x137c0, 0, 35, 0), sp, 0x12345678))

    def test_resident_redirects_wrapper_return_is_rejected(self):
        sp, gp = 0x2000ff00, 0x20004000
        w.store32(self.mem, gp+340, 0)
        def resident(target, frame, mem):
            w.store32(mem, frame+12, 0)
            return 0, frame
        with self.assertRaisesRegex(ValueError, 'wrapper return changed'):
            self.run_path(gp, sp, resident)

    def test_resident_changes_stack_is_rejected_even_if_return_matches(self):
        sp, gp = 0x2000ff00, 0x20004000
        w.store32(self.mem, gp+340, 0)
        def resident(target, frame, mem):
            w.store32(mem, 0x300c, 0x13ca2)
            return 0, 0x3000
        with self.assertRaisesRegex(ValueError, 'wrapper stack changed'):
            self.run_path(gp, sp, resident)

    def test_gate_failure_does_not_write_frame_or_call(self):
        before = dict(self.mem)
        def resident(*args):
            self.fail('must not call')
        result = c.run(self.codes, w.CODE, (0xfffe, 1, 1), (0xfffe, 1, 1),
                       0x20004000, 0x2000ff00, 0x12345678, self.mem, resident)
        self.assertEqual(result[3], 0x13cda)
        self.assertEqual(self.mem, before)


if __name__ == '__main__':
    unittest.main()
