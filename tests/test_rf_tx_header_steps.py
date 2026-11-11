import runpy
import unittest

steps = runpy.run_path('scripts/rf_tx_header_steps.py')
model = runpy.run_path('scripts/rf_tx_copy_model.py')
step, sites, W = steps['step'], steps['SITES'], model['POINTER_WORD']


class HeaderStepsTest(unittest.TestCase):
    def state(self, p, length=4):
        mem = {a: (a - W) & 255 for a in range(W - 16, W + 32)}
        mem.update({W + i: b for i, b in enumerate(p.to_bytes(4, 'little'))})
        regs = [0] * 32
        regs[8], regs[9], regs[23] = W - 32, length, 0x1a5
        return {'regs': regs, 'memory': mem, 'halted': False}

    def test_header_against_python_model_including_pointer_alias(self):
        for p in (W - 8, W - 2, W - 1, W, W + 1, W + 3, W + 8):
            for length in (0, 1, 4):
                with self.subTest(p=p, length=length):
                    initial = self.state(p, length)
                    s = initial
                    for pc in sites:
                        s = step(s, pc, sites[pc][0])
                        self.assertFalse(s['halted'])
                    # The reference includes the helper; compare its header-only
                    # effects by choosing zero payload, keeping the same low byte.
                    expected = dict(initial['memory'])
                    expected[p], expected[p + 1] = 0xa5, length
                    self.assertEqual(s['memory'], expected)
                    reference = model['tx_copy'](initial['memory'], p, W + 16, length, 0x1a5)
                    for a in set(expected) - set(range(p + 2, p + 2 + length)):
                        self.assertEqual(s['memory'][a], reference[a])
                    self.assertEqual(s['regs'][10], p)
                    self.assertEqual(initial, self.state(p, length))

    def test_registers_drive_access_and_loaded_pointer_survives_self_overwrite(self):
        s = self.state(W)
        s = step(s, 0x64e0e, sites[0x64e0e][0])
        s['regs'][23], s['regs'][9] = 0x12345678, 0x102
        s = step(s, 0x64e14, sites[0x64e14][0])
        s = step(s, 0x64e18, sites[0x64e18][0])
        self.assertEqual(s['regs'][10], W)
        self.assertEqual([s['memory'][W], s['memory'][W + 1]], [0x78, 2])
        self.assertNotEqual(model['load_pointer'](s['memory']), W)
        s['regs'][10] = W + 8
        s = step(s, 0x64e14, sites[0x64e14][0])
        self.assertEqual(s['memory'][W + 8], 0x78)

    def test_mutation_forbidden_and_halt_is_sticky(self):
        for pc, (code, _, _) in sites.items():
            for i in range(len(code)):
                for bit in range(8):
                    bad = bytearray(code)
                    bad[i] ^= 1 << bit
                    s = self.state(W)
                    result = step(s, pc, bytes(bad))
                    self.assertTrue(result['halted'])
                    self.assertEqual(result['memory'], s['memory'])
                    self.assertEqual(result['regs'], s['regs'])
                    self.assertEqual(step(result, pc, code), result)
        self.assertTrue(step(self.state(W), 0x64e10, b'')['halted'])

    def test_unmapped_each_access_and_no_partial_write(self):
        for pc, address in ((0x64e0e, W + 3), (0x64e14, W), (0x64e18, W + 1)):
            s = self.state(W)
            s['regs'][10] = W
            del s['memory'][address]
            result = step(s, pc, sites[pc][0])
            self.assertTrue(result['halted'])
            self.assertEqual(result['memory'], s['memory'])
            self.assertEqual(result['regs'], s['regs'])

    def test_real_image_bytes(self):
        decoder = runpy.run_path('scripts/check-rf-tx-header-window.py')
        image = decoder['IMAGE'].read_bytes()
        decoder['check_image'](image)
        for pc, (code, _, _) in sites.items():
            self.assertEqual(image[pc - 0x40000:pc - 0x40000 + len(code)], code)


if __name__ == '__main__':
    unittest.main()
