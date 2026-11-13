#!/usr/bin/env python3
"""Verify one exact source split without modifying any source or executing firmware."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'src/native/receive/feature_state_records.c'
SOURCE_SHA = '19a1c39ee7831f42960454d02393512520c425ea1ad90f9e08b0f8d4e3b32db3'
SPLIT_SHA = 'd7f29f5420dc209f206eb424a527b6c9ed8000eb392ee25a35e2be2b1b90aada'
BLOCK = b'''REGION void tsl9_feature_state_records_provider_105c4(void)
{
    REGS;
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a0 = a0 + UINT32_C(0xfffffffc); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".option push\\n.option rvc\\nret\\n.option pop\\n");
    __builtin_unreachable();
}'''
DECL = b'extern void tsl9_feature_state_records_provider_105c4(void);'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def replace_unique(source):
    need(source.count(BLOCK) == 1, 'exact block count')
    prefix, suffix = source.split(BLOCK)
    return prefix + DECL + suffix, len(prefix)


def split_verified(source):
    need(len(source) == 55715, 'source length')
    need(digest(source) == SOURCE_SHA, 'source SHA-256')
    result, offset = replace_unique(source)
    need(offset == 5968, 'block offset')
    need(len(result) == 55450, 'split length')
    need(digest(result) == SPLIT_SHA, 'split SHA-256')
    return result, offset


class Tests(unittest.TestCase):
    def test_real_source_exact_projection(self):
        original = SOURCE.read_bytes()
        split, pos = split_verified(original)
        self.assertEqual(pos, 5968)
        self.assertEqual(split[:pos], original[:pos])
        self.assertEqual(split[pos:pos + len(DECL)], DECL)
        self.assertEqual(split[pos + len(DECL):], original[pos + len(BLOCK):])
        self.assertEqual(split[:pos] + BLOCK + split[pos + len(DECL):], original)

    def test_every_block_byte_mutation(self):
        source = SOURCE.read_bytes()
        for i in range(len(BLOCK)):
            changed = bytearray(source)
            changed[5968 + i] ^= 1
            with self.subTest(i=i), self.assertRaisesRegex(ValueError, '^source SHA-256$'):
                split_verified(changed)
            with self.subTest(i=i), self.assertRaisesRegex(ValueError, '^exact block count$'):
                replace_unique(changed)

    def test_postconditions_reject_real_projection_mutations(self):
        source = SOURCE.read_bytes()
        block_end = 5968 + len(BLOCK)
        moved = source[5968:block_end] + source[:5968] + source[block_end:]
        with patch.dict(globals(), {'SOURCE_SHA': digest(moved)}):
            with self.assertRaisesRegex(ValueError, '^block offset$'):
                split_verified(moved)
        with patch.dict(globals(), {'DECL': DECL + b' '}):
            with self.assertRaisesRegex(ValueError, '^split length$'):
                split_verified(source)
        replacement = bytes([DECL[0] ^ 1]) + DECL[1:]
        with patch.dict(globals(), {'DECL': replacement}):
            with self.assertRaisesRegex(ValueError, '^split SHA-256$'):
                split_verified(source)
        with patch.dict(globals(), {'SPLIT_SHA': '0' * 64}):
            with self.assertRaisesRegex(ValueError, '^split SHA-256$'):
                split_verified(source)

    def test_other_corruptions_and_ambiguous_blocks(self):
        source = SOURCE.read_bytes()
        with self.assertRaisesRegex(ValueError, '^source length$'):
            split_verified(source[:-1])
        for i in (0, 5967, 5968 + len(BLOCK), len(source) - 1):
            changed = bytearray(source); changed[i] ^= 1
            with self.subTest(i=i), self.assertRaisesRegex(ValueError, '^source SHA-256$'):
                split_verified(changed)
        for changed in (b'', BLOCK + BLOCK, source + BLOCK):
            with self.assertRaisesRegex(ValueError, '^exact block count$'):
                replace_unique(changed)


def main():
    if sys.argv[1:] == ['--test']:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() and result.testsRun == 4 else 1
    if sys.argv[1:] == ['--inspect']:
        try:
            original = SOURCE.read_bytes()
            result, offset = split_verified(original)
            print(json.dumps({'source_sha256': digest(original), 'split_sha256': digest(result),
                              'source_bytes': len(original), 'split_bytes': len(result),
                              'block_offset': offset, 'block_bytes': len(BLOCK),
                              'declaration_bytes': len(DECL), 'source_written': False,
                              'limits': 'Source-byte projection only; no compile, link, ABI or BIN proof.'}, indent=2))
            return 0
        except (OSError, ValueError) as exc:
            print('FAIL: ' + str(exc), file=sys.stderr)
            return 1
    print('usage: verify.py --inspect | --test', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
