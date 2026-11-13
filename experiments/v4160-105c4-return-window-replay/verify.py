#!/usr/bin/env python3
"""Verify 15 proposed continuation windows against the reference BIN.

Run from any directory with Python 3: verify.py --inspect or verify.py --test.
Run tests separately with Python's -O to check optimized mode. The reference
BIN must exist at the repository-relative path below with its exact digest.
The tests mutate every selected byte in memory and exercise isolated CLI errors.

The 0x8000 image base and instruction boundaries are assumptions. This checks
208 bytes only: it does not compile or link the windows, establish reachability,
caller ABI, data ownership, source authenticity, or complete BIN equivalence.
It does not execute, emulate, flash, or access the target. Successful --inspect
means only this bounded check passed; failures exit nonzero. Python, OS and
filesystem are trust assumptions, and reads are not an atomic snapshot.
See analysis/v4160-105c4-return-continuations-candidates.zh-TW.md.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
WINDOWS = (
    ('S107d8', 0x107d8, '05cd'),
    ('S107da', 0x107da, '83470400b245850793f7f70f63f9b700'),
    ('S107ea', 0x107ea, '2300f400'),
    ('S107ee', 0x107ee, 'f2406244d24405618280'),
    ('S107f8', 0x107f8, '230004000145ef70ffa0'),
    ('S10802', 0x10802, '6244f2402685d24405616ff01ff4'),
    ('S10810', 0x10810, '23000400e9bf'),
    ('C10848', 0x10848, '2a8411cd'),
    ('C1084c', 0x1084c, '0145ef70ff9b'),
    ('C10852', 0x10852, '81461306007d814517050000130565f6ef803f8c'),
    ('C10866', 0x10866, '2285b240224441018280'),
    ('S1095a', 0x1095a, '2dc1'),
    ('S1095c', 0x1095c, '97b7ff1f83c7c765a1cf'),
    ('S10966', 0x10966, '03474400834754008346740022075d8f834764001307870c2285a207d58f93168700420741832183558f9387870c2312e40013978700c207c183a183d98f2313f40083478400b240e5072304f400224441016f200005'),
    ('S109bc', 0x109bc, 'b240224441018280'),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(source):
    chunks = []
    remaining = 76801
    while remaining:
        chunk = source.read(remaining)
        require(isinstance(chunk, bytes) and len(chunk) <= remaining, 'image read')
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    return b''.join(chunks)


def read_image():
    # Unbuffered at the Python layer; allow short reads, bounded to 76801 bytes.
    with IMAGE.open('rb', buffering=0) as source:
        return read_bounded(source)


def verify_identity(image):
    require(len(image) == 76800, 'image length')
    require(hashlib.sha256(image).hexdigest() == SHA256, 'image SHA-256')


def verify_windows(image):
    rows = []
    previous_end = BASE
    for name, address, hex_bytes in WINDOWS:
        expected = bytes.fromhex(hex_bytes)
        require(expected and address >= previous_end and address - BASE + len(expected) <= len(image),
                'window bounds: ' + name)
        require(image[address - BASE:address - BASE + len(expected)] == expected,
                'window bytes: ' + name)
        rows.append({'name': name, 'start': hex(address), 'end': hex(address + len(expected)),
                     'length': len(expected), 'bytes': expected.hex()})
        previous_end = address + len(expected)
    require(len(rows) == 15 and sum(row['length'] for row in rows) == 208, 'window inventory')
    return rows


def inspect(image):
    verify_identity(image)
    return {'scope': 'reference windows only', 'base_assumption': hex(BASE),
            'image_sha256': hashlib.sha256(image).hexdigest(), 'window_count': 15,
            'byte_count': 208, 'windows': verify_windows(image)}


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = read_image()
        verify_identity(cls.image)

    def test_actual_image_and_inventory(self):
        rows = inspect(self.image)['windows']
        # Independent start/end inventory transcribed from the published report.
        expected = (
            ('S107d8', 0x107d8, 0x107da), ('S107da', 0x107da, 0x107ea),
            ('S107ea', 0x107ea, 0x107ee), ('S107ee', 0x107ee, 0x107f8),
            ('S107f8', 0x107f8, 0x10802), ('S10802', 0x10802, 0x10810),
            ('S10810', 0x10810, 0x10816), ('C10848', 0x10848, 0x1084c),
            ('C1084c', 0x1084c, 0x10852), ('C10852', 0x10852, 0x10866),
            ('C10866', 0x10866, 0x10870), ('S1095a', 0x1095a, 0x1095c),
            ('S1095c', 0x1095c, 0x10966), ('S10966', 0x10966, 0x109bc),
            ('S109bc', 0x109bc, 0x109c4),
        )
        self.assertEqual(tuple((r['name'], int(r['start'], 16), int(r['end'], 16))
                               for r in rows), expected)
        self.assertEqual((len(rows), sum(row['length'] for row in rows)), (15, 208))

    def test_each_window_byte_mutation(self):
        count = 0
        for name, address, hex_bytes in WINDOWS:
            for offset in range(len(bytes.fromhex(hex_bytes))):
                changed = bytearray(self.image)
                changed[address - BASE + offset] ^= 1
                with self.subTest(window=name, offset=offset):
                    with self.assertRaisesRegex(ValueError, '^window bytes: ' + name + '$'):
                        verify_windows(bytes(changed))
                count += 1
        self.assertEqual(count, 208)

    def test_bounded_short_reads(self):
        class Source:
            def __init__(self, size):
                self.data = (bytes(range(251)) * (size // 251 + 1))[:size]
                self.returned = 0
                self.requests = []
            def read(self, count):
                self.requests.append(count)
                n = min(count, 257, len(self.data) - self.returned)
                chunk = self.data[self.returned:self.returned + n]
                self.returned += n
                return chunk
        source = Source(1000000)
        self.assertEqual(read_bounded(source), source.data[:76801])
        self.assertEqual(source.returned, 76801)
        self.assertEqual(source.requests[0], 76801)
        self.assertEqual(source.requests[-1], 76801 - 257 * (len(source.requests) - 1))
        source = Source(76800)
        self.assertEqual(read_bounded(source), source.data)
        self.assertEqual(source.returned, 76800)
        source = Source(17)
        self.assertEqual(read_bounded(source), source.data)
        self.assertEqual(source.requests, [76801, 76784])

    def test_invalid_window_inventory(self):
        global WINDOWS
        saved = WINDOWS
        try:
            for case, replacement, error in (
                ('empty', (('S107d8', 0x107d8, ''),) + saved[1:], 'window bounds: S107d8'),
                ('overlap', (saved[0], ('S107da', 0x107d8, saved[1][2])) + saved[2:], 'window bounds: S107da'),
                ('past-end', (('S107d8', BASE + len(self.image), '00'),) + saved[1:], 'window bounds: S107d8'),
                ('missing', saved[:-1], 'window inventory'),
            ):
                WINDOWS = replacement
                with self.subTest(case=case):
                    with self.assertRaisesRegex(ValueError, '^' + error + '$'):
                        verify_windows(self.image)
        finally:
            WINDOWS = saved

    def test_identity_rejects_changed_and_short(self):
        changed = bytearray(self.image)
        changed[0] ^= 1
        with self.assertRaisesRegex(ValueError, '^image SHA-256$'):
            inspect(bytes(changed))
        with self.assertRaisesRegex(ValueError, '^image length$'):
            inspect(self.image[:-1])

    def test_cli_isolated(self):
        with tempfile.TemporaryDirectory(prefix='tsl9-105c4-windows-') as tmp:
            root = Path(tmp)
            script = root / 'experiments/v4160-105c4-return-window-replay/verify.py'
            image = root / IMAGE.relative_to(ROOT)
            script.parent.mkdir(parents=True)
            image.parent.mkdir(parents=True)
            script.write_bytes(Path(__file__).read_bytes())
            image.write_bytes(self.image)
            flags = ['-B'] + (['-O'] if sys.flags.optimize else [])
            def call(*args):
                return subprocess.run([sys.executable, *flags, str(script), *args],
                                      cwd=root, capture_output=True, text=True, timeout=30)
            result = call('--inspect')
            self.assertEqual(result.returncode, 0, result.stderr)
            document = json.loads(result.stdout)
            self.assertEqual((document['window_count'], document['byte_count']), (15, 208))
            for args in ((), ('--bad',), ('--inspect', '--test')):
                result = call(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('expected exactly', json.loads(result.stderr)['error'])
            image.unlink()
            result = call('--inspect')
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(json.loads(result.stderr)['error'].startswith('FileNotFoundError:'))
            image.write_bytes(self.image[:-1])
            result = call('--inspect')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stderr)['error'], 'ValueError: image length')
            image.write_bytes(self.image + bytes(1000000))
            result = call('--inspect')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stderr)['error'], 'ValueError: image length')
            changed = bytearray(self.image)
            changed[0] ^= 1
            image.write_bytes(changed)
            result = call('--inspect')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stderr)['error'], 'ValueError: image SHA-256')


def main():
    if sys.argv[1:] == ['--inspect']:
        print(json.dumps(inspect(read_image()), indent=2))
        return 0
    if sys.argv[1:] == ['--test']:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    raise ValueError('expected exactly --inspect or --test')


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print(json.dumps({'error': type(exc).__name__ + ': ' + str(exc)}), file=sys.stderr)
        sys.exit(1)
