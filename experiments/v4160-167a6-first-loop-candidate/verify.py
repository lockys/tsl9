"""Offline image pin and synthetic model tests; never executes C or firmware."""
import hashlib
from pathlib import Path
import unittest

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CANDIDATES = {'candidate.c': '2ca6d73f9d3087a40d184d393397042bc83a32b20b8696e6e0cd740e2c8dacc8',
              'candidate.h': '9f372bc067d2cdfa7f8c7b1e55e0e953ae1e3d0e222f460b90abb91d88c98f1b'}
START = 0x167a6 - 0x8000
WINDOW = bytes.fromhex('01 11 22 cc 26 ca 4a c8 4e c6 06 ce 52 c4 56 c2 aa 84 01 44 93 89 01 06 13 09 e0 0f 83 a7 09 00 a2 97 03 c7 07 00 63 16 97 00 03 c5 17 00 ef e0 df df 09 04 e3 14 24 ff')


def check_window(data):
    if data[START:START + len(WINDOW)] != WINDOW:
        raise ValueError('window mismatch')


def check_image(data):
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('image mismatch')
    check_window(data)


def model(event, snapshot, read, dispatch):
    for offset in range(0, 254, 2):
        pointer = snapshot()
        if read(pointer, offset) == event:
            dispatch(read(pointer, offset + 1))


class Verify(unittest.TestCase):
    def test_pin(self):
        data = IMAGE.read_bytes()
        check_image(data)
        for name, digest in CANDIDATES.items():
            source = Path(__file__).with_name(name).read_bytes()
            self.assertEqual(hashlib.sha256(source).hexdigest(), digest)
            self.assertNotEqual(hashlib.sha256(source + b'\0').hexdigest(), digest)
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

    def test_mutating_callbacks_and_duplicate_matches(self):
        tables = {'A': bytearray(254), 'B': bytearray(254)}
        tables['A'][0:2] = bytes([7, 11])
        tables['B'][2:4] = bytes([7, 22])
        tables['A'][252:254] = bytes([7, 33])
        state = {'slot': 'A'}
        trace = []

        def snapshot():
            pointer = state['slot']
            trace.append(('snapshot', pointer))
            return pointer

        def read(pointer, offset):
            value = tables[pointer][offset]
            trace.append(('read', pointer, offset, value))
            if offset == 0:
                state['slot'] = 'B'  # value read must still use A
                tables['A'][1] = 12  # value is read after the key callback
            return value

        def dispatch(value):
            trace.append(('dispatch', value))
            if value == 22:
                state['slot'] = 'A'  # next iteration reloads the slot

        model(7, snapshot, read, dispatch)
        expected = []
        for offset in range(0, 254, 2):
            pointer = 'A' if offset == 0 or offset >= 4 else 'B'
            key = 7 if offset in (0, 2, 252) else 0
            expected.extend([('snapshot', pointer), ('read', pointer, offset, key)])
            if key == 7:
                value = {0: 12, 2: 22, 252: 33}[offset]
                expected.extend([('read', pointer, offset + 1, value), ('dispatch', value)])
        self.assertEqual(trace, expected)

    def test_snapshot_and_last_dispatch_boundaries(self):
        table = bytearray(254)
        table[0:2] = bytes([9, 0x80])
        table[252:254] = bytes([9, 0xff])
        state = {'snapshots': 0, 'dispatches': []}
        def snapshot():
            state['snapshots'] += 1
            if state['snapshots'] == 1:
                table[1] = 0xfe
            return table
        def dispatch(value):
            state['dispatches'].append(value)
            if len(state['dispatches']) == 2:
                table[0] = 0
        model(9, snapshot, lambda ptr, off: ptr[off], dispatch)
        self.assertEqual(state['snapshots'], 127)
        self.assertEqual(state['dispatches'], [0xfe, 0xff])
        self.assertEqual(table[0], 0)

    def test_all_byte_events_and_full_width(self):
        table = bytes(x for i in range(127) for x in (i * 2, i))
        for event in list(range(256)) + [256, 257, 0x10000, 0x80000000, 0xffffffff]:
            trace = []
            def snapshot():
                trace.append(('s',))
                return table
            def read(pointer, offset):
                trace.append(('r', offset))
                return pointer[offset]
            def dispatch(value):
                trace.append(('d', value))
            model(event, snapshot, read, dispatch)
            expected = []
            for i in range(127):
                expected.extend([('s',), ('r', 2 * i)])
                if event == 2 * i:
                    expected.extend([('r', 2 * i + 1), ('d', i)])
            self.assertEqual(trace, expected, hex(event))


if __name__ == '__main__':
    unittest.main()
