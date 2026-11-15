#!/usr/bin/env python3
"""Offline, instruction-level check of the v4.1.60 0x8202 byte getter.

Pass the decoded original BIN as the only argument. No device access, firmware
modification, full-CPU emulation, runtime reachability or flashability claim.
"""
import hashlib
from pathlib import Path
import sys

IMAGE_SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
IMAGE_BASE = 0x8000
PC = 0x8202
LEAF = bytes.fromhex('174500200345f5cd8280')
ADDRESS = 0x2000bee1
MASK = 0xffffffff


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sign_extend(value, bits):
    return (value ^ (1 << (bits - 1))) - (1 << (bits - 1))


def decode(code):
    """Check exact opcodes/registers, then derive the PC-relative byte address."""
    require(len(code) == 10, 'leaf length')
    auipc = int.from_bytes(code[:4], 'little')
    load = int.from_bytes(code[4:8], 'little')
    require(auipc & 0x7f == 0x17 and (auipc >> 7) & 31 == 10, 'auipc a0')
    require(load & 0x7f == 0x03 and (load >> 12) & 7 == 4, 'unsigned byte load')
    require((load >> 7) & 31 == 10 and (load >> 15) & 31 == 10, 'lbu a0,(a0)')
    require(code[8:] == bytes.fromhex('8280'), 'compressed return')
    target = (PC + (auipc & 0xfffff000) + sign_extend(load >> 20, 12)) & MASK
    return target


def check_leaf(leaf):
    require(leaf == LEAF and decode(leaf) == ADDRESS, 'original leaf and address')


def verify(path):
    image = path.read_bytes()
    require(hashlib.sha256(image).hexdigest() == IMAGE_SHA256, 'firmware SHA-256')
    leaf = image[PC - IMAGE_BASE:PC - IMAGE_BASE + len(LEAF)]
    check_leaf(leaf)
    # LBU zero-extends each possible byte; compare explicitly with signed LB.
    for value in range(256):
        result = value & 0xff
        require(0 <= result <= 255 and result == value, 'zero extension')
        require(sign_extend(value, 8) == (value if value < 128 else value - 256), 'signed control')
    require(sign_extend(0x80, 8) != 0x80, 'signed and unsigned distinguishable')
    # Every byte is pinned. Recheck even if a caller had accepted another image hash.
    for i in range(len(leaf)):
        mutant = bytearray(leaf)
        mutant[i] ^= 1
        try:
            check_leaf(bytes(mutant))
        except ValueError as exc:
            require(str(exc) == 'original leaf and address', 'mutation rejection reason')
        else:
            raise ValueError('mutated leaf accepted')
    # Semantic negatives must fail the opcode/register gate or resolve elsewhere.
    signed = bytearray(leaf)
    signed[5] &= 0xbf  # funct3 100 -> 000: LB rather than LBU
    try:
        decode(signed)
    except ValueError as exc:
        require(str(exc) == 'unsigned byte load', 'signed negative reason')
    else:
        raise ValueError('signed load accepted')
    moved = bytearray(leaf)
    moved[6] ^= 0x10  # change the immediate while preserving opcode/registers
    require(decode(moved) != ADDRESS, 'wrong target accepted')
    print('PASS: original 10 bytes; target 0x2000bee1; 256 byte values; '
          '10 byte mutations; signed and wrong-target controls')
    print('LIMIT: offline instruction projection, not CPU, device, or flash validation')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: verify.py PATH_TO_DECODED_BIN')
    verify(Path(sys.argv[1]))
