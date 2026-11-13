#!/usr/bin/env python3
"""Bounded address arithmetic and fixed BIN anchors; does not execute firmware."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ANCHORS = {
    0xf016: '4111', 0xf018: '22c4', 0xf022: '06c6', 0xf024: '26c2',
    0xf026: 'a304b400', 0xf030: '23059400', 0xf03a: '2300f500',
    0xf03e: '2244', 0xf040: 'b240', 0xf042: '9244',
}
STORES = (0x2000bf8d, 0x2000bf8e, 0x2000bf11)
SLOTS = {'s1': 12, 's0': 8, 'ra': 4}
MASK = 0xffffffff
EXPECTED_ROWS = {
    '0x2000bf8d': {'s1': [0x2000bf96, 0x2000bf97, 0x2000bf98, 0x2000bf99], 's0': [0x2000bf92, 0x2000bf93, 0x2000bf94, 0x2000bf95], 'ra': [0x2000bf8e, 0x2000bf8f, 0x2000bf90, 0x2000bf91]},
    '0x2000bf8e': {'s1': [0x2000bf97, 0x2000bf98, 0x2000bf99, 0x2000bf9a], 's0': [0x2000bf93, 0x2000bf94, 0x2000bf95, 0x2000bf96], 'ra': [0x2000bf8f, 0x2000bf90, 0x2000bf91, 0x2000bf92]},
    '0x2000bf11': {'s1': [0x2000bf1a, 0x2000bf1b, 0x2000bf1c, 0x2000bf1d], 's0': [0x2000bf16, 0x2000bf17, 0x2000bf18, 0x2000bf19], 'ra': [0x2000bf12, 0x2000bf13, 0x2000bf14, 0x2000bf15]},
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def verify_image(image, expected_digest=SHA256):
    need(len(image) == 76800, 'BIN length')
    need(hashlib.sha256(image).hexdigest() == expected_digest, 'BIN SHA-256')
    for pc, text in ANCHORS.items():
        want = bytes.fromhex(text)
        need(image[pc - 0x8000:pc - 0x8000 + len(want)] == want,
             'anchor mismatch: 0x%x' % pc)


def intersections(target, distance, mask=MASK):
    return {(target + distance - lane) & mask for lane in range(4)}


def summarize():
    rows = {hex(t): {name: sorted(intersections(t, distance))
                     for name, distance in SLOTS.items()} for t in STORES}
    sets = [set().union(*(intersections(t, distance) for distance in SLOTS.values()))
            for t in STORES]
    union = set().union(*sets)
    return {'rows': rows, 'distinct_sp': len(union),
            'first_second_overlap': len(sets[0] & sets[1]),
            'third_previous_overlap': len(sets[2] & (sets[0] | sets[1])),
            'aligned_4': sorted(s for s in union if s % 4 == 0),
            'aligned_16': sorted(s for s in union if s % 16 == 0)}


def validate(result):
    need(result['rows'] == EXPECTED_ROWS, 'labeled rows')
    need((result['distinct_sp'], result['first_second_overlap'], result['third_previous_overlap']) == (25, 11, 0), 'counts')
    need(result['aligned_4'] == [0x2000bf14, 0x2000bf18, 0x2000bf1c, 0x2000bf90, 0x2000bf94, 0x2000bf98], '4-byte alignment')
    need(result['aligned_16'] == [0x2000bf90], '16-byte alignment')


class Tests(unittest.TestCase):
    def test_reported_ranges_and_alignment(self):
        r = summarize()
        self.assertEqual((r['distinct_sp'], r['first_second_overlap'], r['third_previous_overlap']), (25, 11, 0))
        self.assertEqual(r['aligned_4'], [0x2000bf14, 0x2000bf18, 0x2000bf1c, 0x2000bf90, 0x2000bf94, 0x2000bf98])
        self.assertEqual(r['aligned_16'], [0x2000bf90])
        self.assertEqual(r['rows'], EXPECTED_ROWS)
        validate(r)
        r['rows']['0x2000bf8d']['s1'], r['rows']['0x2000bf8d']['s0'] = r['rows']['0x2000bf8d']['s0'], r['rows']['0x2000bf8d']['s1']
        with self.assertRaisesRegex(ValueError, 'labeled rows'):
            validate(r)

    def test_independent_modular_oracle(self):
        # Exhaustive smaller ring: enumerate SP and byte addresses, not the inverse formula.
        for target in range(256):
            for distance in SLOTS.values():
                oracle = {sp for sp in range(256)
                          if target in {((sp - distance + lane) & 255) for lane in range(4)}}
                self.assertEqual(intersections(target, distance, 255), oracle)
        self.assertEqual(intersections(0xfffffffe, 4), {0xffffffff, 0, 1, 2})
        for target in (*STORES, 0, 0xffffffff):
            for name, distance in (('s1', 12), ('s0', 8), ('ra', 4)):
                candidates = {(target + delta) & MASK for delta in range(-20, 25)}
                oracle = {sp for sp in candidates if target in {((sp - distance + lane) & MASK) for lane in range(4)}}
                self.assertEqual(intersections(target, SLOTS[name]), oracle)

    def test_real_bin_and_mutations(self):
        image = BIN.read_bytes()
        verify_image(image)
        with self.assertRaisesRegex(ValueError, 'BIN length'):
            verify_image(image[:-1])
        for pc, text in ANCHORS.items():
            for i in range(len(bytes.fromhex(text))):
                changed = bytearray(image); changed[pc - 0x8000 + i] ^= 1
                with self.assertRaisesRegex(ValueError, 'BIN SHA-256'):
                    verify_image(changed)
                # Rebase digest only in this test to isolate the anchor guard.
                with self.assertRaisesRegex(ValueError, 'anchor mismatch: 0x%x' % pc):
                    verify_image(changed, hashlib.sha256(changed).hexdigest())
        changed = bytearray(image); changed[0] ^= 1
        with self.assertRaisesRegex(ValueError, 'BIN SHA-256'):
            verify_image(changed)
        verify_image(changed, hashlib.sha256(changed).hexdigest())


def main():
    if sys.argv[1:] == ['--test']:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() and result.testsRun == 3 else 1
    if sys.argv[1:] == ['--inspect']:
        try:
            verify_image(BIN.read_bytes())
            result = summarize()
            validate(result)
            result['limits'] = ('SP values mean entry SP at 0xf016, before the 16-byte frame; '
                'the live SP at a store equals entry SP minus 16 only if calls preserve SP. '
                'Assumed linear base 0x8000 and instruction boundaries; F030 address needs s0 '
                'preserved across EE9A; F03A needs BD46 to return normally. Alignment lists '
                'are hypothetical filters. No reachability, access success, slot preservation, '
                'full ABI, value effects or target execution is proved.')
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        except (OSError, ValueError) as exc:
            print('FAIL: ' + str(exc), file=sys.stderr)
            return 1
    print('usage: verify.py --inspect | --test', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
