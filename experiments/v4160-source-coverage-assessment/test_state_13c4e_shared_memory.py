#!/usr/bin/env python3
"""Single-memory ordering, gate alias, and synthetic memory validation."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('shared', Path(__file__).with_name('state_13c4e_shared_memory.py'))
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
w, state = x.w, x.state


class SharedMemoryTest(unittest.TestCase):
    def setUp(self):
        self.codes = (state.gate.CODE, state.delta.CODE, state.tail.CODE)
        self.mem = state.gate.fixture((1, 1, 1), (0xfffe, 0, 0))
        w.store32(self.mem, w.SLOT, 0x1001)

    def call(self, gp, sp, raw=0):
        return x.run(self.codes, w.CODE, self.mem, gp, sp, 0x12345678,
                     lambda target, frame, mem: (raw, frame))

    def test_frame_overwrites_gate_after_it_was_read(self):
        sp, gp = state.gate.DATA+8, 0x20004000
        w.store32(self.mem, gp+340, 0)
        got = self.call(gp, sp)
        self.assertEqual(got[3], 0x9124)
        self.assertEqual(got[0], [(state.gate.DATA+2, 2), (state.gate.DATA+5, 1), (state.gate.DATA+4, 1)])
        self.assertEqual(w.load32(self.mem, sp-4), 0x12345678)

    def test_tail_store_updates_record_after_gate(self):
        address = state.gate.DATA+2
        gp = address-340
        got = self.call(gp, 0x2000ff00, 160)
        self.assertEqual((got[2], got[3]), ((address, 100), 0x137c0))
        self.assertEqual(w.load32(self.mem, address), 100)

    def test_invalid_or_missing_gate_bytes_rejected(self):
        del self.mem[state.gate.DATA+9]
        with self.assertRaisesRegex(ValueError, 'uninitialized'):
            self.call(0x20004000, 0x2000ff00)
        self.mem[state.gate.DATA+9] = 256
        with self.assertRaisesRegex(ValueError, 'invalid synthetic byte memory'):
            self.call(0x20004000, 0x2000ff00)

    def test_invalid_slot_and_resident_write_rejected(self):
        self.mem[w.SLOT] = 256
        with self.assertRaisesRegex(ValueError, 'invalid synthetic byte memory'):
            self.call(0x20004000, 0x2000ff00)
        self.mem[w.SLOT] = 1
        w.store32(self.mem, 0x20004154, 0)
        def resident(target, frame, mem):
            mem[0x20004154] = -1
            return 0, frame
        with self.assertRaisesRegex(ValueError, 'invalid synthetic byte memory'):
            x.run(self.codes, w.CODE, self.mem, 0x20004000, 0x2000ff00, 3, resident)

    def test_nonqualifying_record_does_not_call_or_write(self):
        self.mem.update(state.gate.fixture((0xfffe, 1, 1), (0xfffe, 1, 1)))
        before = dict(self.mem)
        def resident(*args):
            self.fail('unexpected call')
        got = x.run(self.codes, w.CODE, self.mem, 0x20004000, 0x2000ff00, 3, resident)
        self.assertEqual(got[3], 0x13cda)
        self.assertEqual(self.mem, before)


if __name__ == '__main__':
    unittest.main()
