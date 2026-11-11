import runpy
import unittest

m = runpy.run_path('scripts/rf_tx_connected_interpreter.py')
w, h = m['window'], m['helper']
model = runpy.run_path('scripts/rf_tx_copy_model.py')
normal_run = m['run']
# Existing corpus exercises the explicit isolated diagnostic seam.
m['run'] = m['run_isolated_provenance']


class ConnectedTest(unittest.TestCase):
    def inputs(self, delta=16, count=5):
        base = h['RAM']
        p = base + 64
        memory = {base + i: i % 256 for i in range(128)}
        memory.update({model['POINTER_WORD'] + i: b for i, b in enumerate(p.to_bytes(4, 'little'))})
        regs = [0] * 32
        regs[8], regs[9], regs[23], regs[24] = model['POINTER_WORD'] - 32, count, 0xa5, p + delta
        code = {w['START'] + i: b for i, b in enumerate(w['CODE'])}
        code.update({0x64e28: 0x1c, 0x64e29: 0x50})
        mapping = {h['BASE'] + i: b for i, b in enumerate(h['BODY'])}
        return {'regs': regs, 'memory': memory}, code, mapping, p

    def test_startup_gate_and_real_mapping(self):
        provenance = runpy.run_path('scripts/check-rf-copy-provenance.py')
        raw = __import__('pathlib').Path('analysis/v131-startup-source/wchble_rom.hex').read_bytes()
        source = provenance['sparse']['parse'](raw)
        state, code, _, _ = self.inputs()
        result = normal_run(state, code, source)
        self.assertEqual((result['status'], result['copy'], result['address']),
                         ('halted', 'second', 0x6eb2c))
        self.assertNotIn('effects', result)
        self.assertEqual(bytes(result['startup_memory'][h['BASE'] + i] for i in range(58)), h['BODY'])
        fixture = m['InjectedSecondCopyFixture'](bytes(range(4)))
        hypothetical = m['run_with_injected_fixture'](state, code, source, fixture)
        self.assertEqual(hypothetical['status'], 'reloaded')
        self.assertIs(hypothetical['hypothetical'], True)
        self.assertNotIn(0x6eb2c, source)
        complete = dict(source)
        complete.update((0x6eb2c + i, i) for i in range(4))
        for bad in (complete, {**source, 0x405a2: source[0x405a2] ^ 1},
                    {k: v for k, v in source.items() if k != 0x6eaa4}):
            for result in (normal_run(state, code, bad),
                           m['run_with_injected_fixture'](state, code, bad, fixture)):
                self.assertEqual(result['status'], 'halted')
                self.assertNotIn('effects', result)
        for invalid in (b'abcd', m['InjectedSecondCopyFixture'](b'abc'),
                        m['InjectedSecondCopyFixture'](bytearray(4))):
            result = m['run_with_injected_fixture'](state, code, source, invalid)
            self.assertEqual(result['status'], 'halted')
            self.assertNotIn('effects', result)
        for i in range(4):
            word = bytearray(range(4)); word[i] ^= 0xff
            result = m['run_with_injected_fixture'](state, code, source,
                                                    m['InjectedSecondCopyFixture'](bytes(word)))
            self.assertEqual(result['status'], 'reloaded')
            self.assertIs(result['hypothetical'], True)
            bad = dict(source); bad[0x6eb2c + i] = word[i]
            self.assertEqual(normal_run(state, code, bad)['status'], 'halted')

    def test_corpus_against_model(self):
        for n in range(9):
            for delta in (-2, 0, 1, 2, 3, 16):
                state, code, mapping, p = self.inputs(delta, n)
                with self.subTest(n=n, delta=delta):
                    result = m['run'](state, code, mapping)
                    self.assertEqual(result['status'], 'reloaded')
                    self.assertEqual(result['pc'], 0x64e2a)
                    self.assertEqual(result['regs'][15], model['load_pointer'](result['memory']))
                    self.assertEqual(result['regs'][1], 0x64e28)
                    self.assertEqual(result['memory'], model['tx_copy'](state['memory'], p, p + delta, n, 0xa5))
                    self.assertEqual(result['mmio'], 0x12345678)

    def test_pointer_alias_against_model(self):
        state, code, mapping, _ = self.inputs()
        word = model['POINTER_WORD']
        p = word - 2
        state['memory'].update({p + i: 0 for i in range(8)})
        state['memory'].update({word + i: b for i, b in enumerate(p.to_bytes(4, 'little'))})
        state['regs'][9], state['regs'][24] = 4, word - 1
        expected, initial, reloaded = model['tx_copy_from_word'](state['memory'], word - 1, 4, 0xa5)
        result = m['run'](state, code, mapping)
        self.assertEqual(result['status'], 'reloaded')
        self.assertEqual(initial, p)
        self.assertEqual(reloaded, 0x04040404)
        self.assertEqual(result['regs'][15], reloaded)
        self.assertEqual(result['memory'], expected)

    def test_reload_fail_closed(self):
        state, code, mapping, _ = self.inputs()
        for address in (0x64e28, 0x64e29):
            bad = dict(code); bad[address] ^= 1
            result = m['run'](state, bad, mapping)
            self.assertEqual(result['status'], 'halted')
            self.assertEqual(result['pc'], 0x64e28)
            del bad[address]
            self.assertEqual(m['run'](state, bad, mapping)['status'], 'halted')
        # Test the reload seam directly: the first load otherwise requires these
        # bytes to be mapped, and the modeled helper cannot unmap them.
        result = m['run'](state, code, mapping)
        result['pc'] = 0x64e28
        del result['memory'][model['POINTER_WORD'] + 2]
        before = list(result['regs'])
        m['reload_pointer'](result, code)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['pc'], 0x64e28)
        self.assertEqual(result['regs'], before)

    def test_unknown_decoded_target(self):
        state, code, mapping, _ = self.inputs()
        boundary = w['run'](state, code)
        boundary['target'] += 2
        prior_ra = boundary['regs'][1]
        original = w['run']
        try:
            w['run'] = lambda *_: boundary
            result = m['run'](state, code, mapping)
            self.assertEqual(result['status'], 'halted')
            self.assertEqual(result['regs'][1], prior_ra)
            self.assertNotIn('effects', result)
        finally:
            w['run'] = original

    def test_mapping_and_data_fail_closed(self):
        state, code, mapping, p = self.inputs()
        for addr in (h['BASE'], h['BASE'] + 57):
            bad = dict(mapping); bad[addr] ^= 1
            self.assertEqual(m['run'](state, code, bad)['status'], 'halted')
            del bad[addr]
            self.assertEqual(m['run'](state, code, bad)['status'], 'halted')
        del state['memory'][p + 18]
        result = m['run'](state, code, mapping)
        self.assertEqual(result['status'], 'halted')
        self.assertEqual(result['reason'], 'unmapped data')
        self.assertEqual(result['regs'][1], 0x64e28)
        self.assertEqual(result['memory'][p + 2], (p + 16 - h['RAM']) % 256)


if __name__ == '__main__':
    unittest.main()
