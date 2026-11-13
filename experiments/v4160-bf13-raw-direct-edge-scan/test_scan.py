#!/usr/bin/env python3
"""Independent synthetic and pinned-image tests; standard library only."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
import unittest
from unittest import mock


def load_scan(path):
    path = Path(path).resolve()
    source = path.read_bytes()
    module = ModuleType('scan')
    module.__file__ = str(path)
    missing = object()
    previous = sys.modules.get('scan', missing)
    sys.modules['scan'] = module
    try:
        exec(compile(source, str(path), 'exec'), module.__dict__)
    except BaseException:
        if previous is missing:
            del sys.modules['scan']
        else:
            sys.modules['scan'] = previous
        raise
    return module


scan = load_scan(Path(__file__).resolve().with_name('scan.py'))


def encode(displacement, rd):
    """Construct J-type words from architectural immediate bit positions."""
    if displacement % 2 or not -(1 << 20) <= displacement <= (1 << 20) - 2:
        raise ValueError("invalid J displacement")
    imm = displacement & 0x1fffff
    return ((imm & 0x100000) << 11 | (imm & 0xff000) |
            (imm & 0x800) << 9 | (imm & 0x7fe) << 20 |
            rd << 7 | 0x6f).to_bytes(4, "little")


class ScanTests(unittest.TestCase):
    def test_timestamp_cache_is_not_used(self):
        # The only cache created by this test is inside the isolated directory.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'test_scan.py').write_bytes(Path(__file__).read_bytes())
            script = '''import importlib.util, json, os, py_compile, runpy, sys
from pathlib import Path
from unittest.mock import patch
root = Path(sys.argv[1])
source = root / 'scan.py'
def contents(value):
    return ("MARKER = '%s'\\ndef marker(): return MARKER\\n" % value).encode('ascii')
source.write_bytes(contents('old'))
os.utime(str(source), (1700000000, 1700000000))
cache = Path(importlib.util.cache_from_source(str(source)))
py_compile.compile(str(source), cfile=str(cache), doraise=True,
                   optimize=sys.flags.optimize,
                   invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
original_cache = cache.read_bytes()
results = []
for value in ('new', 'alt'):
    source.write_bytes(contents(value))
    os.utime(str(source), (1700000000, 1700000000))
    spec = importlib.util.spec_from_file_location('control_scan', str(source))
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    ns = runpy.run_path(str(root / 'test_scan.py'), run_name='isolated_test')
    module = ns['scan']
    with patch('scan.MARKER', 'patched'):
        patched = module.marker()
    results.append([control.marker(), module.marker(), patched,
                    module.__file__ == str(source), module.__name__,
                    module.marker.__globals__ is module.__dict__,
                    sys.modules['scan'] is module,
                    module.marker.__code__.co_filename == str(source),
                    len(contents(value)) == len(contents('old')),
                    int(source.stat().st_mtime), cache.read_bytes() == original_cache])
print(json.dumps(results))
'''
            env = dict(__import__('os').environ)
            env.pop('PYTHONPYCACHEPREFIX', None)
            cmd = [sys.executable] + (['-O'] if sys.flags.optimize else []) + ['-B', '-c', script, str(root)]
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
            self.assertEqual(json.loads(result.stdout),
                             [['old', value, 'patched', True, 'scan', True, True, True,
                               True, 1700000000, True] for value in ('new', 'alt')])

    def test_forward_backward_rd_and_halfword(self):
        # PC 0x1002 is 2-byte but not 4-byte aligned.
        data = b'\x00\x00' + encode(0x802, 1) + encode(-0x1002, 0)
        hits, count = scan.scan(data, 0x1000, {0x1804, 0x4})
        self.assertEqual(count, 4)
        self.assertEqual([(h.offset, h.rd, h.displacement, h.target) for h in hits],
                         [(2, 1, 0x802, 0x1804), (6, 0, -0x1002, 4)])

    def test_extremes_and_modulo(self):
        for disp in (-(1 << 20), (1 << 20) - 2):
            with self.subTest(disp=disp):
                target = (0xfffffffe + disp) & 0xffffffff
                hits, count = scan.scan(encode(disp, 31), 0xfffffffe, {target})
                self.assertEqual(count, 1)
                self.assertEqual((hits[0].displacement, hits[0].rd, hits[0].target),
                                 (disp, 31, target))
        self.assertEqual(scan.scan(encode(2, 0), 0xfffffffe, {0})[0][0].target, 0)
        self.assertEqual(scan.scan(encode(-2, 0), 0, {0xfffffffe})[0][0].target, 0xfffffffe)

    def test_known_instruction_words(self):
        self.assertEqual(encode(-12314, 1).hex(), 'efc07ffe')
        self.assertEqual(encode(-41238, 0).hex(), '6f50bfee')
        self.assertEqual(encode(0, 1).hex(), 'ef000000')
        self.assertEqual(encode(2, 0).hex(), '6f002000')

    def test_overlapping_windows_and_truncation(self):
        # Two valid raw patterns overlap by two bytes. Neither is classified as code.
        data = bytes.fromhex('6f006f000000')
        hits, count = scan.scan(data, 0, {0xf0006, 2})
        self.assertEqual(count, 2)
        self.assertEqual([(h.offset, h.word, h.target) for h in hits],
                         [(0, 0x006f006f, 0xf0006), (2, 0x0000006f, 2)])
        self.assertEqual(scan.scan(data[:-1], 0, {0xf0006, 2})[1], 1)
        self.assertEqual(scan.scan(b'\x6f\x00\x00', 0, {0}) , ((), 0))
        # A pattern starting at an odd byte is not scanned.
        self.assertEqual(scan.scan(b'\x00' + encode(0, 0), 0, {1})[0], ())
        self.assertEqual(scan.scan(b'\x6e\x00\x00\x00', 0, {0})[0], ())

    def test_pin_rejects_wrong_hash_length_and_oversized(self):
        data = scan.BIN.read_bytes()
        scan.check_pin(data)
        for wrong in (bytes(len(data)), data[:-1], data + b'\0', bytes([data[0] ^ 1]) + data[1:]):
            with self.subTest(length=len(wrong)), self.assertRaises(ValueError):
                scan.check_pin(wrong)

    def test_incomplete_zero_missing_extra_and_changed(self):
        n = scan.SIZE // 2 - 1
        scan.check_result(scan.EXPECTED, n)
        cases = [(scan.EXPECTED, 0), (scan.EXPECTED, n - 1), ((), n),
                 (scan.EXPECTED[:-1], n),
                 (scan.EXPECTED + (scan.Hit(0, 0x6f, 0, 0, 0xbd5a),), n),
                 ((scan.EXPECTED[0]._replace(rd=0),) + scan.EXPECTED[1:], n)]
        for hits, count in cases:
            with self.subTest(hits=hits, count=count), self.assertRaises(ValueError):
                scan.check_result(hits, count)

    def test_wrong_bin_fails_before_scan(self):
        with mock.patch.object(scan.BIN.__class__, 'open', mock.mock_open(read_data=bytes(scan.SIZE))), \
             mock.patch.object(scan, 'scan') as scan_mock:
            with self.assertRaisesRegex(ValueError, 'SHA-256'):
                scan.main()
            scan_mock.assert_not_called()

    def test_main_reports_changed_hits_before_failing(self):
        extra = scan.Hit(0, 0x6f, 0, 0, 0xbd5a)
        for hits in (scan.EXPECTED[:-1], scan.EXPECTED + (extra,)):
            with self.subTest(hits=hits), \
                 mock.patch.object(scan.BIN.__class__, 'open', mock.mock_open(read_data=b'')), \
                 mock.patch.object(scan, 'check_pin'), \
                 mock.patch.object(scan, 'scan', return_value=(hits, scan.SIZE // 2 - 1)):
                output = io.StringIO()
                with contextlib.redirect_stdout(output), self.assertRaisesRegex(ValueError, 'hit set changed'):
                    scan.main()
                self.assertEqual(output.getvalue().count('offset='), len(hits))
                if extra in hits:
                    self.assertIn('offset=0x00000', output.getvalue())
                self.assertNotIn('snapshot verified', output.getvalue())

    def test_real_bin_cli_exact_normal_and_optimized(self):
        expected = (
            'raw JAL-pattern scan: size=76800 sha256=0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667 base=0x00008000 windows=38399\n'
            'offset=0x06d74 pc=0x0000ed74 word=0xfe7fc0ef rd=x1 displacement=-12314 target=0x0000bd5a\n'
            'offset=0x0de5a pc=0x00015e5a word=0xf0bf50ef rd=x1 displacement=-41206 target=0x0000bd64\n'
            'offset=0x0de70 pc=0x00015e70 word=0xeebf506f rd=x0 displacement=-41238 target=0x0000bd5a\n'
            'offset=0x0de80 pc=0x00015e80 word=0xedbf506f rd=x0 displacement=-41254 target=0x0000bd5a\n'
            'offset=0x0de90 pc=0x00015e90 word=0xecbf506f rd=x0 displacement=-41270 target=0x0000bd5a\n'
            'exact raw hit snapshot verified; matches are not proven callers\n')
        for flag in ([], ['-O']):
            with self.subTest(flag=flag):
                result = subprocess.run([sys.executable, '-B', *flag, str(scan.Path(scan.__file__))],
                                        capture_output=True, text=True, check=False)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, expected, ''))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ScanTests)
    if suite.countTestCases() != 10:
        raise SystemExit('incomplete or zero tests')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not (result.wasSuccessful() and result.testsRun == 10 and
                  not result.skipped and not result.expectedFailures))
