#!/usr/bin/env python3
"""Exercise the real test entry point with freshly compiled source variants."""
from pathlib import Path
import subprocess
import sys
import unittest


TEST_SCAN = Path(__file__).resolve().with_name('test_scan.py')


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError('fixture anchor is missing or ambiguous')
    return source.replace(old, new, 1)


class RunnerTests(unittest.TestCase):
    def test_entry_point_rejects_incomplete_runs(self):
        source = TEST_SCAN.read_bytes()
        variants = (
            ('empty', b'unittest.defaultTestLoader.loadTestsFromTestCase(ScanTests)',
             b'unittest.TestSuite()', 'incomplete or zero tests'),
            ('all skipped', b'class ScanTests(unittest.TestCase):',
             b'@unittest.skip("fixture skip")\nclass ScanTests(unittest.TestCase):',
             'skipped=10'),
            ('partially skipped', b'    def test_known_instruction_words(self):',
             b'    @unittest.skip("fixture skip")\n    def test_known_instruction_words(self):',
             'skipped=1'),
            ('expected failure', b'    def test_known_instruction_words(self):',
             b'    @unittest.expectedFailure\n    def test_known_instruction_words(self):\n'
             b'        self.fail("fixture expected failure")', 'expected failures=1'),
        )
        # Compile stdin bytes directly: no timestamp-based or stale pyc can be used
        # for a modified test_scan.py, even if source sizes or mtimes coincide.
        bootstrap = (
            'import pathlib, sys; '
            'p = pathlib.Path(sys.argv[1]); '
            'sys.path.insert(0, str(p.parent)); '
            'exec(compile(sys.stdin.buffer.read(), str(p), "exec"), '
            '{"__name__": "__main__", "__file__": str(p)})'
        )
        for flag in ([], ['-O']):
            for name, old, new, evidence in variants:
                with self.subTest(flag=flag, variant=name):
                    modified = replace_once(source, old, new)
                    self.assertNotEqual(modified, source)
                    result = subprocess.run(
                        [sys.executable, '-B', *flag, '-c', bootstrap, str(TEST_SCAN)],
                        input=modified, capture_output=True, check=False)
                    self.assertNotEqual(result.returncode, 0, result.stderr.decode())
                    self.assertIn(evidence, result.stderr.decode())
                    if name != 'empty':
                        self.assertIn('Ran 10 tests', result.stderr.decode())


if __name__ == '__main__':
    unittest.main(verbosity=2)
