#!/usr/bin/env python3
"""Offline instruction-bound projection, not a CPU emulator or runtime proof."""
import argparse
import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'v4160-8202-offline-leaf'))
import verify

LEAVES = {0x10402: (5, 80, bytes.fromhex('03d501058280')),
          0x10408: (4, 82, bytes.fromhex('03c521058280'))}


def decode(code, funct3, offset, expected):
    verify.require(code == expected and len(code) == 6, 'original instruction bytes')
    insn = int.from_bytes(code[:4], 'little')
    verify.require((insn & 127) == 3, 'load opcode')
    verify.require((insn >> 7) & 31 == 10, 'destination a0')
    verify.require((insn >> 12) & 7 == funct3, 'unsigned load width')
    verify.require((insn >> 15) & 31 == 3, 'base gp')
    immediate = insn >> 20
    immediate -= 4096 if immediate & 0x800 else 0
    verify.require(immediate == offset, 'GP offset')
    verify.require(code[4:] == bytes.fromhex('8280'), 'compressed return')
    return 2 if funct3 == 5 else 1, immediate


def project(code, spec, gp, memory):
    width, offset = decode(code, *spec)
    address = (gp + offset) & 0xffffffff
    return sum(memory[(address + i) & 0xffffffff] << (8*i) for i in range(width))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    image = args.bin.read_bytes()
    verify.require(hashlib.sha256(image).hexdigest() == verify.IMAGE_SHA256, 'firmware SHA-256')
    for pc, spec in LEAVES.items():
        code = image[pc-verify.IMAGE_BASE:pc-verify.IMAGE_BASE+6]
        width, offset = decode(code, *spec)
        # Exhaust every possible loaded value, with wraparound addressing as a
        # separate mathematical case. Successful loads and stable GP are assumed.
        for gp in (0x20004000, (0xffffffff-offset) & 0xffffffff):
            addr = (gp+offset) & 0xffffffff
            for value in range(1 << (8*width)):
                memory = {(addr+i) & 0xffffffff: (value >> (8*i)) & 255 for i in range(width)}
                verify.require(project(code, spec, gp, memory) == value, 'unsigned load projection')
        for i in range(len(code)):
            mutant = bytearray(code)
            mutant[i] ^= 1
            try:
                decode(bytes(mutant), *spec)
            except ValueError:
                continue
            raise ValueError('mutated instruction accepted at byte ' + str(i))
        print(hex(pc), 'width', width, 'gp_offset', offset, 'values_per_gp', 1 << (8*width),
              'gp_cases', 2, 'byte_mutants_rejected', len(code))
    print('LIMIT: mathematical load projection; no trap, concurrency, CPU or device evidence')


if __name__ == '__main__':
    main()
