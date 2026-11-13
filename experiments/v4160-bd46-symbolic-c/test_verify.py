#!/usr/bin/env python3
"""Synthetic parsed-record mutations and a fresh offline replay."""
import json
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import unittest
from unittest import mock

import verify as v


def sym(index, name, value, size, info, section, other=0):
    return dict(index=index, name=name, value=value, size=size, info=info,
                other=other, section=section)


class SyntheticELF:
    def __init__(self, linked=False):
        self.header = [2 if linked else 1, 243, 1, 0]
        self.program_headers = [[0] * 8] if linked else []
        self.leaf = dict(index=1, name='.leaf', type=1, flags=6,
                         address=v.ADDR if linked else 0, size=10)
        self.sections = [dict(index=0, type=0), self.leaf,
                         dict(index=2, type=3),
                         dict(index=3, type=2, entsize=16, size=64, link=2)]
        self.symbols = [sym(0, '', 0, 0, 0, 0),
                        sym(1, v.FUNC, v.ADDR if linked else 0, 10, 0x12, 1),
                        sym(2, v.FLAG, v.WITNESS if linked else 0, 0, 0x10,
                            0xfff1 if linked else 0),
                        sym(3, '.Lpcrel_hi0', 0, 0, 0, 1)]
        self.relocations = []
        if not linked:
            self.sections.append(dict(index=4, type=4, info=1, size=24))
            self.relocations = [dict(section=1, offset=0, type=23, symbol=2, addend=0),
                                dict(section=1, offset=4, type=24, symbol=3, addend=0)]
        self.payload = v.REFERENCE

    def section(self, name):
        v.need(name == '.leaf', 'missing section')
        return self.leaf

    def data(self, section):
        return self.payload


def linked_elf_bytes(extra_type=None, duplicate_target=False, symtab_type=2,
                     unresolved=False):
    # Complete bounded ELF32, independent of the pinned parser's record objects.
    strings = b'\0' + v.FUNC.encode() + b'\0' + v.FLAG.encode() + b'\0'
    if unresolved:
        strings += b'unresolved\0'
    names = b'\0.leaf\0.strtab\0.symtab\0.shstrtab\0.extra\0'
    symbols = [struct.pack('<IIIBBH', 0, 0, 0, 0, 0, 0),
               struct.pack('<IIIBBH', 1, v.ADDR, 10, 0x12, 0, 1),
               struct.pack('<IIIBBH', 2 + len(v.FUNC), v.WITNESS, 0, 0x10, 0, 0xfff1)]
    if duplicate_target:
        symbols.append(symbols[-1])
    if unresolved:
        symbols.append(struct.pack('<IIIBBH', strings.index(b'unresolved'), 0, 0, 0x10, 0, 0))
    data = bytearray(b'\0' * 52)
    rows = [(0,) * 10]
    def section(name, typ, flags, addr, content, link=0, entsize=0):
        offset = len(data)
        data.extend(content)
        rows.append((names.index(name.encode() + b'\0'), typ, flags, addr, offset,
                     len(content), link, 0, 1, entsize))
    section('.leaf', 1, 6, v.ADDR, v.REFERENCE)
    section('.strtab', 3, 0, 0, strings)
    section('.symtab', symtab_type, 0, 0, b''.join(symbols), 2, 16)
    section('.shstrtab', 3, 0, 0, names)
    if extra_type is not None:
        # Bounded examples with realistic ELF32 entry sizes, not only empty headers.
        content, link, entsize = {9: (b'\0' * 8, 3, 8),
                                  11: (b''.join(symbols), 2, 16),
                                  19: (struct.pack('<I', v.ADDR + 2), 0, 4)}[extra_type]
        section('.extra', extra_type, 0, 0, content, link, entsize)
    shoff = len(data)
    for row in rows:
        data.extend(struct.pack('<10I', *row))
    struct.pack_into('<16sHHIIIIIHHHHHH', data, 0,
                     b'\x7fELF\x01\x01\x01' + b'\0' * 9, 2, 243, 1, 0,
                     0, shoff, 0, 52, 0, 0, 40, len(rows), 4)
    return bytes(data)


class TestSynthetic(unittest.TestCase):
    def test_accept_object_and_exec(self):
        self.assertEqual(v.check_object(SyntheticELF())['hi_symbol'], v.FLAG)
        self.assertEqual(v.check_exec(SyntheticELF(True), v.WITNESS), v.REFERENCE)
        v.check_bytes(v.REFERENCE, v.WITNESS)
        v.check_bytes(bytes.fromhex('171500201305b51c8280'), v.WITNESS + 0x1000)

    def test_relocation_mutations_rejected(self):
        for index, field, bad in [(0, 'section', 2), (0, 'offset', 4),
                                   (0, 'type', 26), (0, 'symbol', 1),
                                   (0, 'addend', 1), (1, 'offset', 0),
                                   (1, 'type', 25), (1, 'symbol', 2),
                                   (1, 'addend', 1)]:
            with self.subTest(index=index, field=field):
                elf = SyntheticELF()
                elf.relocations[index][field] = bad
                with self.assertRaises(ValueError):
                    v.check_object(elf)
        elf = SyntheticELF()
        elf.symbols[3]['value'] = 4
        with self.assertRaisesRegex(ValueError, 'anchor'):
            v.check_object(elf)
        elf = SyntheticELF()
        elf.relocations = []
        with self.assertRaises(ValueError):
            v.check_object(elf)

    def test_exec_mutations_rejected(self):
        mutations = [lambda e: e.header.__setitem__(3, 1),
                     lambda e: e.program_headers.append([1] + [0] * 7),
                     lambda e: e.leaf.__setitem__('address', v.ADDR + 2),
                     lambda e: e.leaf.__setitem__('size', 9),
                     lambda e: e.symbols[1].__setitem__('section', 0xfff1),
                     lambda e: e.symbols[1].__setitem__('size', 9),
                     lambda e: e.symbols[2].__setitem__('value', v.WITNESS + 0x1000),
                     lambda e: e.relocations.append({})]
        for mutate in mutations:
            elf = SyntheticELF(True)
            mutate(elf)
            with self.subTest(mutate=mutate):
                with self.assertRaises(ValueError):
                    v.check_exec(elf, v.WITNESS)
        with self.assertRaises(ValueError):
            v.check_bytes(b'\0' * 10, v.WITNESS)
        for wrong in (v.REFERENCE, b'\0' * 10, bytes.fromhex('171500201305b51c8281')):
            with self.subTest(wrong=wrong.hex()), self.assertRaises(ValueError):
                v.check_bytes(wrong, v.WITNESS + 0x1000)
        self.assertEqual(v.expected_bytes(v.WITNESS + 0x1000).hex(), '171500201305b51c8280')

    def test_exec_unresolved_symbol_rejected(self):
        elf = SyntheticELF(True)
        elf.symbols.append(sym(4, 'unresolved', 0, 0, 0x10, 0))
        elf.sections[3]['size'] = elf.sections[3]['entsize'] * len(elf.symbols)
        with self.assertRaisesRegex(ValueError, '^unresolved symbol$'):
            v.check_exec(elf, v.WITNESS)

    def test_actual_elf_tables_and_unsupported_sections(self):
        ELF = v.reader_class()
        good = ELF(linked_elf_bytes())
        self.assertEqual(v.check_exec(good, v.WITNESS), v.REFERENCE)
        self.assertEqual(sum(s['name'] == v.FLAG for s in good.symbols), 1)
        with self.assertRaisesRegex(ValueError, '^unresolved symbol$'):
            v.check_exec(ELF(linked_elf_bytes(unresolved=True)), v.WITNESS)
        for offset, fmt, value, message in (
                (16, '<H', 1, 'ET_EXEC/entry'),
                (24, '<I', 1, 'ET_EXEC/entry')):
            data = bytearray(linked_elf_bytes())
            struct.pack_into(fmt, data, offset, value)
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, message):
                v.check_exec(ELF(bytes(data)), v.WITNESS)
        for typ in (11, 19):  # The pinned parser otherwise silently ignores these.
            parsed = ELF(linked_elf_bytes(extra_type=typ))
            with self.subTest(type=typ), self.assertRaisesRegex(ValueError, 'forbidden'):
                v.check_exec(parsed, v.WITNESS)
        with self.assertRaisesRegex(ValueError, 'REL records forbidden'):
            ELF(linked_elf_bytes(extra_type=9))
        for data in (linked_elf_bytes(duplicate_target=True),
                     linked_elf_bytes(symtab_type=11)):
            with self.assertRaises(ValueError):
                v.check_exec(ELF(data), v.WITNESS)
        for typ in (9, 11, 19):
            for linked in (False, True):
                elf = SyntheticELF(linked)
                elf.sections.append(dict(index=len(elf.sections), type=typ))
                with self.subTest(type=typ, linked=linked), self.assertRaises(ValueError):
                    (v.check_exec(elf, v.WITNESS) if linked else v.check_object(elf))

    def test_parser_and_hash_fail_closed(self):
        elf = v.reader_class()
        for payload in (b'', b'\x7fELF' + b'\0' * 100):
            with self.assertRaises(ValueError):
                elf(payload)
        with self.assertRaises(ValueError):
            v.pinned(Path(__file__), '0' * 64)

    def test_command_failure(self):
        with mock.patch.object(v.subprocess, 'run', return_value=subprocess.CompletedProcess([], 9, '', 'failure')):
            with self.assertRaisesRegex(ValueError, 'command failed'):
                v.run(['compiler'])

    def test_missing_executable_cli(self):
        # Keep pinning intact; only redirect the actual spawn to a nonexistent path.
        # runpy executes the real __main__ exception handler in a child process.
        with tempfile.TemporaryDirectory(prefix='bd46-missing-') as td:
            missing = str(Path(td) / 'absent-tool.exe')
            code = ("import runpy, subprocess, sys\n"
                    "real = subprocess.run\n"
                    "def spawn(cmd, *a, **kw):\n"
                    "    print('attempting missing executable: ' + sys.argv[2], file=sys.stderr)\n"
                    "    return real([sys.argv[2]] + cmd[1:], *a, **kw)\n"
                    "subprocess.run = spawn\n"
                    "runpy.run_path(sys.argv[1], run_name='__main__')\n")
            cmd = [sys.executable, '-B']
            if sys.flags.optimize:
                cmd.append('-O')
            result = subprocess.run(cmd + ['-c', code, str(v.HERE / 'verify.py'), missing],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FAILED:', result.stderr)
            self.assertIn('absent-tool.exe', result.stderr)
            self.assertNotIn('"passed"', result.stdout)

    def test_fresh_replay(self):
        command = [sys.executable, '-B']
        if sys.flags.optimize:
            command.append('-O')
        command.append(str(v.HERE / 'verify.py'))
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = json.loads(result.stdout)
        self.assertIs(receipt['passed'], True)
        self.assertEqual(receipt['optimize'], sys.flags.optimize)
        self.assertEqual(len(receipt['cases']), 4)
        self.assertEqual([x['exact'] for x in receipt['cases']], [True, False, True, False])
        self.assertEqual([x['bytes'] for x in receipt['cases']],
                         [v.REFERENCE.hex(), '171500201305b51c8280'] * 2)
        self.assertEqual(receipt['source_sha256'], v.SOURCE_SHA)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSynthetic)
    if suite.countTestCases() == 0:
        print('FAILED: no tests', file=sys.stderr)
        sys.exit(1)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() and result.testsRun > 0 else 1)
