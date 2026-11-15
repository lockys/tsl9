#!/usr/bin/env python3
"""Pinned original direct JAL sites to AB68; not a complete call graph."""
import argparse
import hashlib
from pathlib import Path

SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
TARGET = 0xab68
SITES = ((0x10394, bytes.fromhex('efa04ffd')),
         (0x13ac6, bytes.fromhex('ef702f8a')))

def decode_jal(pc, code):
    if len(code) != 4:
        raise ValueError('JAL length')
    w = int.from_bytes(code, 'little')
    if (w & 0x7f, (w >> 7) & 31) != (0x6f, 1):
        raise ValueError('JAL opcode or link register')
    delta = ((w >> 31) << 20) | (((w >> 12) & 255) << 12) | (((w >> 20) & 1) << 11) | (((w >> 21) & 1023) << 1)
    if delta & (1 << 20):
        delta -= 1 << 21
    return (pc + delta) & 0xffffffff

def inspect(image):
    if hashlib.sha256(image).hexdigest() != SHA256:
        raise ValueError('image SHA-256')
    for pc, expected in SITES:
        code = image[pc-BASE:pc-BASE+4]
        if code != expected:
            raise ValueError('site bytes')
        if decode_jal(pc, code) != TARGET:
            raise ValueError('JAL target')
    return tuple(pc for pc, _ in SITES)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('bin', type=Path)
    a = p.parse_args()
    for pc in inspect(a.bin.read_bytes()):
        print(f'PASS: original JAL {pc:#x} -> {TARGET:#x}, rd=ra')
    print('LIMIT: two static direct calls; not exhaustive reachability or runtime proof')

if __name__ == '__main__':
    main()
