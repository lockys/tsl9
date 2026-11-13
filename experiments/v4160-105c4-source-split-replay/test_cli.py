#!/usr/bin/env python3
"""Exercise the source projection CLI in a disposable tree; no firmware execution."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = Path('src/native/receive/feature_state_records.c')
SCRIPT = Path('experiments/v4160-105c4-source-split-replay/verify.py')


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='tsl9-split-cli-')
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.script = root / SCRIPT
        self.source = root / SOURCE
        self.script.parent.mkdir(parents=True)
        self.source.parent.mkdir(parents=True)
        self.script_bytes = (ROOT / SCRIPT).read_bytes()
        self.source_bytes = (ROOT / SOURCE).read_bytes()
        self.script.write_bytes(self.script_bytes)
        self.source.write_bytes(self.source_bytes)

    def invoke(self, *args):
        command = [sys.executable, '-B']
        if sys.flags.optimize:
            command.append('-O')
        return subprocess.run([*command, str(self.script), *args], cwd=self.tmp.name,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)

    def snapshot(self):
        root = Path(self.tmp.name)
        return {p.relative_to(root).as_posix(): (p.stat().st_size, p.stat().st_mtime_ns,
                                                 hashlib.sha256(p.read_bytes()).hexdigest())
                for p in root.rglob('*') if p.is_file()}

    def test_positive_cli_and_unchanged_files(self):
        before = self.snapshot()
        inspect = self.invoke('--inspect')
        self.assertEqual(inspect.returncode, 0, inspect.stderr)
        data = json.loads(inspect.stdout)
        self.assertEqual(data['source_sha256'], '19a1c39ee7831f42960454d02393512520c425ea1ad90f9e08b0f8d4e3b32db3')
        self.assertEqual(data['split_sha256'], 'd7f29f5420dc209f206eb424a527b6c9ed8000eb392ee25a35e2be2b1b90aada')
        self.assertEqual((data['source_bytes'], data['split_bytes'], data['block_offset'],
                          data['block_bytes'], data['declaration_bytes']), (55715, 55450, 5968, 325, 60))
        self.assertIs(data['source_written'], False)
        self.assertEqual(self.snapshot(), before)
        result = self.invoke('--test')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Ran 4 tests', result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.source.read_bytes(), self.source_bytes)
        self.assertEqual(self.script.read_bytes(), self.script_bytes)

    def test_invalid_arguments(self):
        before = self.snapshot()
        for args in ((), ('--bad',), ('--inspect', 'extra'), ('--test', '--inspect')):
            with self.subTest(args=args):
                result = self.invoke(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn('usage:', result.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_changed_and_missing_source(self):
        changed = bytearray(self.source_bytes)
        changed[0] ^= 1
        self.source.write_bytes(changed)
        before = self.snapshot()
        result = self.invoke('--inspect')
        self.assertEqual(result.returncode, 1)
        self.assertIn('FAIL: source SHA-256', result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.source.read_bytes(), changed)
        self.source.unlink()
        before = self.snapshot()
        result = self.invoke('--inspect')
        self.assertEqual(result.returncode, 1)
        self.assertIn('FAIL:', result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.source.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
