#!/usr/bin/env python3
"""Fresh builds and mutations of their actual ELF records, no target execution."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from types import ModuleType


def load_probe(path):
    path = Path(path).resolve()
    source = path.read_bytes()
    module = ModuleType('probe')
    module.__file__ = str(path)
    previous = sys.modules.get('probe')
    sys.modules['probe'] = module
    try:
        exec(compile(source, str(path), 'exec'), module.__dict__)
    except BaseException:
        if previous is None:
            del sys.modules['probe']
        else:
            sys.modules['probe'] = previous
        raise
    return module


p = load_probe(Path(__file__).resolve().with_name('probe.py'))


class SourceLoadingTests(unittest.TestCase):
    def test_timestamp_cache_is_not_used(self):
        # This fixture alone creates a cache, entirely inside an isolated directory.
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / 'test_probe.py').write_bytes(Path(__file__).read_bytes())
            script = '''import importlib.util, json, os, py_compile, runpy, sys
from pathlib import Path
from unittest.mock import patch
root = Path(sys.argv[1])
source = root / 'probe.py'
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
    spec = importlib.util.spec_from_file_location('control_probe', str(source))
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    ns = runpy.run_path(str(root / 'test_probe.py'), run_name='isolated_test')
    module = ns['p']
    with patch('probe.MARKER', 'patched'):
        patched = module.marker()
    results.append([control.marker(), module.marker(), patched,
                    module.__file__ == str(source), module.__name__,
                    module.marker.__globals__ is module.__dict__,
                    sys.modules['probe'] is module,
                    module.marker.__code__.co_filename == str(source),
                    len(contents(value)) == len(contents('old')),
                    int(source.stat().st_mtime), cache.read_bytes() == original_cache])
print(json.dumps(results))
'''
            env = dict(__import__('os').environ)
            env.pop('PYTHONPYCACHEPREFIX', None)
            cmd = [sys.executable] + (['-O'] if sys.flags.optimize else []) + ['-B', '-c', script, str(d)]
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=True)
            self.assertEqual(json.loads(result.stdout),
                             [['old', value, 'patched', True, 'probe', True, True, True,
                               True, 1700000000, True] for value in ('new', 'alt')])


class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader = staticmethod(p.load_reader())
        cls.tmp = tempfile.TemporaryDirectory(dir=p.HERE, prefix='test-')
        cls.d = Path(cls.tmp.name)
        cls.clang, cls.lld = p.toolpaths(p.NDK)
        source = p.pinned((p.HERE / 'leaf.c').read_bytes(), 'source')
        cls.obj = p.build(cls.d, cls.clang, cls.lld, 'c', source).read_bytes()
        # link() requires the object on disk; save both independent final snapshots.
        cls.good = p.link(cls.d, cls.lld, cls.d / 'leaf.o', p.TARGET).read_bytes()
        cls.bad = p.link(cls.d, cls.lld, cls.d / 'leaf.o', p.TARGET + 0x1000).read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def reject(self, data, checker, message):
        with self.assertRaisesRegex(ValueError, message):
            checker(self.reader(bytes(data)))

    def rel(self, row, word, value):
        e = self.reader(self.obj); b = bytearray(self.obj)
        s = e.section('.rela.leaf')
        struct.pack_into('<I', b, s['offset'] + row * 12 + word * 4, value)
        return b

    def symbol(self, source, name, offset, fmt, value):
        e = self.reader(source); b = bytearray(source)
        table = e.section('.symtab'); s = p.sym(e, name)
        struct.pack_into(fmt, b, table['offset'] + 16*s['index'] + offset, value)
        return b

    def section(self, source, name, offset, value):
        e = self.reader(source); b = bytearray(source)
        struct.pack_into('<I', b, e.header[5] + 40*e.section(name)['index'] + offset, value)
        return b

    def test_full_fresh_subprocess(self):
        cmd = [sys.executable] + (['-O'] if sys.flags.optimize else []) + ['-B', str(p.HERE / 'probe.py')]
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        cases = json.loads(r.stdout)['cases']
        self.assertEqual([(c['language'], c['data_address'], c['bytes'], c['matches_original']) for c in cases],
                         [(lang, hex(addr), raw.hex(), match) for lang in ('c', 'c++')
                          for addr, raw, match in ((p.TARGET, p.ORIGINAL, True), (p.TARGET + 0x1000, p.WRONG, False))])

    def test_reference_and_pins(self):
        self.assertEqual(p.reference(p.BIN.read_bytes()), p.ORIGINAL)
        for data in (b'', b'bad', p.BIN.read_bytes()[:-1]):
            with self.assertRaisesRegex(ValueError, 'bin SHA-256'): p.reference(data)
        for name in ('reader', 'clang', 'lld', 'source'):
            with self.assertRaisesRegex(ValueError, 'SHA-256'): p.pinned(b'', name)

    def test_valid(self):
        p.object_check(self.reader(self.obj))
        p.final_check(self.reader(self.good), p.TARGET, p.ORIGINAL)
        p.final_check(self.reader(self.bad), p.TARGET + 0x1000, p.WRONG)
        with self.assertRaisesRegex(ValueError, 'final ABS data symbol'):
            p.final_check(self.reader(self.bad), p.TARGET, p.ORIGINAL)
        with self.assertRaisesRegex(ValueError, 'final exact bytes'):
            p.final_check(self.reader(self.bad), p.TARGET + 0x1000, p.ORIGINAL)

    def test_object_relocation_mutations(self):
        e = self.reader(self.obj)
        anchor = p.sym(e, '.Lpcrel_hi0')['index']; data = p.sym(e, 'status_byte')['index']
        for b in (self.rel(0, 2, 1), self.rel(1, 2, 1),
                  self.rel(0, 1, (data << 8) | 26), self.rel(1, 1, (data << 8) | 24),
                  self.rel(0, 1, (anchor << 8) | 23), self.rel(1, 0, 0)):
            self.reject(b, p.object_check, 'object relocations')
        self.reject(self.section(self.obj, '.rela.leaf', 20, 0), p.object_check, 'object relocation section')
        self.reject(self.section(self.obj, '.rela.leaf', 28, 2), p.object_check, 'object relocation section')

    def test_object_symbols_and_sections(self):
        e = self.reader(self.obj); b = bytearray(self.obj)
        table = e.section('.strtab'); at = b.find(b'status_byte\0', table['offset'], table['offset'] + table['size'])
        self.assertGreaterEqual(at, 0); b[at] = ord('x')
        self.reject(b, p.object_check, 'symbol status_byte count')
        self.reject(self.symbol(self.obj, 'status_byte', 13, 'B', 0), p.object_check, 'object data symbol')
        self.reject(self.symbol(self.obj, '.Lpcrel_hi0', 4, '<I', 4), p.object_check, 'object anchor')
        self.reject(self.symbol(self.obj, '.Lpcrel_hi0', 12, 'B', 0x10), p.object_check, 'object anchor')
        self.reject(self.symbol(self.obj, 'get_status', 8, '<I', 0), p.object_check, 'object FUNC')
        self.reject(self.section(self.obj, '.leaf', 8, 2), p.object_check, 'leaf section')
        self.reject(self.section(self.obj, '.leaf', 20, 0), p.object_check, 'leaf section')
        self.reject(self.section(self.obj, '.symtab', 20, 0), p.object_check, 'RELA symbol index')
        # Mutate opcode, destination/source registers, ret and unrelocated immediates
        # directly in the fresh ELF's leaf bytes.
        e = self.reader(self.obj); off = e.section('.leaf')['offset']
        for byte, mask, message in ((0, 1, 'object AUIPC opcode/register'),
                                    (1, 1, 'object AUIPC opcode/register'),
                                    (4, 1, 'object LBU opcode/registers'),
                                    (5, 1, 'object LBU opcode/registers'),
                                    (6, 1, 'object LBU opcode/registers'),
                                    (8, 1, 'object ret opcode/register'),
                                    (9, 1, 'object ret opcode/register'),
                                    (2, 1, 'object instruction bytes'),
                                    (7, 0x10, 'object instruction bytes')):
            b = bytearray(self.obj); b[off + byte] ^= mask
            self.reject(b, p.object_check, message)

    def test_abi_and_null_symbol_raw_mutations(self):
        for source, checker, label in ((self.obj, p.object_check, 'object'),
                                       (self.good, lambda e: p.final_check(e, p.TARGET, p.ORIGINAL), 'final')):
            for flags in (0, 3, 5, 9, 0x11, 0x80000001):
                b = bytearray(source); struct.pack_into('<I', b, 36, flags)
                self.reject(b, checker, label + ' ABI e_flags')
            e = self.reader(source); off = e.section('.symtab')['offset']
            self.assertEqual(source[off:off + 16], bytes(16))
            for byte in range(16):
                b = bytearray(source); b[off + byte] = 1
                # Invalid string or section indices may be rejected by the reader first.
                message = ('ELF string offset' if byte in (1, 2, 3) else
                           'symbol section index' if byte == 15 else 'null symbol 0')
                with self.subTest(artifact=label, byte=byte): self.reject(b, checker, message)

    def test_final_alloc_overlap(self):
        check = lambda e: p.final_check(e, p.TARGET, p.ORIGINAL)
        e = self.reader(self.good); leaf = e.section('.leaf')
        pos = e.header[5] + 40 * e.section('.text')['index']
        def mutate(fields):
            b = bytearray(self.good)
            for offset, value in fields: struct.pack_into('<I', b, pos + offset, value)
            return b
        # Nonempty, file-backed section: separately alias VMA and file.
        self.reject(mutate(((12, p.PC + 9), (20, 1))), check, 'final alloc VMA overlap')
        self.reject(mutate(((16, leaf['offset'] + 9), (20, 1))), check, 'final alloc file overlap')
        self.reject(mutate(((12, 0xffffffff), (20, 2))), check, 'final alloc VMA extent')
        # NOBITS still has a VMA but does not occupy file bytes.
        self.reject(mutate(((4, 8), (12, p.PC), (20, 1))), check, 'final alloc VMA overlap')
        p.final_check(self.reader(mutate(((4, 8), (16, leaf['offset']), (20, 1)))), p.TARGET, p.ORIGINAL)
        # Adjacent nonempty extents do not overlap.
        p.final_check(self.reader(mutate(((20, 1),))), p.TARGET, p.ORIGINAL)

    def test_entry_rejects_skipped_and_zero_tests(self):
        path = str(p.HERE / 'test_probe.py')
        for suite in ('zero', 'skipped', 'mixed'):
            script = '''import runpy, sys, unittest
class T(unittest.TestCase):
    def test_ok(self): pass
    @unittest.skip('synthetic skip')
    def test_skip(self): pass
kind, path = sys.argv[1:]
sys.path.insert(0, __import__('os').path.dirname(path))
tests = {'zero': [], 'skipped': [T('test_skip')], 'mixed': [T('test_ok'), T('test_skip')]}[kind]
unittest.defaultTestLoader.loadTestsFromModule = lambda *a, **k: unittest.TestSuite(tests)
sys.argv = [path]
runpy.run_path(path, run_name='__main__')
'''
            cmd = [sys.executable] + (['-O'] if sys.flags.optimize else []) + ['-B', '-c', script, suite, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            with self.subTest(suite=suite):
                self.assertNotEqual(result.returncode, 0, result.stderr)
                self.assertIn('zero tests or skipped tests', result.stderr)

    def test_final_mutations(self):
        check = lambda e: p.final_check(e, p.TARGET, p.ORIGINAL)
        self.reject(self.symbol(self.good, 'status_byte', 4, '<I', p.TARGET + 1), check, 'final ABS data symbol')
        self.reject(self.symbol(self.good, 'get_status', 14, '<H', 2), check, 'final FUNC')
        self.reject(self.section(self.good, '.leaf', 12, p.PC + 2), check, 'leaf section')
        self.reject(self.symbol(self.good, 'get_status', 14, '<H', 0), check, 'final FUNC')
        b = bytearray(self.good); struct.pack_into('<I', b, 52, 1)
        self.reject(b, check, 'final EXEC/no PT_LOAD')
        b = bytearray(self.good); e = self.reader(b); b[e.section('.leaf')['offset'] + 4] ^= 1
        self.reject(b, check, 'final exact bytes')
        # Turn a harmless named symbol undefined and add an empty RELA section.
        self.reject(self.symbol(self.good, '$x.0', 14, '<H', 0), check, 'final undefined symbol')
        e = self.reader(self.good); b = bytearray(self.good)
        pos = e.header[5] + 40 * e.section('.text')['index']
        for off, value in ((4, 4), (24, e.section('.symtab')['index']),
                           (28, e.section('.leaf')['index']), (36, 12)):
            struct.pack_into('<I', b, pos + off, value)
        self.reject(b, check, 'final relocations')

    def test_empty_and_compile_failure(self):
        for b in (b'', bytes(52)):
            with self.assertRaises(ValueError): self.reader(b)
        with self.assertRaises(RuntimeError):
            p.build(self.d, self.clang, self.lld, 'c', b'this is not valid C;')
        with self.assertRaises(RuntimeError):
            p.run([self.lld, '--definitely-invalid-option'])


if __name__ == '__main__':
    result = unittest.main(verbosity=2, exit=False).result
    if result.testsRun == 0 or result.skipped:
        print('FAIL: zero tests or skipped tests', file=sys.stderr)
        sys.exit(1)
    sys.exit(0 if result.wasSuccessful() else 1)
