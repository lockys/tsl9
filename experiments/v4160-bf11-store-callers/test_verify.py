#!/usr/bin/env python3
import io
import json
import subprocess
import sys
import unittest
from unittest import mock

import verify as v


def jal(rd, displacement):
    if displacement % 2 or not -(1 << 20) <= displacement < (1 << 20):
        raise ValueError('invalid JAL displacement')
    n = displacement & ((1 << 21) - 1)
    word = ((n >> 20) << 31 | ((n >> 1) & 0x3ff) << 21 |
            ((n >> 11) & 1) << 20 | ((n >> 12) & 0xff) << 12 | rd << 7 | 0x6f)
    return word.to_bytes(4, 'little')


def flip(data, offset, bit):
    result = bytearray(data)
    result[offset] ^= 1 << bit
    return bytes(result)


class DecoderTests(unittest.TestCase):
    def test_known_instructions_and_widths(self):
        cases = [
            ('17050020', ('auipc', 10, 0x20000000, 4)),
            ('1305b51c', ('addi', 10, 10, 459, 4)),
            ('8280', ('jr', 1, 2)),
            ('8547', ('li', 15, 1, 2)),
            ('23000500', ('sb', 0, 10, 0, 4)),
            ('2300f500', ('sb', 15, 10, 0, 4)),
            ('efc0bfde', ('jal', 1, -0x3216, 4)),
            ('efc03fd1', ('jal', 1, -0x32ee, 4)),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(v.decode(bytes.fromhex(raw)), expected)

    def test_signed_and_jal_direction(self):
        for n in (-1048576, -2, 0, 2, 1048574):
            with self.subTest(n=n):
                self.assertEqual(v.decode(jal(1, n)), ('jal', 1, n, 4))
        self.assertEqual(v.decode(bytes.fromhex('1305f5ff')), ('addi', 10, 10, -1, 4))
        self.assertEqual(v.decode(bytes.fromhex('fd57')), ('li', 15, -1, 2))
        self.assertEqual(v.decode(bytes.fromhex('17050080')), ('auipc', 10, -0x80000000, 4))
        self.assertEqual(v.decode(bytes.fromhex('a30ff5fe')), ('sb', 15, 10, -1, 4))

    def test_truncation_unsupported_and_alignment(self):
        for data in (b'', b'\x13', b'\x13\x05', b'\x13\x05\xb5',
                     b'\x1f\x00', b'\x00\x00', b'\x02\x80',
                     bytes.fromhex('1315b51c'), bytes.fromhex('23100500')):
            with self.subTest(data=data.hex()), self.assertRaises(v.VerificationError):
                v.decode(data)
        with self.assertRaises(v.VerificationError):
            v.sequence(bytes.fromhex('8280'), 1)
        with self.assertRaises(v.VerificationError):
            v.decode(b'\x82\x80', -1)

    def test_address_overflow(self):
        for pc, delta in ((0, -1), (0xffffffff, 1), (-1, 0), (0x100000000, 0)):
            with self.subTest(pc=pc, delta=delta), self.assertRaises(v.VerificationError):
                v.add_address(pc, delta)
        with self.assertRaises(v.VerificationError):
            v.sequence(bytes.fromhex('17050020'), 0xfffffffe)
        self.assertEqual(v.add_address(0xffffffff, 0), 0xffffffff)

    def test_synthetic_windows(self):
        windows = dict(v.WINDOWS)
        result = v.verify_windows(windows)
        self.assertEqual(result['bd46_address'], '0x2000bf11')
        self.assertEqual([x['store_pc'] for x in result['callers']], ['0xef60', '0xf03a'])
        self.assertEqual([x['store_value'] for x in result['callers']], [0, 1])

    def test_semantic_mutations_not_hidden_by_pin(self):
        # Call the window checker directly, not verify_file or a hash gate.
        mutations = [
            (0xbd46, 0, 2),    # AUIPC opcode
            (0xbd46, 1, 0),    # AUIPC rd
            (0xbd46, 2, 4),    # AUIPC immediate
            (0xbd46, 4, 2),    # ADDI opcode
            (0xbd46, 5, 0),    # ADDI rd
            (0xbd46, 6, 3),    # ADDI rs1
            (0xbd46, 7, 4),    # ADDI immediate
            (0xbd46, 8, 7),    # JR register
            (0xef5c, 0, 2),    # JAL opcode
            (0xef5c, 0, 7),    # JAL rd
            (0xef5c, 3, 7),    # JAL direction
            (0xef5c, 2, 5),    # JAL target
            (0xef5c, 4, 2),    # SB opcode
            (0xef5c, 5, 4),    # SB funct3
            (0xef5c, 6, 0),    # SB base register
            (0xef5c, 6, 4),    # SB source register
            (0xef5c, 4, 7),    # SB immediate
            (0xf034, 4, 2),    # C.LI value
            (0xf034, 5, 0),    # C.LI register
            (0xf034, 8, 4),    # SB source register
        ]
        for pc, offset, bit in mutations:
            windows = dict(v.WINDOWS)
            windows[pc] = flip(windows[pc], offset, bit)
            with self.subTest(pc=hex(pc), offset=offset, bit=bit):
                with mock.patch.object(v, 'SHA256', 'irrelevant'):
                    with self.assertRaises(v.VerificationError) as cm:
                        v.verify_windows(windows)
                self.assertNotIn('window bytes differ', str(cm.exception))
        for pc in v.WINDOWS:
            for n in range(len(v.WINDOWS[pc])):
                windows = dict(v.WINDOWS)
                windows[pc] = windows[pc][:n]
                with self.subTest(pc=pc, length=n), self.assertRaises(v.VerificationError):
                    v.verify_windows(windows)

    def test_changed_instruction_widths(self):
        windows = dict(v.WINDOWS)
        windows[0xef5c] = bytes.fromhex('82808280') + windows[0xef5c][4:]
        with self.assertRaises(v.VerificationError):
            v.verify_windows(windows)
        windows = dict(v.WINDOWS)
        windows[0xf034] = windows[0xf034][:4] + bytes.fromhex('13000000') + windows[0xf034][8:]
        with self.assertRaises(v.VerificationError):
            v.verify_windows(windows)

    def test_window_bytes_pin_is_separate(self):
        windows = dict(v.WINDOWS)
        windows[0xef5c] += b'\x00'
        with self.assertRaises(v.VerificationError):
            v.verify_windows(windows)
        with self.assertRaises(v.VerificationError):
            v.verify_windows({})


class InputTests(unittest.TestCase):
    def test_single_bounded_read_and_pin_failures(self):
        class Reader(io.BytesIO):
            def __init__(self, data):
                super().__init__(data)
                self.calls = []
            def read(self, n=-1):
                self.calls.append(n)
                return super().read(n)
        for length in (0, v.SIZE - 1, v.SIZE, v.SIZE + 1, v.SIZE + 100):
            reader = Reader(b'\0' * length)
            with mock.patch('builtins.open', return_value=reader):
                with self.subTest(length=length), self.assertRaises(v.VerificationError):
                    v.read_pinned('synthetic')
            self.assertEqual(reader.calls, [76801])

    def test_runner_rejects_empty_suite(self):
        code = ("import os, sys, runpy, unittest; "
                "sys.path.insert(0, os.path.dirname(%r)); "
                "unittest.defaultTestLoader.loadTestsFromModule = "
                "lambda module: unittest.TestSuite(); "
                "runpy.run_path(%r, run_name='__main__')" % (__file__, __file__))
        flags = ['-O'] if sys.flags.optimize else []
        result = subprocess.run([sys.executable, '-B', *flags, '-c', code],
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('no tests collected', result.stderr)

    def test_cli_failures_have_nonzero_and_no_passed_true(self):
        for args in ([], ['definitely-nonexistent-input.bin']):
            result = subprocess.run([sys.executable, '-B', v.__file__, *args],
                                    capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('"passed": true', result.stdout + result.stderr)
            self.assertIn('error', json.loads(result.stderr))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    if suite.countTestCases() == 0:
        sys.exit('no tests collected')
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if outcome.wasSuccessful() and outcome.testsRun else 1)
