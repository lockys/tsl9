#!/usr/bin/env python3
"""Test the boundary verifier CLI in a disposable tree without running firmware."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path('experiments/v4160-105c4-selected-return-boundaries/verify.py')
IMAGE = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='tsl9-return-cli-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for path in (SCRIPT, IMAGE):
            dst = self.root / path
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes((ROOT / path).read_bytes())

    def invoke(self, *args):
        flags = ['-B'] + (['-O'] if sys.flags.optimize else [])
        return subprocess.run([sys.executable, *flags, str(self.root / SCRIPT), *args],
                              cwd=self.root, stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, timeout=60)

    def test_inspect_and_test(self):
        result = self.invoke('--inspect')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {
            'image_sha256': '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
            'assumed_base': '0x8000',
            'selected_return_sites': ['0x107d8', '0x10848', '0x1095a'],
            'conditional_branch_successors': {'0x107d8': ['0x10810', '0x107da'],
                                             '0x1084a': ['0x10866', '0x1084c'],
                                             '0x1095a': ['0x109bc', '0x1095c']},
            'limits': 'Static selected windows only; return requires normal callee return. No reachability, ABI, complete control flow or firmware execution proof.'})
        tests = self.invoke('--test')
        self.assertEqual(tests.returncode, 0, tests.stderr)
        self.assertIn('Ran 5 tests', tests.stderr)

    def test_invalid_arguments(self):
        for args in ((), ('--bad',), ('--inspect', 'extra'), ('--inspect', '--test')):
            with self.subTest(args=args):
                p = self.invoke(*args)
                self.assertEqual(p.returncode, 2)
                self.assertIn('usage:', p.stderr)
                self.assertEqual(p.stdout, '')

    def test_changed_and_missing_image(self):
        image = self.root / IMAGE
        data = bytearray(image.read_bytes()); data[0] ^= 1; image.write_bytes(data)
        p = self.invoke('--inspect')
        self.assertEqual(p.returncode, 1)
        self.assertIn('FAIL: image SHA-256', p.stderr)
        self.assertEqual(p.stdout, '')
        image.unlink()
        p = self.invoke('--inspect')
        self.assertEqual(p.returncode, 1)
        self.assertIn('FAIL:', p.stderr)
        self.assertEqual(p.stdout, '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
