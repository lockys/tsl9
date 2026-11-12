"""Independent Python sequence model; it does not execute the C candidate."""
import hashlib
from pathlib import Path
import unittest


def model(bus, a0, a1, a2):
    s1 = a0
    bus.write(a1)
    bus.csr('csrc', 0x800, 136)
    r = bus.call('18e98', (a0, a1, a2))
    r = bus.call('18e90', (49, r[1], r[2]))
    r = bus.call('18ec4', (s1, r[1], r[2]))
    slot = bus.read()
    r = bus.call('18ef2', (s1, slot, r[2]))
    r = bus.call('18eb6', r)
    bus.csr('csrs', 0x800, 136)
    return r[0]


class Stop(Exception):
    pass


class Bus:
    def __init__(self, stop=None):
        self.events = []
        self.slot = None
        self.stop = stop

    def write(self, v):
        self.events.append(('write', v))
        self.slot = v

    def read(self):
        self.events.append(('read', self.slot))
        return self.slot

    def csr(self, op, csr, mask):
        self.events.append((op, csr, mask))

    def call(self, name, args):
        self.events.append((name, args))
        if name == self.stop:
            raise Stop()
        if name == '18ec4':
            # A callee can reach the same slot through a bus alias.
            self.slot = 'overwritten'
        return tuple(name + ':' + reg for reg in ('a0', 'a1', 'a2'))


class SequenceTests(unittest.TestCase):
    def test_full_sequence_and_alias(self):
        bus = Bus()
        result = model(bus, 'entry-a0', 'entry-a1', 'entry-a2')
        self.assertEqual(result, '18eb6:a0')
        self.assertEqual(bus.events, [
            ('write', 'entry-a1'), ('csrc', 0x800, 136),
            ('18e98', ('entry-a0', 'entry-a1', 'entry-a2')),
            ('18e90', (49, '18e98:a1', '18e98:a2')),
            ('18ec4', ('entry-a0', '18e90:a1', '18e90:a2')),
            ('read', 'overwritten'),
            ('18ef2', ('entry-a0', 'overwritten', '18ec4:a2')),
            ('18eb6', ('18ef2:a0', '18ef2:a1', '18ef2:a2')),
            ('csrs', 0x800, 136),
        ])

    def test_each_nonreturn_stops_suffix(self):
        names = ['18e98', '18e90', '18ec4', '18ef2', '18eb6']
        full = Bus()
        model(full, 1, 2, 3)
        for name in names:
            with self.subTest(name=name):
                bus = Bus(stop=name)
                with self.assertRaises(Stop):
                    model(bus, 1, 2, 3)
                end = next(i for i, event in enumerate(full.events) if event[0] == name)
                self.assertEqual(bus.events, full.events[:end + 1])

    def test_c_source_pin(self):
        source = Path(__file__).with_name('candidate.c').read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), '3b8cf44d2894d9491eb976696e190f149905c384b56085751776381886a6268c')


if __name__ == '__main__':
    unittest.main()
