#!/usr/bin/env python3
"""Bounded CLI replay tests; builds only isolated RV32 ELF evidence, never firmware."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
HERE = Path('experiments/v4160-105c4-six-section-published-split/probe.py')
INPUTS = (
    'src/source-build-manifest.json',
    'src/native/receive/feature_state_records.c',
    'src/native/receive/feature_callback.c',
    'experiments/v4160-new-leaf-turn/leaf.c',
    'experiments/v4160-105c4-source-split-replay/verify.py',
    'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',
    'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
)
SYMBOL_LABELS = ('target', 'trampoline_b', 'trampoline_a', 'caller_a', 'tail', 'caller_b')
SYMBOL_MUTATIONS = ('missing', 'duplicate', 'wrong-address', 'wrong-section')
EXPECTED_SECTIONS = (
    ('target', 0x105c4, 12, 'tsl9_feature_state_records_provider_105c4'),
    ('trampoline_b', 0x107c6, 18, 'tsl9_feature_state_records_provider_107c6'),
    ('trampoline_a', 0x1083c, 12, 'tsl9_feature_external_1083c'),
    ('caller_a', 0x10944, 22, 'tsl9_feature_external_10944'),
    ('tail', 0x10bbe, 4, 'tsl9_feature_state_records_block_10bbe'),
    ('caller_b', 0x10bde, 26, 'tsl9_feature_state_records_block_10bde'),
)
INPUT_KEYS = ('manifest', 'owner', 'callback', 'leaf', 'splitter', 'parser', 'bin')
EXPECTED_RELOCATIONS = [
    ['.text.tsl9_feature_external_10944', 8, 23, 'tsl9_feature_state_records_provider_105c4', 0],
    ['.text.tsl9_feature_external_10944', 12, 24, '.Lfeature_state_records_literal_1094c', 0],
    ['.text.tsl9_feature_external_10944', 18, 17, 'tsl9_feature_external_1083c', 0],
    ['.text.tsl9_feature_state_records_block_10bbe', 0, 17, 'tsl9_feature_state_records_provider_107c6', 0],
    ['.text.tsl9_feature_state_records_block_10bde', 6, 23, 'tsl9_feature_state_records_provider_105c4', 0],
    ['.text.tsl9_feature_state_records_block_10bde', 10, 24, '.Lfeature_state_records_literal_10be4', 0],
    ['.text.tsl9_feature_state_records_block_10bde', 24, 45, 'tsl9_feature_state_records_block_10bbe', 0],
]


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='tsl9-105c4-cli-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for relative in (str(HERE), *INPUTS):
            src = ROOT / relative
            dest = self.root / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)

    def invoke(self, *args, env=None):
        flags = ['-B'] + (['-O'] if sys.flags.optimize else [])
        child_env = os.environ.copy() if env is None else env.copy()
        if child_env.get('TSL9_NDK_BIN'):
            child_env['TSL9_NDK_BIN'] = str(Path(child_env['TSL9_NDK_BIN']).resolve())
        p = subprocess.run([sys.executable, *flags, str(self.root / HERE), *args],
                           cwd=self.root, env=child_env, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=240)
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertEqual(p.stderr, '')
        result = json.loads(p.stdout)
        self.assertEqual(result['status'], 'INCOMPLETE_FAIL_CLOSED')
        self.assertIs(result['passed'], False)
        return result

    def test_selected_link_replay(self):
        result = self.invoke()
        self.assertIs(result['selected_checks_passed'], True)
        self.assertEqual(result['split_offset'], 5968)
        expected_hashes = {key: hashlib.sha256((self.root / path).read_bytes()).hexdigest()
                           for key, path in zip(INPUT_KEYS, INPUTS)}
        self.assertEqual(result['input_sha256'], expected_hashes)
        self.assertEqual(set(result['checked_tool_sha256']), {'clang.exe', 'ld.lld.exe', 'stdint.h'})
        self.assertIn('not type, binding, size or visibility', result['limits'])
        positive = [case for case in result['cases'] if 'case' in case]
        self.assertEqual({(case['mode'], case['case']) for case in positive},
                         {('c', 'original'), ('c', 'split'), ('cpp', 'original'), ('cpp', 'split')})
        self.assertEqual(len(positive), 4)
        expected_mutations = {label + ':' + mutation for label in SYMBOL_LABELS for mutation in SYMBOL_MUTATIONS}
        for case in positive:
            with self.subTest(mode=case['mode'], case=case['case']):
                self.assertEqual(case['bytes_matched'], 94)
                self.assertRegex(case['final_elf_sha256'], r'^[0-9a-f]{64}$')
                self.assertEqual([section['name'] for section in case['sections']], list(SYMBOL_LABELS))
                image = (self.root / INPUTS[-1]).read_bytes()
                for section, (label, addr, size, symbol) in zip(case['sections'], EXPECTED_SECTIONS):
                    self.assertEqual(section['address'], hex(addr))
                    self.assertEqual(section['bytes'], image[addr-0x8000:addr-0x8000+size].hex())
                    self.assertEqual(section['symbol']['name'], symbol)
                    self.assertEqual(section['symbol']['value'], hex(addr))
                    self.assertGreater(section['symbol']['section_index'], 0)
                self.assertEqual(case['elf_negatives'], ['missing-symtab', 'dynamic-symtab', 'null-only-symtab'])
                self.assertEqual(len(case['symbol_negatives']), 24)
                self.assertEqual(set(case['symbol_negatives']), expected_mutations)
        negatives = [case for case in result['cases'] if 'negative_checks' in case]
        self.assertEqual({case['mode'] for case in negatives}, {'c', 'cpp'})
        self.assertEqual(len(negatives), 2)
        for case in negatives:
            self.assertEqual(case['negative_checks'], ['missing-leaf undefined', 'wrong-target-address', 'wrong-leaf-constant'])
            self.assertEqual(case['selected_original_and_split_relocations']['owner'], EXPECTED_RELOCATIONS)
            self.assertEqual(case['selected_original_and_split_relocations']['split'], EXPECTED_RELOCATIONS)

    def test_relocation_tuple_guard_fault_injections(self):
        path = self.root / HERE
        original = path.read_text(encoding='utf-8')
        guard = "                need(found == EXPECTED_RELOCATIONS, 'selected input relocations: '+owner_unit)"
        self.assertEqual(original.count(guard), 1)
        # Perturb the observed tuple, not the expected tuple. If the guard is removed,
        # these tests fail rather than accepting the unchanged tuple count.
        for index, value in ((1, 10), (2, 24), (3, 'wrong_symbol'), (4, 1)):
            with self.subTest(field=index):
                mutation = ("                row = list(found[0]); row[%d] = %r; found[0] = tuple(row)\n" % (index, value))
                path.write_text(original.replace(guard, mutation + guard), encoding='utf-8')
                result = self.invoke()
                self.assertIs(result['selected_checks_passed'], False)
                self.assertEqual(result['error'], 'ValueError: selected input relocations: owner')
        # Control: the same faulty observation escapes if the comparison is removed;
        # the independent positive-result tuple assertion also detects that change.
        disabled = "                row = list(found[0]); row[1] = 10; found[0] = tuple(row)\n"
        path.write_text(original.replace(guard, disabled), encoding='utf-8')
        result = self.invoke()
        self.assertIs(result['selected_checks_passed'], True)
        negative = next(case for case in result['cases'] if case.get('mode') == 'c' and 'negative_checks' in case)
        self.assertNotEqual(negative['selected_original_and_split_relocations']['owner'], EXPECTED_RELOCATIONS)
        path.write_text(original, encoding='utf-8')

    def test_invalid_arguments(self):
        for args in (('--help',), ('unexpected',), ('--formal',)):
            with self.subTest(args=args):
                result = self.invoke(*args)
                self.assertIs(result['selected_checks_passed'], False)
                self.assertEqual(result['error'], 'ValueError: no arguments supported')

    def test_missing_tool_environment(self):
        env = os.environ.copy()
        env.pop('TSL9_NDK_BIN', None)
        result = self.invoke(env=env)
        self.assertIs(result['selected_checks_passed'], False)
        self.assertEqual(result['error'], "KeyError: 'TSL9_NDK_BIN'")

    def test_selected_guard_fault_injections(self):
        path = self.root / HERE
        original = path.read_text(encoding='utf-8')
        faults = (
            ("        need(len(symbols) == 1 and symbols[0]['index'] == sec['index'] and symbols[0]['value'] == addr,",
             "        if not symbols: return rows  # deliberately accept missing symbols\n        need(len(symbols) == 1 and symbols[0]['index'] == sec['index'] and symbols[0]['value'] == addr,",
             'ValueError: negative accepted: selected symbol target'),
            ("            need(p.returncode != 0 and b'undefined symbol' in p.stderr and NAME.encode() in p.stderr, 'missing leaf negative')",
             "            p.returncode = 0  # deliberately fake a successful linker status\n            need(p.returncode != 0 and b'undefined symbol' in p.stderr and NAME.encode() in p.stderr, 'missing leaf negative')",
             'ValueError: missing leaf negative'),
            ("def selected(e, image):\n    h = struct.unpack_from",
             "def selected(e, image):\n    if e.byname.get('.out_target', {}).get('address') == 0x105c6: return []\n    h = struct.unpack_from",
             'ValueError: negative accepted: section layout target'),
            ("        b = e.data(sec); need(b == image[addr-0x8000:addr-0x8000+size], 'BIN mismatch '+label)",
             "        b = e.data(sec); need(label == 'target' or b == image[addr-0x8000:addr-0x8000+size], 'BIN mismatch '+label)",
             'ValueError: negative accepted: BIN mismatch target'),
            ("def selected(e, image):\n    h = struct.unpack_from",
             "def selected(e, image):\n    if any(s['type'] == 11 for s in e.sections): return []\n    h = struct.unpack_from",
             'ValueError: negative accepted: dynamic symbol table'),
            ("    pinned(path, TOOLS[path.name])\n    return p",
             "    pinned(path, TOOLS[path.name])\n    if path.name == 'clang.exe' and Path(args[-1]).parent.name == 'cpp' and Path(args[-1]).name == 'owner.o':\n        Path(args[-1]).unlink()  # deliberately report success without an output\n    return p",
             'ValueError: compile output missing: cpp/owner'),
            ("    pinned(path, TOOLS[path.name])\n    return p",
             "    pinned(path, TOOLS[path.name])\n    if path.name == 'ld.lld.exe' and Path(args[-1]).parent.name == 'cpp' and Path(args[-1]).name == 'original.elf':\n        Path(args[-1]).unlink()  # deliberately report success without an output\n    return p",
             'ValueError: link output missing: cpp/original'),
        )
        for old, new, expected in faults:
            with self.subTest(expected=expected):
                self.assertEqual(original.count(old), 1)
                path.write_text(original.replace(old, new), encoding='utf-8')
                result = self.invoke()
                self.assertIs(result['selected_checks_passed'], False)
                self.assertEqual(result['error'], expected)
        path.write_text(original, encoding='utf-8')

    def test_each_input_pin_mutation(self):
        for relative in INPUTS:
            with self.subTest(path=relative):
                path = self.root / relative
                original = path.read_bytes()
                self.assertTrue(original)
                path.write_bytes(bytes([original[0] ^ 1]) + original[1:])
                try:
                    result = self.invoke()
                    self.assertIs(result['selected_checks_passed'], False)
                    self.assertEqual(result['error'], 'ValueError: pin: ' + path.name)
                finally:
                    path.write_bytes(original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
