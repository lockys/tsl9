"""Host-only composition of selected RF steps and retained helper bytes.

This is not a callsite execution: intervening branches, argument setup and
transfer are omitted. Helper entry registers are supplied synthetically.
"""
import importlib.util
import pathlib
import runpy
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('copy_interpreter', pathlib.Path(__file__).with_name('interpreter.py'))
i = importlib.util.module_from_spec(spec)
spec.loader.exec_module(i)
model = runpy.run_path(str(ROOT / 'scripts/rf_tx_copy_model.py'))
header = runpy.run_path(str(ROOT / 'scripts/rf_tx_header_steps.py'))
provenance = runpy.run_path(str(ROOT / 'scripts/check-rf-copy-provenance.py'))
W = model['POINTER_WORD']
SIZE = W - i.RAM + 64


def seed(p):
    data = bytearray((x * 37 + 11) & 255 for x in range(SIZE))
    data[W-i.RAM:W-i.RAM+4] = p.to_bytes(4, 'little')
    return data


def header_steps(data, n):
    image = provenance['bulk']['base']['base']['IMAGE'].read_bytes()
    regs = [0] * 32
    regs[8], regs[9], regs[23] = W - 32, n, 0xa5
    state = {'regs': regs, 'memory': {i.RAM+k: v for k, v in enumerate(data)}, 'halted': False}
    for pc, (code, _, _) in header['SITES'].items():
        raw = image[pc-0x40000:pc-0x40000+len(code)]
        state = header['step'](state, pc, raw)
        if state['halted']:
            raise ValueError('header step halted')
    return state


def composed(data, src, n, fail_read=(), fail_write=()):
    state = header_steps(data, n)
    p = state['regs'][10]
    data = bytes(state['memory'][i.RAM+k] for k in range(len(data)))
    image = provenance['bulk']['base']['base']['IMAGE'].read_bytes()
    code = image[0x405a2-0x40000:0x405dc-0x40000]
    if code != i.BODY:
        raise ValueError('helper bytes changed')
    machine = i.Machine(data, p+2, src, n, code=code, unmapped_reads=fail_read, unmapped_writes=fail_write)
    machine.run()
    reload = int.from_bytes(machine.data[W-i.RAM:W-i.RAM+4], 'little')
    return p, reload, machine


class Integration(unittest.TestCase):
    def test_pinned_source(self):
        bulk = provenance['bulk']
        image = bulk['base']['base']['IMAGE'].read_bytes()
        bulk['base']['verify_windows'](image)
        provenance['source']['gate'](image)
        self.assertEqual(image[0x405a2-0x40000:0x405dc-0x40000], i.BODY)
        self.assertEqual(provenance['source']['pair'](image, 0x64e20, 0x64e24, 1, True, True), i.BASE)
        for pc in (0x64e0e, 0x64e14, 0x64e18, 0x64e1a, 0x64e1c, 0x64e1e, 0x64e20, 0x64e24, 0x64e28):
            mutant = bytearray(image); mutant[pc-0x40000] ^= 1
            with self.subTest(pc=hex(pc)), self.assertRaises(ValueError):
                bulk['base']['verify_windows'](mutant)

    def test_normal(self):
        for p in range(W-6, W+5):
            for src in (W-7, W-1, W, W+1, W+16, p+1, p+2, p+3):
                for n in (0, 1, 2, 4, 8):
                    with self.subTest(p=p, src=src, n=n):
                        data = seed(p)
                        memory = {i.RAM+k: v for k, v in enumerate(data)}
                        expected, initial, reloaded = model['tx_copy_from_word'](memory, src, n, 0xa5)
                        actual_p, actual_reload, m = composed(data, src, n)
                        self.assertEqual((actual_p, actual_reload), (initial, reloaded))
                        self.assertEqual(m.data, bytes(expected[i.RAM+k] for k in range(SIZE)))
                        self.assertEqual(m.r[10], p+2)
                        self.assertEqual(m.mmio, 0x12345678)
                        shadow = bytearray(data)
                        shadow[p-i.RAM:p-i.RAM+2] = bytes((0xa5, n))
                        events = [('read32', i.MMIO, 0x12345678), ('write32', i.MMIO, 0), ('fence.i',)]
                        for j in range(n):
                            value = shadow[src-i.RAM+j]
                            events.extend((('read8', src+j, value), ('write8', p+2+j, value)))
                            shadow[p+2-i.RAM+j] = value
                        events.append(('write32', i.MMIO, 0x12345678))
                        self.assertEqual(m.effects, events)

    def test_unmapped_header_steps_fail_closed(self):
        image = provenance['bulk']['base']['base']['IMAGE'].read_bytes()
        for pc, missing in ((0x64e0e, W+3), (0x64e14, W-4), (0x64e18, W-3)):
            with self.subTest(pc=hex(pc)):
                data = seed(W-4)
                memory = {i.RAM+k: v for k, v in enumerate(data)}
                del memory[missing]
                with self.assertRaises(ValueError):
                    model['tx_copy_from_word'](memory, W+16, 2, 0xa5)
                regs = [0] * 32
                regs[8], regs[9], regs[23] = W-32, 2, 0xa5
                state = {'regs': regs, 'memory': memory, 'halted': False}
                for site, (code, _, _) in header['SITES'].items():
                    before = state
                    state = header['step'](state, site, image[site-0x40000:site-0x40000+len(code)])
                    if site == pc:
                        self.assertTrue(state['halted'])
                        self.assertEqual(state['memory'], before['memory'])
                        self.assertEqual(state['regs'], before['regs'])
                        break
                    self.assertFalse(state['halted'])

    def test_unmapped_partial_effects(self):
        p, src, n = W-2, W-1, 4
        for mode in ('read', 'write'):
            for pos in range(n):
                with self.subTest(mode=mode, pos=pos):
                    data = seed(p)
                    memory = {i.RAM+k: v for k, v in enumerate(data)}
                    missing = (src if mode == 'read' else p+2) + pos
                    del memory[missing]
                    with self.assertRaises(ValueError):
                        model['tx_copy_from_word'](memory, src, n, 0xa5)
                    state = header_steps(data, n)
                    self.assertEqual(state['regs'][10], p)
                    data = bytearray(state['memory'][i.RAM+k] for k in range(SIZE))
                    m = i.Machine(data, p+2, src, n,
                                  unmapped_reads={missing} if mode == 'read' else (),
                                  unmapped_writes={missing} if mode == 'write' else ())
                    with self.assertRaisesRegex(i.Halt, 'unmapped data'):
                        m.run()
                    self.assertEqual(m.mmio, 0)
                    self.assertEqual(sum(e[0] == 'write8' for e in m.effects), pos)
                    self.assertEqual(sum(e[0] == 'read8' for e in m.effects), pos + (mode == 'write'))
                    shadow = bytearray(data)
                    for j in range(pos): shadow[p+2-i.RAM+j] = shadow[src-i.RAM+j]
                    self.assertEqual(m.data, shadow)

if __name__ == '__main__': unittest.main()
