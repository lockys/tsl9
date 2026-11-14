#!/usr/bin/env python3
"""Partition the conservative APP indexed-read window; not a reachability proof."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
HASH = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def run():
    data = BIN.read_bytes()
    need(len(data) == 0x12c00 and hashlib.sha256(data).hexdigest() == HASH, 'original BIN mismatch')
    at = lambda pc, n: data[pc-0x8000:pc-0x8000+n]
    # The existing residual access audit supplies the ordinary-entry reaching
    # definitions and 8-bit mode bound. Decode the PC-relative pair; rest of
    # arithmetic is checked against the original selected-function evidence.
    high = int.from_bytes(at(0xcf4e, 4), 'little')
    low = int.from_bytes(at(0xcf52, 4), 'little')
    need(high & 127 == 0x17 and (high >> 7) & 31 == 15, 'AUIPC encoding')
    need(low & 0x707f == 0x13 and (low >> 7) & 31 == (low >> 15) & 31 == 15, 'ADDI encoding')
    imm = (low >> 20) - (4096 if low >> 31 else 0)
    base = (0xcf4e + (high & 0xfffff000) + imm) & 0xffffffff
    need(base == 0x1a078, 'indexed base mismatch')
    counts = {'backed_pool': 0, 'remaining_image': 0, 'outside_image': 0, 'tail_carrier': 0}
    outside = []
    carrier = []
    for mode in range(256):
        for nibble in range(16):
            addr = base + 16 * mode + nibble
            if addr < 0x1a088:
                counts['backed_pool'] += 1
            elif addr < 0x1ac00:
                counts['remaining_image'] += 1
            else:
                counts['outside_image'] += 1
                outside.append((mode, nibble))
            if 0x1abe0 <= addr < 0x1ac00:
                counts['tail_carrier'] += 1
                carrier.append((mode, nibble))
    need(counts == {'backed_pool':16,'remaining_image':2936,'outside_image':1144,'tail_carrier':32}, 'partition counts')
    need(carrier == [(m,n) for m in range(256) for n in range(16) if (m == 182 and n >= 8) or m == 183 or (m == 184 and n < 8)], 'tail carrier preimages')
    need(outside == [(m,n) for m in range(256) for n in range(16) if m > 184 or (m == 184 and n >= 8)], 'outside preimages')
    print('PASS: 4096 mode/nibble combinations: 16 pool bytes, 2936 other image bytes, 1144 outside image')
    print('PASS: tail carrier: mode 182 nibble 8..15, mode 183 all, mode 184 nibble 0..7; 184 nibble 8..15 is outside')
    print('LIMIT: conditional arithmetic only; mode/nibble reachability, mappings, reads and hardware not established')


if __name__ == '__main__':
    run()
