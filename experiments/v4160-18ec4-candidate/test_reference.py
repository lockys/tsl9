"""Tests of an independent Python event model, not of candidate.c."""
import hashlib
import unittest
from pathlib import Path

C = 0x40022010
A = 0x40022014
S = 0x4002200c
SOURCE_SHA256 = 'e1d2826c9bed81029380766c46a8a774e09d342b615593f40dba8519db25d99d'


def reference(a0, read, write):
    """Abstract 32-bit event model; callbacks may affect future reads."""
    masked = a0 & 0xffffff00
    first = read(C)
    write(C, first | 0x20000)
    write(A, masked)
    second = read(C)
    write(C, second | 0x40)
    while read(S) & 1:
        pass
    third = read(C)
    write(C, third & 0xfffdffff)
    return masked


class ScriptBus:
    def __init__(self, reads):
        self.reads = iter(reads)
        self.events = []

    def read(self, address):
        expected, value = next(self.reads)
        if address != expected:
            raise ValueError('unexpected read address')
        self.events.append(('r', address, value))
        return value

    def write(self, address, value):
        self.events.append(('w', address, value))


class ReferenceTests(unittest.TestCase):
    def test_source_identity(self):
        source = Path(__file__).with_name('candidate.c').read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_SHA256)

    def test_distinct_reads_and_multiple_polls(self):
        bus = ScriptBus([(C, 0x12340001), (C, 0x80000002),
                         (S, 3), (S, 0xffffffff), (S, 2), (C, 0xffffffff)])
        self.assertEqual(reference(0xabcdefab, bus.read, bus.write), 0xabcdef00)
        self.assertEqual(bus.events, [
            ('r', C, 0x12340001), ('w', C, 0x12360001),
            ('w', A, 0xabcdef00), ('r', C, 0x80000002),
            ('w', C, 0x80000042), ('r', S, 3),
            ('r', S, 0xffffffff), ('r', S, 2),
            ('r', C, 0xffffffff), ('w', C, 0xfffdffff)])
        self.assertEqual(list(bus.reads), [])

    def test_zero(self):
        bus = ScriptBus([(C, 0), (C, 0), (S, 0), (C, 0)])
        self.assertEqual(reference(0, bus.read, bus.write), 0)
        self.assertEqual(bus.events, [('r', C, 0), ('w', C, 0x20000),
            ('w', A, 0), ('r', C, 0), ('w', C, 0x40),
            ('r', S, 0), ('r', C, 0), ('w', C, 0)])

    def test_aliasing_bus(self):
        # All three logical addresses alias one storage cell in this test bus.
        cell = [0]
        events = []
        def read(addr):
            events.append(('r', addr, cell[0]))
            return cell[0]
        def write(addr, value):
            events.append(('w', addr, value))
            cell[0] = value
        self.assertEqual(reference(0x123456ff, read, write), 0x12345600)
        self.assertEqual(events, [('r', C, 0), ('w', C, 0x20000),
            ('w', A, 0x12345600), ('r', C, 0x12345600),
            ('w', C, 0x12345640), ('r', S, 0x12345640),
            ('r', C, 0x12345640), ('w', C, 0x12345640)])

    def test_bounded_observation_of_busy_prefix(self):
        # Observer interrupts the model; this does not prove actual nontermination.
        class StopObservation(Exception):
            pass
        events = []
        def read(addr):
            if addr == S and sum(e[1] == S for e in events) == 4:
                raise StopObservation
            value = 1 if addr == S else 0
            events.append(('r', addr, value))
            return value
        def write(addr, value):
            events.append(('w', addr, value))
        with self.assertRaises(StopObservation):
            reference(0xff, read, write)
        self.assertEqual(events, [('r', C, 0), ('w', C, 0x20000),
            ('w', A, 0), ('r', C, 0), ('w', C, 0x40),
            ('r', S, 1), ('r', S, 1), ('r', S, 1), ('r', S, 1)])


if __name__ == '__main__':
    unittest.main()
