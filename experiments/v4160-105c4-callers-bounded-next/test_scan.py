#!/usr/bin/env python3
import hashlib
import importlib.util
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SCAN_SHA = 'b4f361bf8adca851119fde6fe4bd61ad2afee41736907b44aa92d329dffdd493'


def load_pinned(path, digest):
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != digest:
        raise ValueError('scan source hash mismatch')
    module = types.ModuleType('pinned_scan')
    module.__file__ = str(path)
    exec(compile(source, str(path), 'exec'), module.__dict__)
    return module


s = load_pinned(HERE / 'scan.py', SCAN_SHA)


def enc_jal(delta, rd=1):
    if delta & 1 or not -(1 << 20) <= delta < (1 << 20) or not 0 <= rd < 32:
        raise ValueError('jal range')
    d = delta & 0x1fffff
    return (0x6f | rd << 7 | (d & 0x100000) << 11 | (d & 0x800) << 9 | (d & 0x7fe) << 20)


def enc_cjal(delta):
    if delta & 1 or not -2048 <= delta <= 2046:
        raise ValueError('cjal range')
    d = delta & 0xfff
    h = 0x2001
    for ibit, hbit in ((11,12), (4,11), (9,10), (8,9), (10,8), (6,7),
                       (7,6), (3,5), (2,4), (1,3), (5,2)):
        h |= ((d >> ibit) & 1) << hbit
    return h


class ScanTests(unittest.TestCase):
    def test_jal_bits_and_extremes(self):
        self.assertEqual(s.jal(0x008000ef, 0x1000), (1, 8, 0x1008))
        self.assertEqual(s.jal(0xffdff06f, 0), (0, -4, 0xfffffffc))
        for d in [-1048576, -1048574, -4096, -2048, -2, 0, 2, 2046, 2048, 4096, 1048574] + [1 << i for i in range(1, 20)]:
            for rd in (0, 1, 5, 31):
                self.assertEqual(s.jal(enc_jal(d, rd), 0xfffffff0), (rd, d, (0xfffffff0 + d) & 0xffffffff))
        for bad in (-1048578, 1048576, 1):
            with self.assertRaises(ValueError): enc_jal(bad)
        self.assertIsNone(s.jal(0x008000ee, 0))

    def test_rasm2_cjal_vectors(self):
        # Independent rasm2 disassembly output and commands are recorded in README.
        for raw, pc, delta, target in [('0122', 0x1000, 256, 0x1100),
                                       ('7d3f', 0x1000, -66, 0xfbe)]:
            with self.subTest(raw=raw):
                self.assertEqual(s.cjal(int.from_bytes(bytes.fromhex(raw), 'little'), pc), (1, delta, target))
                hits, _ = s.scan(bytes.fromhex(raw), pc, target)
                self.assertTrue(any(h['kind'] == 'C.JAL/RV32' and h['offset'] == 0 for h in hits))

    def test_real_listed_jals(self):
        data = s.BIN.read_bytes()
        s.pinned(data, s.BIN_SHA, 'BIN')
        for pc, raw, rd, dest in [(0x10956, 'eff07fee', 1, 0x1083c),
                                  (0x10bda, 'eff0dfbe', 1, 0x107c6),
                                  (0x10bbe, '6ff09fc0', 0, 0x107c6)]:
            with self.subTest(pc=hex(pc)):
                insn = data[pc-s.BASE:pc-s.BASE+4]
                self.assertEqual(insn.hex(), raw)
                self.assertEqual(s.jal(int.from_bytes(insn, 'little'), pc), (rd, dest-pc, dest))
                hits, _ = s.scan(insn, pc, dest)
                self.assertTrue(any(h['kind'] == 'JAL' and h['offset'] == 0 and h['rd'] == rd for h in hits))

    def test_cjal_all_immediates(self):
        for d in range(-2048, 2048, 2):
            self.assertEqual(s.cjal(enc_cjal(d), 0), (1, d, d & 0xffffffff))
        for bad in (-2050, 2048, 1):
            with self.assertRaises(ValueError): enc_cjal(bad)
        self.assertIsNone(s.cjal(0xa001, 0))

    def test_scan_lengths_false_target_and_odd(self):
        for width, encoder, kind in ((4, lambda d: enc_jal(d).to_bytes(4, 'little'), 'JAL'),
                                     (2, lambda d: enc_cjal(d).to_bytes(2, 'little'), 'C.JAL/RV32')):
            raw = encoder(0)
            self.assertEqual(s.scan(raw[:-1], 0x1000, 0x1000)[0], [])
            self.assertEqual(s.scan(raw, 0x1000, 0x1002)[0], [])
            hits, counts = s.scan(raw, 0x1000, 0x1000)
            self.assertEqual(counts[kind], 1)
            self.assertTrue(any(h['kind'] == kind and h['offset'] == 0 for h in hits))
            odd, _ = s.scan(b'\x00' + raw, 0x1000, 0x1001)
            self.assertTrue(any(h['kind'] == kind and h['offset'] == 1 and h['alignment'] == 'odd' for h in odd))
        self.assertEqual(s.scan(b'', 0, 0), ([], {'JAL': 0, 'C.JAL/RV32': 0}))

    def test_actual_decoder_visits_after_insertions(self):
        data = s.pinned(s.BIN.read_bytes(), s.BIN_SHA, 'BIN')
        for width, raw, delta, kind in ((4, bytes.fromhex('ef008000'), 8, 'JAL'),
                                        (2, bytes.fromhex('0122'), 256, 'C.JAL/RV32')):
            # First, last, consecutive even/odd, and interior offsets, each in a fresh copy.
            for off in (0, 1, 2, 257, 258, len(data)-width-1, len(data)-width):
                with self.subTest(kind=kind, off=off):
                    mutant = bytearray(data)
                    mutant[off:off+width] = raw
                    seen = {'JAL': [], 'C.JAL/RV32': []}
                    def wrap(name, decoder):
                        def visit(word, pc):
                            seen[name].append((word, pc))
                            return decoder(word, pc)
                        return visit
                    with mock.patch.object(s, 'jal', wrap('JAL', s.jal)), mock.patch.object(s, 'cjal', wrap('C.JAL/RV32', s.cjal)):
                        hits, counts = s.scan(mutant, target=s.BASE+off+delta)
                    self.assertTrue(any(h['kind'] == kind and h['offset'] == off and h['bytes'] == raw.hex() and h['target'] == s.BASE+off+delta for h in hits))
                    for k, w in (('JAL', 4), ('C.JAL/RV32', 2)):
                        expected = [(int.from_bytes(mutant[i:i+w], 'little'), s.BASE+i)
                                    for i in range(len(mutant)-w+1)]
                        self.assertEqual(seen[k], expected)
                        self.assertEqual(counts[k], len(seen[k]))

    def test_pinned_real_and_mutation(self):
        data = s.BIN.read_bytes()
        sources = {n: (s.ROOT / n).read_bytes() for n in s.PINS}
        self.assertEqual(len(s.verify_evidence(data, sources)), 2)
        hits, counts = s.scan(data)
        self.assertEqual(hits, [])
        self.assertEqual(counts, {'JAL': 76797, 'C.JAL/RV32': 76799})
        for name in s.PINS:
            changed = dict(sources)
            changed[name] += b'\n'
            with self.subTest(name=name), self.assertRaises(ValueError):
                s.verify_evidence(data, changed)
        mutant = bytearray(data)
        mutant[0] ^= 1
        with self.assertRaises(ValueError): s.verify_evidence(mutant, sources)
        with self.assertRaises(ValueError): s.verify_evidence(data[:-1], sources)

    def test_pairs(self):
        self.assertEqual(s.auipc_addi(bytes.fromhex('17050000130585c7'), 0x1094c), (10, s.TARGET))
        self.assertEqual(s.auipc_addi(bytes.fromhex('970600009386069e'), 0x10be4), (13, s.TARGET))
        with self.assertRaises(ValueError): s.auipc_addi(b'\x00' * 8, 0)
        self.assertNotEqual(s.auipc_addi(bytes.fromhex('17050000130585c6'), 0x1094c)[1], s.TARGET)

    def test_stale_pyc_and_source_pin_mutation(self):
        # Timestamp-based pyc of malicious source, followed by equal-size source with
        # identical integer mtime: standard import really consumes stale bytecode.
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            path = Path(tmp) / 'probe.py'
            good = b'STALE_EXECUTED = False\n'
            bad = b'STALE_EXECUTED = True \n'
            self.assertEqual(len(good), len(bad))
            timestamp = 1700000000
            path.write_bytes(bad)
            os.utime(path, (timestamp, timestamp))
            cache = py_compile.compile(str(path), doraise=True, invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
            path.write_bytes(good)
            os.utime(path, (timestamp, timestamp))
            self.assertTrue(Path(cache).is_file())
            self.assertEqual(int(path.stat().st_mtime), timestamp)
            spec = importlib.util.spec_from_file_location('stale_probe', path)
            stale = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(stale)
            self.assertTrue(stale.STALE_EXECUTED)
            digest = hashlib.sha256(good).hexdigest()
            self.assertFalse(load_pinned(path, digest).STALE_EXECUTED)
            path.write_bytes(bad)
            os.utime(path, (timestamp, timestamp))
            with self.assertRaises(ValueError): load_pinned(path, digest)
            with self.assertRaises(ValueError): load_pinned(HERE / 'scan.py', '0' * 64)

    def test_cli_normal_and_optimized(self):
        for opt in ([], ['-O']):
            p = subprocess.run([sys.executable, '-B', *opt, str(HERE / 'scan.py')], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn('"raw_hits": []', p.stdout)
            self.assertEqual(p.stderr, '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
