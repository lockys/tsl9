"""Compare finite synthetic cases with the existing C effect model, not RV32 execution.

Set RF_COPY_PROBE to the compiled tests/rf_copy_reference_probe.c executable.
"""
import os
import runpy
import subprocess
import unittest

model = runpy.run_path('scripts/rf_tx_copy_model.py')
W = model['POINTER_WORD']
BASE = W - 16


class ReferenceDiff(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('RF_COPY_PROBE'), 'set RF_COPY_PROBE to the compiled C probe')
    def test_fixed_alias_cases_and_effect_order(self):
        # Empty, independent, forward propagation, backward overlap, prefix alias,
        # and self-overwriting P. Each address belongs to the synthetic byte map.
        for p, src, n in ((W-2, W-1, 4), (W, W+16, 2),
                          (W-4, W-2, 4), (W-2, W+16, 0),
                          (W+1, W-4, 4), (W-5, W+16, 4)):
            with self.subTest(p=p, src=src, n=n):
                before = {BASE+i: i for i in range(64)}
                for i, byte in enumerate(p.to_bytes(4, 'little')):
                    before[W+i] = byte
                expected, initial, reload = model['tx_copy_from_word'](before, src, n, 0xa5)
                lines = subprocess.check_output([os.environ['RF_COPY_PROBE'], hex(p), hex(src), str(n)], text=True).splitlines()
                self.assertEqual(lines[-1], 'memory ' + bytes(expected[BASE+i] for i in range(64)).hex())
                self.assertEqual(initial, p)
                self.assertEqual(reload, model['load_pointer'](expected))
                events = [tuple(int(x, 16) if j else int(x) for j, x in enumerate(line.split())) for line in lines[:-1]]
                self.assertEqual([e[0] for e in events], [0, 1, 2] + [x for _ in range(n) for x in (3, 4)] + [1, 5])
                self.assertEqual(events[0][1:3], (0x20000336, 0x4002420c))
                self.assertEqual(events[1][1:], (0x2000033a, 0x4002420c, 0))
                self.assertEqual(events[2][1], 0x2000033e)
                shadow = dict(before)
                shadow[p], shadow[p+1] = 0xa5, n & 255
                for i in range(n):
                    read, write = events[3+2*i:5+2*i]
                    self.assertEqual(read[1:3], (0x20000358, src+i))
                    self.assertEqual(write[1:], (0x20000362, p+2+i, shadow[src+i]))
                    shadow[p+2+i] = shadow[src+i]
                self.assertEqual(events[-2][1:], (0x2000034e, 0x4002420c, 0x12345678))
                self.assertEqual(events[-1][1], 0x20000352)
                self.assertEqual(shadow, expected)


if __name__ == '__main__':
    unittest.main()
