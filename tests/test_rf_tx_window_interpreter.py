import runpy
import unittest

m = runpy.run_path('scripts/rf_tx_window_interpreter.py')
old = runpy.run_path('scripts/rf_tx_header_steps.py')
image = runpy.run_path('scripts/check-rf-tx-header-window.py')
W = 0x20003534


class WindowTest(unittest.TestCase):
    def code(self):
        return {m['START'] + i: b for i, b in enumerate(m['CODE'])}

    def state(self, p=W, source=0x1234):
        regs = [0] * 32
        regs[8], regs[9], regs[23], regs[24] = W - 32, 7, 0xa5, source
        mem = {a: 0 for a in range(W - 8, W + 16)}
        mem.update({W + i: b for i, b in enumerate(p.to_bytes(4, 'little'))})
        return {'regs': regs, 'memory': mem}

    def test_fallthrough_against_prior_header(self):
        for p in (W - 2, W, W + 3):
            s = self.state(p)
            prior = dict(s, halted=False)
            for pc, (code, _, _) in old['SITES'].items():
                prior = old['step'](prior, pc, code)
            result = m['run'](s, self.code())
            self.assertEqual(result['status'], 'boundary')
            self.assertEqual(result['memory'], prior['memory'])
            self.assertEqual(result['regs'][10:13], [p + 2, 0x1234, 7])
            self.assertEqual(result['target'], 0x20000332)
            self.assertEqual(result['pc'], 0x64e24)

    def test_taken_branch_exits_subset_without_stores(self):
        s = self.state(source=0)
        result = m['run'](s, self.code())
        self.assertEqual((result['status'], result['pc']), ('halted', 0x64ee0))
        self.assertEqual(result['memory'], s['memory'])
        self.assertEqual(result['regs'][10], W)

    def test_each_byte_mutation_and_missing_fetch(self):
        for address in self.code():
            for replacement in (None, self.code()[address] ^ 1):
                code = self.code()
                if replacement is None:
                    del code[address]
                else:
                    code[address] = replacement
                self.assertEqual(m['run'](self.state(), code)['status'], 'halted')

    def test_unmapped_load_and_stores(self):
        for address in (W + 3, W - 2, W - 1):
            s = self.state(W - 2)
            del s['memory'][address]
            result = m['run'](s, self.code())
            self.assertEqual(result['status'], 'halted')
            self.assertNotIn('target', result)

    def test_candidate_bytes(self):
        data = image['IMAGE'].read_bytes()
        image['check_image'](data)
        self.assertEqual(data[m['START'] - 0x40000:m['START'] - 0x40000 + len(m['CODE'])], m['CODE'])


if __name__ == '__main__':
    unittest.main()
