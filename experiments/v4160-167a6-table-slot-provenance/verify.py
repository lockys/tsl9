#!/usr/bin/env python3
"""Offline, byte-level checks; addresses use the 0x8000 image base."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
WINDOWS = {
    0x186aa: bytes.fromhex('97c1fe1f938161951781ff1f1301e194172500001305654a938501001386010863fac5008322050023a0550011059105e3eac5fe'),
    0x1abc0: bytes.fromhex('94c4002094c5002094c60020'),
    0x167a6: bytes.fromhex('011122cc26ca4ac84ec606ce52c456c2aa840144938901061309e00f83a70900a29703c707006316970003c51700efe0dfdf0904e31424ff9d4a054493894106138a81061309400203a709005697834607000347170093771700a207d58f63989700098b09c7a2850145ef10a01703270a005697834607000347170093771700a207d58f6398f400098b09c7a2850545ef10401505041374f40f9d0ae31624fb'),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check_windows(data):
    for address, expected in WINDOWS.items():
        offset = address - BASE
        need(data[offset:offset + len(expected)] == expected, 'window mismatch at %#x' % address)


def stores(data):
    """All 2-byte aligned 32-bit standard gp-base store bit patterns, including data."""
    for pos in range(0, len(data) - 3, 2):
        ins = int.from_bytes(data[pos:pos + 4], 'little')
        funct3 = (ins >> 12) & 7
        if ins & 0x7f != 0x23 or (ins >> 15) & 31 != 3 or funct3 not in (0, 1, 2):
            continue
        imm = ((ins >> 25) << 5) | ((ins >> 7) & 31)
        if imm & 0x800:
            imm -= 0x1000
        width = 1 << funct3
        if imm < 0x6c and imm + width > 0x60:
            yield (pos, imm, width)


def encode_store(imm, width, rs1=3):
    u = imm & 0xfff
    funct3 = {1: 0, 2: 1, 4: 2}[width]
    return (((u >> 5) << 25) | (7 << 20) | (rs1 << 15) |
            (funct3 << 12) | ((u & 31) << 7) | 0x23).to_bytes(4, 'little')


def self_test(data):
    # Exhaustive signed S-immediates, all three widths, at both halfword positions.
    for width in (1, 2, 4):
        for imm in range(-2048, 2048):
            encoded = encode_store(imm, width)
            overlap = imm <= 0x6b and imm + width - 1 >= 0x60
            for prefix in (b'', b'\x00\x00'):
                actual = list(stores(prefix + encoded))
                expected = [(len(prefix), imm, width)] if overlap else []
                need(actual == expected, 'synthetic store mismatch: %d %d' % (width, imm))
            need(not list(stores(encode_store(imm, width, 4))), 'wrong base accepted')
    for n in range(4):
        need(not list(stores(encode_store(0x60, 4)[:n])), 'truncated store accepted')
    need(not list(stores(b'\x00' + encode_store(0x60, 4))), 'odd-aligned store accepted')
    # Every byte of each evidence window independently matters, without hash gate.
    for address, expected in WINDOWS.items():
        for i in range(len(expected)):
            changed = bytearray(data)
            changed[address - BASE + i] ^= 1
            try:
                check_windows(changed)
            except ValueError:
                continue
            raise ValueError('window mutation escaped at %#x' % (address + i))
    # Independent image identity gate detects mutations even outside windows.
    changed = bytearray(data)
    changed[0] ^= 1
    need(hashlib.sha256(changed).hexdigest() != SHA256, 'hash mutation escaped')


def main():
    data = IMAGE.read_bytes()
    need(len(data) == 76800, 'image size mismatch')
    need(hashlib.sha256(data).hexdigest() == SHA256, 'image SHA-256 mismatch')
    check_windows(data)
    entries = [int.from_bytes(data[0x1abc0 - BASE + i:0x1abc4 - BASE + i], 'little') for i in (0, 4, 8)]
    need(entries == [0x2000c494, 0x2000c594, 0x2000c694], 'initializer entries mismatch')
    hits = list(stores(data))
    need(not hits, 'overlapping gp store bit patterns: %r' % (hits,))
    first = max(i + 1 for i in range(0, 254, 2))
    other = max(7 * i + 1 for i in range(1, 36))
    need((first, other) == (253, 246), 'loop bound mismatch')
    self_test(data)
    print('OK: image identity, three exact windows, initializer slots, raw store scan and synthetic tests')
    print('Conditional maximum accessed offsets: first +%d; second and third +%d' % (first, other))


if __name__ == '__main__':
    main()
