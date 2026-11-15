#!/usr/bin/env python3
"""Decode the d314 leaf and project successful halfword reads, entirely offline.

This does not emulate a CPU, establish RAM ownership, or validate hardware access.
"""
import argparse
import hashlib
from pathlib import Path
import struct
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'v4160-8202-offline-leaf'))
import verify

PC = 0xd314
EXPECTED = bytes.fromhex('17f5ff1f035585c43335a0008280')
MASK = 0xffffffff


def decode(code):
    verify.require(len(code) == 14, 'd314 length')
    auipc, load, sltu, ret = struct.unpack('<IIIH', code)
    verify.require((auipc & 0xfff) == 0x517, 'auipc opcode or destination')
    verify.require((load & 0xfffff) == 0x55503, 'lhu opcode, registers or width')
    verify.require(sltu == 0x00a03533, 'sltu instruction')
    verify.require(ret == 0x8082, 'compressed return')
    hi = auipc & 0xfffff000
    lo = (load >> 20) & 0xfff
    lo -= (lo & 0x800) << 1
    address = (PC + hi + lo) & MASK
    verify.require(address == 0x2000bf5c, 'halfword address')
    verify.require(code == EXPECTED, 'original instructions')
    return address


def project(value):
    verify.require(isinstance(value, int) and 0 <= value <= 0xffff, 'halfword range')
    return int(value != 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    raw = args.bin.read_bytes()
    verify.require(hashlib.sha256(raw).hexdigest() == verify.IMAGE_SHA256, 'firmware SHA-256')
    code = raw[PC-verify.IMAGE_BASE:PC-verify.IMAGE_BASE+len(EXPECTED)]
    target = decode(code)
    for value in range(0x10000):
        verify.require(project(value) == (0 if value == 0 else 1), 'projection')
    for offset in range(len(code)):
        mutant = bytearray(code)
        mutant[offset] ^= 1
        try:
            decode(mutant)
        except ValueError:
            continue
        raise ValueError('accepted byte mutation at '+str(offset))
    print('d314:', code.hex(), 'lhu address:', hex(target), '65536 values, 14 byte mutations rejected')
    print('LIMIT: successful read projection only; not CPU, RAM binding, reachability or hardware evidence')


if __name__ == '__main__':
    main()
