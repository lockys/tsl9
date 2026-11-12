#!/usr/bin/env python3
"""Read-only image identity, fixed window, and independent direct-edge checks."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
PIN = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
START, END = 0x18ef2, 0x18f56
WINDOW = bytes.fromhex('372702401c4bc166137505f0d58f1ccb5c47858bf5ff372702405c47898bf5ff3727024013060010b386f50003a80600b306f50023a006015447898af5fe9107e394c7fe1c4bb7062000d58f1ccbb7270240d847058b75ff984bc176fd16758f98cb8280')
EDGES = {0x18f06: (0x18f02, 15, 0, 'c.bnez'), 0x18f10: (0x18f0c, 15, 0, 'c.bnez'), 0x18f2e: (0x18f2a, 13, 0, 'c.bnez'), 0x18f32: (0x18f1a, 15, 12, 'bne'), 0x18f48: (0x18f44, 14, 0, 'c.bnez')}


def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n


def direct(pc, raw):
    if len(raw) < 2:
        raise ValueError('truncated instruction')
    h = int.from_bytes(raw[:2], 'little')
    if h & 3 != 3:
        if h & 3 != 1 or (h >> 13) not in (6, 7):
            raise ValueError('not compressed branch')
        imm = ((h >> 12 & 1) << 8 | (h >> 10 & 3) << 3 | (h >> 5 & 3) << 6 | (h >> 3 & 3) << 1 | (h >> 2 & 1) << 5)
        return pc + signed(imm, 9), 8 + (h >> 7 & 7), 0, 'c.bnez' if h >> 13 == 7 else 'c.beqz'
    if len(raw) < 4:
        raise ValueError('truncated instruction')
    w = int.from_bytes(raw[:4], 'little')
    op = w & 127
    if op == 0x63 and (w >> 12 & 7) in (0, 1, 4, 5, 6, 7):
        imm = ((w >> 31) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1)
        return pc + signed(imm, 13), (w >> 15 & 31), (w >> 20 & 31), {0:'beq',1:'bne',4:'blt',5:'bge',6:'bltu',7:'bgeu'}[w >> 12 & 7]
    if op == 0x6f:
        imm = ((w >> 31) << 20 | (w >> 12 & 255) << 12 | (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1)
        return pc + signed(imm, 21), (w >> 7 & 31), 0, 'jal'
    raise ValueError('not supported direct edge')


def verify(data):
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != PIN:
        raise ValueError('image size or SHA-256 mismatch')
    w = data[START-0x8000:END-0x8000]
    if w != WINDOW or len(w) != END-START:
        raise ValueError('window mismatch')
    for pc, expected in EDGES.items():
        if direct(pc, w[pc-START:]) != expected:
            raise ValueError(f'edge mismatch at {pc:#x}')
    return w


def main():
    try:
        data = Path(sys.argv[1]).read_bytes() if len(sys.argv) == 2 else IMAGE.read_bytes() if len(sys.argv) == 1 else None
        if data is None:
            raise ValueError('usage: verify.py [image]')
        verify(data)
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    print('OK: pinned image, fixed window, five direct branch edges')
    return 0


if __name__ == '__main__':
    sys.exit(main())
