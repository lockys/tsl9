"""Python event model and tests only: never loads or executes candidate C."""
import hashlib
import unittest
from pathlib import Path

MASK = 0xffffffff
STATUS, CONTROL = 0x4002200c, 0x40022010
ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
PIN = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
C_PIN = '5db6dd08f40ee73470fd1475dbb2259dd747fae30450e01fd67b4e81d77c3e37'
WINDOW = bytes.fromhex('372702401c4bc166137505f0d58f1ccb5c47858bf5ff372702405c47898bf5ff3727024013060010b386f50003a80600b306f50023a006015447898af5fe9107e394c7fe1c4bb7062000d58f1ccbb7270240d847058b75ff984bc176fd16758f98cb8280')


def bitop(op, value, mask):
    if isinstance(value, int):
        return (value | mask if op == 'or' else value & mask) & MASK
    return (op, value, mask)  # symbolic expression, not a solver


class Bus:
    def __init__(self, words=None, reads=None):
        self.words = dict(words or {})
        self.reads = {a: list(v) for a, v in (reads or {}).items()}
        self.events = []

    def read(self, addr):
        addr &= MASK
        queue = self.reads.get(addr, [])
        value = queue.pop(0) if queue else self.words.get(addr, 0)
        self.events.append(('r', addr, value))
        return value

    def write(self, addr, value):
        addr &= MASK
        self.events.append(('w', addr, value))
        self.words[addr] = value


class ObservationStop(Exception):
    """Test observer stopped the run; this is not a model return or timeout."""


class BoundedBus(Bus):
    def __init__(self, reads, limit):
        super().__init__(reads=reads)
        self.limit = limit

    def read(self, addr):
        if len(self.events) == self.limit:
            raise ObservationStop()
        return super().read(addr)

    def write(self, addr, value):
        if len(self.events) == self.limit:
            raise ObservationStop()
        super().write(addr, value)


def model(bus, a0, a1, mutation=None):
    dest = a0 & 0xffffff00
    bus.write(CONTROL, bitop('or', bus.read(CONTROL), 0x10000))
    def poll(mask):
        while bus.read(STATUS) & mask:
            pass
    poll(1)
    poll(2)
    # Mutation models the incorrect prefetch-all interpretation.
    prefetched = ([bus.read((a1 + i) & MASK) for i in range(0, 256, 4)]
                  if mutation == 'prefetch' else None)
    for i in range(0, 256, 4):
        value = prefetched[i // 4] if prefetched is not None else bus.read((a1 + i) & MASK)
        bus.write((dest + i) & MASK, value)
        poll(2)
    bus.write(CONTROL, bitop('or', bus.read(CONTROL), 0x200000))
    poll(1)
    bus.write(CONTROL, bitop('and', bus.read(CONTROL), 0xfffeffff))
    return dest


class ReferenceTests(unittest.TestCase):
    def test_source_pins(self):
        data = IMAGE.read_bytes()
        self.assertEqual(len(data), 76800)
        self.assertEqual(hashlib.sha256(data).hexdigest(), PIN)
        window = data[0x18ef2-0x8000:0x18f56-0x8000]
        self.assertEqual(window, WINDOW)
        self.assertEqual(hashlib.sha256(window).hexdigest(), '8cd6ddd7edd2d5a0adb776d396c8cb499d64ce974f38df7e651f9af720114dd8')

    def test_c_source_identity_and_mutation(self):
        data = Path(__file__).with_name('candidate.c').read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), C_PIN)
        mutated = bytearray(data)
        mutated[0] ^= 1
        self.assertNotEqual(hashlib.sha256(mutated).hexdigest(), C_PIN)

    def test_bounded_poll_prefixes(self):
        start = [('r', CONTROL, 0), ('w', CONTROL, 0x10000)]
        copy = []
        for i in range(0, 256, 4):
            copy += [('r', 0x2000+i, 0), ('w', 0x3000+i, 0), ('r', STATUS, 0)]
        cases = [
            ([1]*3, start + [('r', STATUS, 1)]*3),
            ([0] + [2]*3, start + [('r', STATUS, 0)] + [('r', STATUS, 2)]*3),
            ([0, 0] + [2]*3, start + [('r', STATUS, 0)]*2 +
             [('r', 0x2000, 0), ('w', 0x3000, 0)] + [('r', STATUS, 2)]*3),
            ([0, 0] + [0]*64 + [1]*3, start + [('r', STATUS, 0)]*2 + copy +
             [('r', CONTROL, 0x10000), ('w', CONTROL, 0x210000)] + [('r', STATUS, 1)]*3),
        ]
        for reads, expected in cases:
            with self.subTest(prefix_length=len(expected)):
                bus = BoundedBus({STATUS: reads}, len(expected))
                with self.assertRaises(ObservationStop):
                    model(bus, 0x3000, 0x2000)
                self.assertEqual(bus.events, expected)

    def test_exact_trace_symbolic_and_poll_reloads(self):
        words = {0x2000 + i: ('source', i) for i in range(0, 256, 4)}
        words[CONTROL] = 'C'
        bus = Bus(words, {STATUS: [1, 0, 2, 0, 2, 0] + [0]*63 + [1, 0]})
        self.assertEqual(model(bus, 0x30ff, 0x2000), 0x3000)
        c1 = ('or', 'C', 0x10000)
        c2 = ('or', c1, 0x200000)
        expected = [('r', CONTROL, 'C'), ('w', CONTROL, c1)]
        expected += [('r', STATUS, n) for n in (1, 0, 2, 0)]
        for i in range(0, 256, 4):
            expected += [('r', 0x2000+i, ('source', i)), ('w', 0x3000+i, ('source', i))]
            expected += [('r', STATUS, n) for n in ([2, 0] if i == 0 else [0])]
        expected += [('r', CONTROL, c1), ('w', CONTROL, c2), ('r', STATUS, 1), ('r', STATUS, 0), ('r', CONTROL, c2), ('w', CONTROL, ('and', c2, 0xfffeffff))]
        self.assertEqual(bus.events, expected)

    def test_overlap_and_negative_mutation(self):
        words = {0x1000+i: i + 1 for i in range(0, 260, 4)}
        correct, bad = Bus(words), Bus(words)
        model(correct, 0x1000, 0x0ffc)
        model(bad, 0x1000, 0x0ffc, mutation='prefetch')
        self.assertEqual(correct.words[0x1004], 0)
        self.assertEqual(bad.words[0x1004], 1)
        self.assertNotEqual(correct.events, bad.events)

    def test_wrap_and_mmio_alias(self):
        bus = Bus({0xfffffffc: 0x1234, CONTROL: 0x87654321})
        self.assertEqual(model(bus, 0x2005, 0xfffffffc), 0x2000)
        self.assertEqual(bus.events[4:6], [('r', 0xfffffffc, 0x1234), ('w', 0x2000, 0x1234)])
        self.assertIn(('r', 0, 0), bus.events)
        # Destination aliases status/control, and the later loads see those writes.
        bus = Bus({0x1000+i: 0 for i in range(0, 256, 4)})
        model(bus, 0x400220ff, 0x1000)
        self.assertIn(('w', STATUS, 0), bus.events)
        self.assertIn(('w', CONTROL, 0), bus.events)
        self.assertEqual(bus.words[CONTROL], 0x200000)
        # Source aliases control: first RMW value is read as data at offset 0x10.
        bus = Bus({CONTROL: 0x40})
        model(bus, 0x3000, 0x40022000)
        self.assertEqual(bus.words[0x3010], 0x10040)

    def test_fictional_arguments(self):
        # Fictional inputs; the established call instruction proves no runtime arguments.
        a0, a1 = 0x9c0a, 0x2000
        bus = Bus()
        self.assertEqual(model(bus, a0, a1), 0x9c00)
        self.assertIn(('w', 0x9c00, 0), bus.events)


if __name__ == '__main__':
    unittest.main()
