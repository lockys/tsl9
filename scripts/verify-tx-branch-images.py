#!/usr/bin/env python3
"""Check the TX loop branch in two pinned offline images; never flash."""
import argparse
import hashlib
import json
from pathlib import Path

BASE, SIZE, PC = 0x8000, 76800, 0x8b10
REF_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CAND_SHA = '28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89'
REF_BYTES = bytes.fromhex('63618504')
CAND_BYTES = bytes.fromhex('637f8500')


def decode(raw, pc=PC):
    if len(raw) != 4:
        raise ValueError('branch length')
    w = int.from_bytes(raw, 'little')
    if w & 127 != 0x63 or (w >> 12) & 7 not in (6, 7):
        raise ValueError('not BLTU/BGEU')
    imm = ((w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 |
           (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
    if imm & 0x1000:
        imm -= 0x2000
    return ((w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31, pc + imm)


def check_branches(ref, candidate):
    if (decode(ref), decode(candidate)) != ((6, 10, 8, 0x8b52), (7, 10, 8, 0x8b2e)):
        raise ValueError('branch decode mismatch')
    if ref != REF_BYTES or candidate != CAND_BYTES:
        raise ValueError('branch bytes mismatch')


def read_image(path, expected):
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != SIZE or digest != expected:
        raise ValueError('image size or SHA-256 mismatch: ' + str(path))
    return data, digest


def verify(reference, candidate):
    ref, rh = read_image(reference, REF_SHA)
    cand, ch = read_image(candidate, CAND_SHA)
    offset = PC - BASE
    a, b = ref[offset:offset+4], cand[offset:offset+4]
    check_branches(a, b)
    return {'passed': True, 'reference': {'path': str(reference), 'sha256': rh, 'bytes': a.hex(), 'decode': decode(a)},
            'candidate': {'path': str(candidate), 'sha256': ch, 'bytes': b.hex(), 'decode': decode(b)},
            'pc': hex(PC), 'freshness_independently_proved': False, 'reference_authenticated': False,
            'full_behavior_equivalence_proved': False, 'target_execution': False, 'flashable_proved': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.reference, args.candidate), indent=2))
