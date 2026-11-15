#!/usr/bin/env python3
"""Offline bounded decode of 13ca2..13cb4, not a complete state callback.

Assume the prior call returned, gp and a0 are the supplied 32-bit values,
the word load succeeds, and no concurrent changes occur. This does not model
stack aliases, faults, target CPU execution, downstream calls, or reachability.
"""
import argparse
import hashlib
from pathlib import Path

BASE, PC, END = 0x8000, 0x13ca2, 0x13cb4
MASK = 0xffffffff
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE = bytes.fromhex('938741159c4313072002b307f5406379f700')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def project(code, gp, current, stored):
    need(code == CODE, 'instruction bytes mismatch')
    # Decode the non-compressed words rather than assuming their fields.
    addi = int.from_bytes(code[0:4], 'little')
    need((addi & 0x7f, (addi >> 7) & 31, (addi >> 12) & 7,
          (addi >> 15) & 31, addi >> 20) == (0x13, 15, 0, 3, 340), 'gp-relative addi')
    need(code[4:6] == b'\x9c\x43', 'compressed lw a5,0(a5)')
    li = int.from_bytes(code[6:10], 'little')
    need((li & 0x7f, (li >> 7) & 31, (li >> 12) & 7,
          (li >> 15) & 31, li >> 20) == (0x13, 14, 0, 0, 34), 'threshold')
    sub = int.from_bytes(code[10:14], 'little')
    need((sub & 0x7f, (sub >> 7) & 31, (sub >> 12) & 7,
          (sub >> 15) & 31, (sub >> 20) & 31, sub >> 25) ==
         (0x33, 15, 0, 10, 15, 0x20), 'sub')
    branch = int.from_bytes(code[14:18], 'little')
    imm = (((branch >> 31) & 1) << 12 | ((branch >> 7) & 1) << 11 |
           ((branch >> 25) & 63) << 5 | ((branch >> 8) & 15) << 1)
    if imm & 0x1000:
        imm -= 0x2000
    need((branch & 0x7f, (branch >> 12) & 7, (branch >> 15) & 31,
          (branch >> 20) & 31, PC + 14 + imm) == (0x63, 7, 14, 15, 0x13cc2), 'unsigned branch')
    delta = ((current & MASK) - (stored & MASK)) & MASK
    return ((gp + 340) & MASK, delta, 0x13cc2 if delta <= 34 else END)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    data = args.bin.read_bytes()
    need(hashlib.sha256(data).hexdigest() == SHA256, 'firmware SHA-256')
    code = data[PC-BASE:END-BASE]
    for prior in (0, 1, 0x7fffffff, 0xffffffdf, 0xfffffffe, 0xffffffff):
        for delta in range(65536):
            current = (prior + delta) & MASK
            address, difference, target = project(code, 0xffffff00, current, prior)
            need((address, difference, target) == (0x54, delta, 0x13cc2 if delta <= 34 else END),
                 'difference case')
    for delta in (65536, 0x7fffffff, 0x80000000, 0xfffffffe, 0xffffffff):
        for prior in (0, 0x80000000, 0xffffffff):
            current = (prior + delta) & MASK
            need(project(code, 0, current, prior)[1:] == (delta, END), 'wide delta')
    for offset in range(len(code)):
        bad = bytearray(code)
        bad[offset] ^= 1
        try:
            project(bad, 0, 0, 0)
        except ValueError:
            continue
        raise ValueError('mutation accepted: '+str(offset))
    print('PASS: 393216 unsigned delta cases and 15 wide boundary cases; 18 instruction-byte identity mutations rejected')
    print('LIMIT: post-call local window only; no scheduler, target execution, memory faults, or hardware')


if __name__ == '__main__':
    main()
