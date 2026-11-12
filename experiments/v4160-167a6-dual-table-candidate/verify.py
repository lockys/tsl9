"""Offline pins and synthetic behavioral tests; never compile or execute C."""
import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
DIGEST = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SOURCES = {'candidate.c': '3ec9f2f2dee8313c9ef5e5f82f01ed21f6b5af8bcca33644407c0a06018c6419', 'candidate.h': 'f4f27dd828de497eec73bdb2a0ed26ac0d37f165b903712d219d26c6270e3769'}
START = 0x167de - 0x8000
WINDOW = bytes.fromhex('9d 4a 05 44 93 89 41 06 13 8a 81 06 13 09 40 02 03 a7 09 00 56 97 83 46 07 00 03 47 17 00 93 77 17 00 a2 07 d5 8f 63 98 97 00 09 8b 09 c7 a2 85 01 45 ef 10 a0 17 03 27 0a 00 56 97 83 46 07 00 03 47 17 00 93 77 17 00 a2 07 d5 8f 63 98 f4 00 09 8b 09 c7 a2 85 05 45 ef 10 40 15 05 04 13 74 f4 0f 9d 0a e3 16 24 fb')


def check_window(data):
    if data[START:START + len(WINDOW)] != WINDOW:
        raise ValueError('window mismatch')


def check_image(data):
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != DIGEST:
        raise ValueError('image mismatch')
    check_window(data)


def check_source(data, digest):
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('source mismatch')


def model(event, snapshot, read, dispatch):
    for index in range(1, 36):
        for table in range(2):
            pointer = snapshot(table)
            low = read(pointer, index * 7)
            high = read(pointer, index * 7 + 1)
            if low | ((high & 1) << 8) == event and high & 2:
                dispatch(table, index)


class Tests(unittest.TestCase):
    def test_pins_and_mutations(self):
        data = IMAGE.read_bytes()
        self.assertEqual(len(WINDOW), 0x68)
        check_image(data)
        for i in range(len(WINDOW)):
            for bit in range(8):
                bad = bytearray(data)
                bad[START + i] ^= 1 << bit
                with self.assertRaises(ValueError):
                    check_window(bad)
        for bad in (data[:-1], data + b'\0', data[:START - 1] + bytes([data[START - 1] ^ 1]) + data[START:]):
            with self.assertRaises(ValueError):
                check_image(bad)
        with self.assertRaises(ValueError):
            check_window(data[:START + len(WINDOW) - 1])
        for name, digest in SOURCES.items():
            source = Path(__file__).with_name(name).read_bytes()
            check_source(source, digest)
            with self.assertRaises(ValueError):
                check_source(source + b'\0', digest)

    def test_exhaustive_fields_and_full_event(self):
        for low in (0, 1, 127, 255):
            for high in range(256):
                key = low | ((high & 1) << 8)
                for event in (key, key ^ 256, key + 512, 0xffffffff):
                    trace = []
                    def snapshot(t):
                        trace.append(('s', t))
                        return t
                    def read(t, off):
                        trace.append(('r', t, off))
                        return (low if off == 7 else high) if t == 0 and off in (7, 8) else 0
                    def dispatch(t, i):
                        trace.append(('d', t, i))
                    model(event, snapshot, read, dispatch)
                    expected = []
                    for i in range(1, 36):
                        for t in range(2):
                            expected.extend([('s', t), ('r', t, 7*i), ('r', t, 7*i+1)])
                            if t == 0 and i == 1 and event == key and high & 2:
                                expected.append(('d', t, i))
                    self.assertEqual(trace, expected)

    def test_mutation_and_latched_high(self):
        tables = {name: bytearray(253) for name in ('a', 'b', 'c')}
        tables['a'][7:9] = bytes((5, 3))
        tables['b'][7:9] = bytes((5, 1))
        tables['c'][7:9] = bytes((5, 3))
        tables['c'][245:247] = bytes((5, 3))
        slots = ['a', 'b']
        trace = []
        def snapshot(t):
            trace.append(('s', t, slots[t]))
            return slots[t]
        def read(p, off):
            value = tables[p][off]
            trace.append(('r', p, off, value))
            if p == 'a' and off == 7:
                slots[0] = 'c'  # high remains read from a
            if p == 'a' and off == 8:
                tables['a'][8] = 0  # flag uses returned high, no reread
            return value
        def dispatch(t, i):
            trace.append(('d', t, i))
            if (t, i) == (0, 1):
                slots[1] = 'c'  # second slot must not have been preloaded
        model(261, snapshot, read, dispatch)
        self.assertEqual(trace[:8], [('s', 0, 'a'), ('r', 'a', 7, 5), ('r', 'a', 8, 3), ('d', 0, 1), ('s', 1, 'c'), ('r', 'c', 7, 5), ('r', 'c', 8, 3), ('d', 1, 1)])
        self.assertEqual([x for x in trace if x[0] == 'd'], [('d', 0, 1), ('d', 1, 1), ('d', 0, 35), ('d', 1, 35)])
        self.assertEqual(len([x for x in trace if x[0] == 's']), 70)
        self.assertEqual(len([x for x in trace if x[0] == 'r']), 140)


if __name__ == '__main__':
    unittest.main()
