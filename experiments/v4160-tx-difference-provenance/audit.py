"""Read-only fixed-image audit; swaps exist only as transient Python bytes."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
CANDIDATE = ROOT / 'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin'
SHA_OFFICIAL = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SHA_CANDIDATE = '28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89'
SIZE, BASE = 76800, 0x8000
START, END = 0x8a56, 0x8b6e
RANGES = ((0x8a7f, 0x8a81), (0x8ad3, 0x8ad5), (0x8b11, 0x8b12),
          (0x8b13, 0x8b5c), (0x8b5d, 0x8b6c))
EXPECTED = tuple(a for lo, hi in RANGES for a in range(lo, hi))


def check_image(data, digest):
    if len(data) != SIZE or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError('image size or SHA-256 mismatch')


def check_range(start, end):
    if (start, end) != (START, END) or end - start != 280:
        raise ValueError('TX range mismatch')


def check_differences(a, b):
    if len(a) != SIZE or len(b) != SIZE:
        raise ValueError('image size mismatch')
    differences = tuple(BASE + i for i, (x, y) in enumerate(zip(a, b)) if x != y)
    if differences != EXPECTED or len(differences) != 93:
        raise ValueError('difference addresses mismatch')
    if any(not START <= address < END for address in differences):
        raise ValueError('difference outside TX')


def check_outside(a, b, start, end):
    check_range(start, end)
    if len(a) != SIZE or len(b) != SIZE:
        raise ValueError('image size mismatch')
    lo, hi = start - BASE, end - BASE
    if a[:lo] != b[:lo] or a[hi:] != b[hi:]:
        raise ValueError('outside TX differs')


def check_swap(destination, donor, reference, start, end):
    check_range(start, end)
    if any(len(image) != SIZE for image in (destination, donor, reference)):
        raise ValueError('image size mismatch')
    lo, hi = start - BASE, end - BASE
    if destination[:lo] + donor[lo:hi] + destination[hi:] != reference:
        raise ValueError('swapped image differs from reference')


def audit():
    official, candidate = OFFICIAL.read_bytes(), CANDIDATE.read_bytes()
    check_image(official, SHA_OFFICIAL)
    check_image(candidate, SHA_CANDIDATE)
    check_range(START, END)
    check_differences(official, candidate)
    check_outside(official, candidate, START, END)
    check_swap(official, candidate, candidate, START, END)
    check_swap(candidate, official, official, START, END)
    print('OK: pinned images; 93 fixed differences in TX; outside equal; both in-memory swaps match')


if __name__ == '__main__':
    audit()
