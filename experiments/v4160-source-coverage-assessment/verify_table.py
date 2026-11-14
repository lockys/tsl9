#!/usr/bin/env python3
"""Check the relative table's actual base against the pinned v4.1.60 APP.

This is a static byte/data check, not a complete control-flow or hardware proof.
"""
import hashlib
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x1a6a4
TARGETS = (0x1452e, 0x1453e, 0x1454a, 0x1473e, 0x14748)


def decode(data, base):
    if len(data) != 20:
        raise ValueError('expected five 32-bit entries')
    return tuple((base + offset) & 0xffffffff for offset in struct.unpack('<5i', data))


def check(data, base=BASE):
    if decode(data, base) != TARGETS:
        raise ValueError('relative target mismatch')


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    table = image[BASE - 0x8000:BASE - 0x8000 + 20]
    check(table)
    try:
        check(table, 0x1a6a0)
    except ValueError:
        pass
    else:
        raise ValueError('incorrect base accepted')
    for i in range(20):
        mutant = bytearray(table)
        mutant[i] ^= 1
        try:
            check(mutant)
        except ValueError:
            continue
        raise ValueError(f'byte mutation {i} accepted')
    for bad in (table[:-1], table+b'\0'):
        try:
            check(bad)
        except ValueError:
            continue
        raise ValueError('incorrect table length accepted')
    print('PASS: pinned APP, five signed offsets relative to 0x1a6a4')
    print('PASS: wrong 0x1a6a0 base, 20 single-byte mutations, and two length mutations rejected')
    print('Static data only; no claim about reachability or hardware.')


if __name__ == '__main__':
    main()
