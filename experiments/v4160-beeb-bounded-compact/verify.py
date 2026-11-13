#!/usr/bin/env python3
"""Bounded offline byte replay; no target code is executed."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
BIN = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
MAN = 'src/source-manifest.json'
BUILD = 'src/source-build-manifest.json'
UNIT = 'src/native/startup/reset_data.c'
ORIGIN = 'experiments/tsl9-runtime-reset-clock/src/reset_data.c'
SOURCE_HASH = '02aad93670679ef0c8c472dc998e3d41963ba33d280a5ec6baa336a3173ed1ec'
PINS = {
    BIN: (76800, '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'),
    MAN: (193258, '30e7076ed9fa896f5745024ab6fa0a9f016124a2dd11ae12fe566e2107f06479'),
    BUILD: (114004, '466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739'),
    UNIT: (1389, SOURCE_HASH), ORIGIN: (1389, SOURCE_HASH),
}
BASE = 0x8000
TARGET = 0x2000beeb
# Half-open windows, indexed by target PC, not file offset.
WINDOWS = {
    0xae9e: '9717002083c7d70499cb19478d07238ee10aa38ef10a97170020a38b0702',
    0xb096: '9716002083c636e5094781476393e6008d47b2403e8541018280',
    0xb0b0: '97170020a38da7e28280',
    0x186aa: '97c1fe1f938161951781ff1f1301e194172500001305654a938501001386010863fac5008322050023a0550011059105e3eac5fe138501089745ff1f938565276377b500232005001105e36db5fe',
    0x1873e: 'b7070020dc43829773002030',
    0x1ab60: '020000000c0004000100000038ab010002000000120004000100000042ab01000200000044ab010002000000884000200200000018000400030000008040002000000000000000000102030406070809000001009cc200200cc300200cc4002094c4002094c5002094c6002000d8b805a90089018c060000ea037a03a1030000',
}
EXPECTED = [(0xae9e, 'load', 0x2000beeb, 1),
            (0xaeb4, 'store', 0x2000beeb, 1),
            (0xb0b0, 'store', 0x2000beeb, 1)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def signed(x, bits):
    return x - (1 << bits) if x & (1 << (bits - 1)) else x


def covers(start, width, address):
    # RV32 arithmetic wraps, including a multi-byte access at the top of space.
    return ((address - start) & 0xffffffff) < width


def scan(data, base=BASE, target=TARGET):
    """Every 2-byte-aligned offset: adjacent 32-bit U + I/S, not decoding code."""
    found = []
    for i in range(0, len(data) - 7, 2):
        a = int.from_bytes(data[i:i+4], 'little')
        b = int.from_bytes(data[i+4:i+8], 'little')
        op, rd = a & 127, (a >> 7) & 31
        code, rs, funct = b & 127, (b >> 15) & 31, (b >> 12) & 7
        if op not in (0x17, 0x37) or rd == 0 or rd != rs:
            continue
        if code == 3 and funct in (0, 1, 2, 4, 5):
            kind, width, imm = 'load', (1, 2, 4, 0, 1, 2)[funct], signed(b >> 20, 12)
        elif code == 0x23 and funct in (0, 1, 2):
            kind, width = 'store', 1 << funct
            imm = signed(((b >> 25) << 5) | ((b >> 7) & 31), 12)
        elif code == 0x13 and funct == 0:
            kind, width, imm = 'addi', 1, signed(b >> 20, 12)
        else:
            continue
        addr = ((a & 0xfffff000) + (base + i if op == 0x17 else 0) + imm) & 0xffffffff
        if covers(addr, width, target):
            found.append((base + i, kind, addr, width))
    return found


def windows(data):
    for pc, value in WINDOWS.items():
        expected = bytes.fromhex(value)
        offset = pc - BASE
        require(offset >= 0 and data[offset:offset+len(expected)] == expected,
                'window mismatch at %#x' % pc)


def pinned(root=ROOT):
    result = {}
    for path, (size, digest) in PINS.items():
        data = (root / path).read_bytes()
        require(len(data) == size and hashlib.sha256(data).hexdigest() == digest,
                'pin mismatch: ' + path)
        result[path] = data
    return result


def metadata(inputs):
    require(inputs[UNIT] == inputs[ORIGIN], 'origin differs')
    m, b = (json.loads(inputs[p]) for p in (MAN, BUILD))
    def one(items, field, value):
        matches = [x for x in items if x.get(field) == value]
        require(len(matches) == 1, 'missing/duplicate ' + value)
        return matches[0]
    entry = one(m['files'], 'destination', UNIT)
    require(entry == {'origin': ORIGIN, 'destination': UNIT, 'replacements': [],
                      'origin_sha256': SOURCE_HASH, 'sha256': SOURCE_HASH}, 'source entry')
    require(one(b['files'], 'destination', UNIT) == {'destination': UNIT, 'sha256': SOURCE_HASH}, 'build entry')
    u = one(m['native_units'], 'name', 'startup-data')
    require(all(u.get(k) == v for k, v in {'profile': 'runtime-reset', 'origin_unit': ORIGIN,
            'curated_unit': UNIT, 'origin_unit_sha256': SOURCE_HASH}.items()), 'source unit')
    require(one(b['native_units'], 'name', 'startup-data') ==
            {'curated_unit': UNIT, 'name': 'startup-data', 'profile': 'runtime-reset'}, 'build unit')
    text = inputs[UNIT].decode('ascii')
    require('section(".rodata.tsl9_reset_initializer"),aligned(4)' in text and
            'tsl9_runtime_reset_initializer[32]' in text and
            'section(".bss.tsl9_reset_ram"),aligned(4)' in text and
            'tsl9_runtime_reset_ram[8790]' in text and
            'section(".bss.tsl9_reset_stack"),aligned(16)' in text and
            'tsl9_runtime_reset_stack[4]' in text, 'carrier declarations')
    words = re.findall(r'UINT32_C\(0x([0-9a-f]{8})\)', text)
    data = b''.join(int(w, 16).to_bytes(4, 'little') for w in words)
    require(data == bytes.fromhex(WINDOWS[0x1ab60]), 'carrier literal')


def pair_addi(data, pc):
    offset = pc - BASE
    a = int.from_bytes(data[offset:offset+4], 'little')
    b = int.from_bytes(data[offset+4:offset+8], 'little')
    rd = (a >> 7) & 31
    require(a & 127 == 0x17 and rd != 0 and b & 0x707f == 0x13 and
            (b >> 15) & 31 == rd and (b >> 7) & 31 == rd, 'bad AUIPC/ADDI')
    return (pc + (a & 0xfffff000) + signed(b >> 20, 12)) & 0xffffffff


def word_starts(start, end):
    # Model the reset loop's unsigned precheck and four-byte increment.
    require(0 <= start <= 0xffffffff and 0 <= end <= 0xffffffff and
            start % 4 == 0 and end % 4 == 0, 'invalid reset range')
    return range(start, end, 4) if start < end else range(0)


def verify(root=ROOT):
    inputs = pinned(root)
    metadata(inputs)
    data = inputs[BIN]
    windows(data)
    gp = pair_addi(data, 0x186aa)
    src = pair_addi(data, 0x186ba)
    end = pair_addi(data, 0x186e2)
    require((gp, src, end) == (0x20004000, 0x1ab60, 0x2000c958), 'reset addresses')
    require(0x2000bee8 in word_starts(gp + 128, end), 'reset word coverage')
    # Pinned pairs: aeb4 stores x0; b0b0 stores x10. Both are SB.
    for pc, reg in ((0xaeb4, 0), (0xb0b0, 10)):
        word = int.from_bytes(data[pc-BASE+4:pc-BASE+8], 'little')
        require((word >> 20) & 31 == reg and (word >> 12) & 7 == 0, 'store fields')
    candidates = scan(data)
    require(candidates == EXPECTED, 'raw scan mismatch: %r' % (candidates,))
    return candidates


def jalr(value, imm=0):
    return ((value + imm) & 0xffffffff) & ~1


class Tests(unittest.TestCase):
    def test_full_replay(self):
        self.assertEqual(verify(), EXPECTED)

    def test_all_window_bytes_mutated(self):
        original = pinned()[BIN]
        for pc, value in WINDOWS.items():
            for i in range(len(bytes.fromhex(value))):
                with self.subTest(pc=hex(pc), byte=i):
                    altered = bytearray(original)
                    altered[pc - BASE + i] ^= 1
                    with self.assertRaises(ValueError):
                        windows(altered)

    def test_missing_and_tampered_inputs(self):
        original = Path.read_bytes
        for name in PINS:
            for missing in (True, False):
                with self.subTest(path=name, missing=missing):
                    def read(path):
                        if path == ROOT / name:
                            if missing:
                                raise FileNotFoundError(str(path))
                            data = original(path)
                            return data[:-1] + bytes([data[-1] ^ 1])
                        return original(path)
                    with patch.object(Path, 'read_bytes', read):
                        with self.assertRaises((ValueError, FileNotFoundError)):
                            pinned()

    def test_range_and_word_coverage(self):
        self.assertFalse(covers(0x20004080, 0xc958-0x4080, 0x2000407f))
        self.assertTrue(covers(0x20004080, 0xc958-0x4080, TARGET))
        self.assertTrue(covers(0x20004080, 0xc958-0x4080, 0x2000c957))
        self.assertFalse(covers(0x20004080, 0xc958-0x4080, 0x2000c958))
        self.assertEqual(list(word_starts(8, 8)), [])
        self.assertEqual(list(word_starts(12, 8)), [])
        self.assertEqual(list(word_starts(8, 16)), [8, 12])
        with self.assertRaises(ValueError):
            word_starts(9, 16)
        self.assertIn(0x2000bee8, word_starts(0x20004080, 0x2000c958))
        self.assertEqual((TARGET - 0x20004080) // 4 * 4 + 0x20004080, 0x2000bee8)
        self.assertTrue(covers(0x2000bee8, 4, TARGET))
        self.assertTrue(covers(0xfffffffe, 4, 1))
        self.assertFalse(covers(0xfffffffe, 4, 2))

    def test_metadata_rejects_changed_carrier_and_origin(self):
        inputs = pinned()
        for name in (UNIT, ORIGIN):
            changed = dict(inputs)
            changed[name] = changed[name].replace(b'0x00000002', b'0x00000003', 1)
            with self.subTest(path=name), self.assertRaises(ValueError):
                metadata(changed)
        changed = dict(inputs)
        changed[UNIT] = changed[ORIGIN] = inputs[UNIT].replace(b'0x00000002', b'0x00000003', 1)
        with self.assertRaises(ValueError):
            metadata(changed)

    def test_negative_load_and_wrong_pc(self):
        # AUIPC x13; LBU x13,-429(x13), at actual PC b096.
        pair = bytes.fromhex('9716002083c636e5')
        self.assertEqual(scan(pair, 0xb096, 0x2000bee9), [(0xb096, 'load', 0x2000bee9, 1)])
        self.assertEqual(scan(pair, 0xb098, 0x2000bee9), [])
        self.assertEqual(signed(0xe53, 12), -429)
        data = pinned()[BIN]
        self.assertEqual(pair_addi(data, 0x186aa), 0x20004000)
        with self.assertRaises(ValueError):
            pair_addi(data, 0x186ac)

    def test_store_scan_edges(self):
        pair = bytes.fromhex('97170020a38da7e2')
        self.assertEqual(scan(pair, 0xb0b0), [(0xb0b0, 'store', TARGET, 1)])
        self.assertEqual(scan(pair[:-1], 0xb0b0), [])
        self.assertEqual(scan(b'\x00\x00' + pair, 0xb0ae), [(0xb0b0, 'store', TARGET, 1)])
        self.assertEqual(scan(b'\x00' + pair, 0xb0af), [])
        # SW x10,0(x15) with LUI x15,0x2000c: word covers its last byte.
        sw = bytes.fromhex('b7c7002023a0a700')
        self.assertEqual(scan(sw, 0, 0x2000c003), [(0, 'store', 0x2000c000, 4)])
        self.assertEqual(scan(sw, 0, 0x2000c004), [])

    def test_scan_result_is_checked(self):
        with patch('__main__.scan', return_value=[]):
            with self.assertRaises(ValueError):
                verify()

    def test_jalr_odd_target(self):
        self.assertEqual(jalr(0x1235), 0x1234)
        self.assertEqual(jalr(0xffffffff, 2), 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--test', action='store_true')
    group.add_argument('--inspect', action='store_true')
    args = parser.parse_args()
    if args.test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        count = suite.countTestCases()
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(not result.wasSuccessful() or bool(result.skipped) or result.testsRun != count)
    try:
        candidates = verify()
        print('pins, metadata, windows: OK')
        for pc, kind, address, width in candidates:
            print('%#x %s %#x width=%d' % (pc, kind, address, width))
        print('reset: conditional copy [0x20004000,0x20004080), zero [0x20004080,0x2000c958); target word 0x2000bee8')
        print('0x1873e: load pointer from 0x20000004, JALR clears target bit 0 if reached')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('FAIL:', exc, file=sys.stderr)
        sys.exit(1)
