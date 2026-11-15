#!/usr/bin/env python3
"""Offline 15630 table dispatch; static bytes, not runtime or full CPU."""
import hashlib
import json
import struct
import unittest
from pathlib import Path
import test_155d0_entry_order as entry

MASK = 0xffffffff
BASE = 0x1a6f4
CODE = bytes.fromhex('1379f90f9307c00f63ea2715175700001307870b0a093a9983270900ba978287')
TABLE_SHA = '719c2a814210b025b79dcb9dd1e6dd73c132922ab7e3ebbde9898c0af3c5daf7'
MAP = Path(__file__).resolve().parents[2] / 'analysis/action-dispatch-2026-10-24/case-map.json'


def dispatch(code, table, s2):
    if len(code) != 32 or len(table) != 1012:
        raise ValueError('invalid window')
    # Exact instruction matching deliberately refuses unsupported mutations.
    if code != CODE:
        raise ValueError('unsupported instruction')
    index = s2 & 255
    if index > 252:
        return index, None, 0x1578c
    word = int.from_bytes(table[4 * index:4 * index + 4], 'little')
    # JALR clears bit zero even if a synthetic table entry is odd.
    return index, BASE + 4 * index, ((BASE + word) & MASK) & ~1


class Dispatch(unittest.TestCase):
    def test_original_table_and_case_map(self):
        image = entry.BIN.read_bytes()
        self.assertEqual(hashlib.sha256(image).hexdigest(), entry.SHA)
        code = image[0x15630 - 0x8000:0x15650 - 0x8000]
        table = image[BASE - 0x8000:BASE - 0x8000 + 1012]
        self.assertEqual(code, CODE)
        self.assertEqual(hashlib.sha256(table).hexdigest(), TABLE_SHA)
        record = json.loads(MAP.read_text(encoding='utf-8'))
        self.assertEqual((record['table_PC'], record['relative_base'], record['bytes']), (BASE, BASE, 1012))
        self.assertEqual(len(record['entries']), 253)
        targets = []
        for i, item in enumerate(record['entries']):
            word = struct.unpack_from('<i', table, i * 4)[0]
            index, address, target = dispatch(code, table, i)
            self.assertEqual((item['index'], item['relative_word'], item['target_PC']), (i, word, target))
            self.assertEqual((index, address), (i, BASE + 4 * i))
            targets.append(target)
        self.assertEqual((len(set(targets)), targets.count(0x1578c)), (174, 39))

    def test_boundaries_mutation_and_unsigned_wrap(self):
        table = bytearray(1012)
        table[:4] = (0xffffffff).to_bytes(4, 'little')
        self.assertEqual(dispatch(CODE, table, 0), (0, BASE, (BASE - 1) & ~1))
        for n in (253, 254, 255, 0x123400fd):
            self.assertEqual(dispatch(CODE, table, n), (n & 255, None, 0x1578c))
        self.assertEqual(dispatch(CODE, table, 0x100)[0], 0)
        for offset in range(len(CODE)):
            altered = bytearray(CODE)
            altered[offset] ^= 1
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                dispatch(altered, table, 0)
        with self.assertRaises(ValueError):
            dispatch(CODE, table[:-1], 0)


if __name__ == '__main__':
    unittest.main()
