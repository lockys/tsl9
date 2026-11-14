"""Decode ingress length gate and compare its range with dispatcher arithmetic.

This composes numerical predicates only, not the intervening control flow.
"""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def gate(raw, length):
    if len(raw) != 8 or not 1 <= length <= 65535:
        raise ValueError('expected nonzero 16-bit length at ingress gate')
    addi = int.from_bytes(raw[:4], 'little')
    if (addi & 127, (addi >> 7) & 31, (addi >> 12) & 7, (addi >> 15) & 31) != (0x13, 13, 0, 0):
        raise ValueError('expected addi a3,zero,immediate')
    limit = (addi >> 20) & 0xfff
    if limit & 0x800:
        limit -= 0x1000
    limit &= 0xffffffff
    branch = int.from_bytes(raw[4:], 'little')
    if (branch & 127, (branch >> 12) & 7, (branch >> 15) & 31, (branch >> 20) & 31) != (0x63, 6, 13, 14):
        raise ValueError('expected bltu a3,a4')
    imm = ((branch >> 31 & 1) << 12 | (branch >> 7 & 1) << 11 |
           (branch >> 25 & 63) << 5 | (branch >> 8 & 15) << 1)
    if imm & 0x1000:
        imm -= 0x2000
    return 0x89e4 + imm if limit < length else 0x89e8


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    raw = image[0x89e0 - 0x8000:0x89e8 - 0x8000]
    if raw != bytes.fromhex('9306004163e6e600'):
        raise ValueError('ingress gate bytes mismatch')
    candidates = []
    for length in range(1, 65536):
        pc = gate(raw, length)
        if pc != (0x89e8 if length <= 1040 else 0x89f0):
            raise ValueError(f'ingress gate mismatch at {length}')
        if pc == 0x89e8 and ((length - 2) & 65535) >> 1 > 255:
            candidates.append(length)
    if candidates != [1, *range(514, 1041)]:
        raise ValueError('incorrect arithmetic intersection')
    # Alter the comparison limit: the boundary test must detect a difference.
    mutant = bytearray(raw)
    mutant[2] ^= 0x10
    if gate(mutant, 1041) == gate(raw, 1041):
        raise ValueError('limit mutation was not detected')
    print('PASS: 65535 nonzero ingress gate inputs; 527 values 514-1040 plus 1 intersect high-bound arithmetic; no reachability claimed')


if __name__ == '__main__':
    main()
