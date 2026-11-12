"""Offline bounded semantic model and provenance checks; never executes C or firmware."""
from pathlib import Path
import hashlib
import unittest

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
C_SHA = 'b89d8552a4270c5ea2a6672ce7f2c88867f878d9c98c60a6f5d09c061a85b38f'
WINDOW = bytes.fromhex('''
b7070400fc474111b78507081306000706c6938505a01795ff1f1305450c82971797ff1f1307a70b9796ff1f9386660b1306e0058347c700811793f7f70f637ef60eeff07ff6b7070400fc47b785070813060010938505901795ff1f1305a52782971797ff1f0347f7369307a0056304f700eff03fc5b7070400fc47b785070813060010938505801795ff1f1305250c82971797ff1f0347771b9307a0056304f700eff05fcbb7070400fc47b775070813060010938505701795ff1f1305a53182971797ff1f0347f7409307a0056304f700eff07fceb7070400fc47b775070813060010938505601795ff1f1305a53e82971797ff1f0347f74d9307a0056304f700eff01fdcb7070400fc47b775070813065008938505501795ff1f1305251382971797ff1f0347c71a9307a005630af700b24041016ff01fe10507e39ce6ee19b7b24041018280
''')
SRC = (0x8077a00, 0x8077900, 0x8077800, 0x8077700, 0x8077600, 0x8077500)
DST = (0x2000c29c, 0x2000c494, 0x2000c30c, 0x2000c594, 0x2000c694, 0x2000c40c)
SIZE = (112, 256, 256, 256, 256, 133)
DEFAULT = (0x1316a, 0x12e86, 0x12f18, 0x12f7a, 0x13084, 0x13108)
MARK = tuple(DST[i] + SIZE[i] - 1 for i in range(1, 6))


def check_image(data):
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('image length/hash mismatch')
    if len(WINDOW) != 0x1330a - 0x131c2 or data[0x131c2-0x8000:0x1330a-0x8000] != WINDOW:
        raise ValueError('instruction window mismatch')


def model(h):
    for i in range(6):
        target = h.load_slot(0x4004c)
        h.external_call(target & ~1, DST[i], SRC[i], SIZE[i])
        if i == 0:
            for j in range(4):
                if not 32 <= h.read_byte(DST[0] + 12 + j) <= 126:
                    h.default_call(DEFAULT[0], False)
                    break
        elif h.read_byte(MARK[i-1]) != 0x5a:
            h.default_call(DEFAULT[i], i == 5)
            if i == 5:
                return 'tail'
    return 'return'


class Hooks:
    def __init__(self):
        self.mem = {DST[0] + 12 + i: 32 for i in range(4)}
        self.mem.update({a: 0x5a for a in MARK})
        self.slot = 1
        self.events = []
        self.action = lambda kind, arg: None

    def load_slot(self, addr):
        self.action('load', addr)
        raw = self.slot
        self.events.append(('load', addr, raw))
        return raw

    def external_call(self, target, dst, src, length):
        self.events.append(('call', target, dst, src, length))
        self.action('call', dst)

    def read_byte(self, addr):
        self.events.append(('read', addr))
        self.action('read', addr)
        return self.mem[addr]

    def default_call(self, target, tail):
        self.events.append(('default', target, tail))
        self.action('default', target)


class Checks(unittest.TestCase):
    def test_pins(self):
        data = IMAGE.read_bytes()
        check_image(data)
        self.assertEqual(hashlib.sha256((HERE / 'candidate.c').read_bytes()).hexdigest(), C_SHA)
        for at in (0, 0x131c2-0x8000, 0x1330a-0x8000-1):
            altered = bytearray(data); altered[at] ^= 1
            with self.assertRaises(ValueError): check_image(altered)
        with self.assertRaises(ValueError): check_image(data[:-1])
        self.assertEqual(data[0x131c2-0x8000:0x1330a-0x8000], WINDOW)

    def test_every_byte_and_position(self):
        for pos in range(4):
            for byte in range(256):
                h = Hooks(); h.mem[DST[0]+12+pos] = byte
                model(h)
                failures = [e for e in h.events if e[0] == 'default']
                self.assertEqual(bool(failures), not 32 <= byte <= 126)
                reads = [e[1] for e in h.events if e[0] == 'read' and DST[0]+12 <= e[1] < DST[0]+16]
                self.assertEqual(len(reads), 4 if 32 <= byte <= 126 else pos+1)
        for index, address in enumerate(MARK):
            for byte in range(256):
                h = Hooks(); h.mem[address] = byte
                result = model(h)
                failures = [e for e in h.events if e[0] == 'default']
                self.assertEqual(failures, [] if byte == 90 else [('default', DEFAULT[index+1], index == 4)])
                self.assertEqual(result, 'tail' if index == 4 and byte != 90 else 'return')

    def test_order_and_effects(self):
        h = Hooks()
        def effect(kind, arg):
            if kind == 'call':
                h.slot += 1
                if arg == DST[0]: h.mem[DST[0]+12] = 0
            if kind == 'default' and arg == DEFAULT[0]: h.mem[MARK[0]] = 0
            if kind == 'default' and arg == DEFAULT[1]: h.mem[MARK[1]] = 0
            if kind == 'read' and arg == MARK[1]: h.mem[MARK[2]] = 0
        h.action = effect
        self.assertEqual(model(h), 'return')
        expected = []
        for i in range(6):
            expected += [('load', 0x4004c, i+1), ('call', (i+1) & ~1, DST[i], SRC[i], SIZE[i])]
            expected += [('read', DST[0]+12)] if i == 0 else [('read', MARK[i-1])]
            if i < 4: expected += [('default', DEFAULT[i], False)]
        self.assertEqual(h.events, expected)

    def test_jalr_raw_and_effective_targets(self):
        values = (0, 1, 0x12345678, 0x12345679, 0xfffffffe, 0xffffffff)
        h = Hooks()
        def effect(kind, arg):
            if kind == 'load':
                h.slot = values[sum(e[0] == 'load' for e in h.events)]
        h.action = effect
        self.assertEqual(model(h), 'return')
        transfers = [e for e in h.events if e[0] in ('load', 'call')]
        expected = []
        for i, raw in enumerate(values):
            expected.extend([('load', 0x4004c, raw),
                             ('call', raw & 0xfffffffe, DST[i], SRC[i], SIZE[i])])
        self.assertEqual(transfers, expected)

    def test_read_side_effect_and_no_cache(self):
        h = Hooks()
        def effect(kind, arg):
            if kind == 'read' and arg == DST[0]+12:
                h.mem[DST[0]+13] = 31
        h.action = effect
        model(h)
        self.assertIn(('default', DEFAULT[0], False), h.events)
        self.assertNotIn(('read', DST[0]+14), h.events)

    def test_all_fail_and_tail(self):
        h = Hooks(); h.mem[DST[0]+12] = 0
        for a in MARK: h.mem[a] = 0
        self.assertEqual(model(h), 'tail')
        self.assertEqual([e for e in h.events if e[0] == 'default'],
                         [('default', d, i == 5) for i, d in enumerate(DEFAULT)])
        self.assertEqual(h.events[-1], ('default', DEFAULT[5], True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
