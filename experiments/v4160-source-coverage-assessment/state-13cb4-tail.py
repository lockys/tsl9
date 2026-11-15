#!/usr/bin/env python3
"""Offline projection of two 0x13cb4/0x13cc2 tail paths.

Inputs are values after the unsigned-difference branch. Assumes successful
ordinary memory accesses and no asynchronous interference. Restored ra is
read before the optional store; arbitrary aliasing is not otherwise modeled.
Targets are jump destinations only, not downstream execution or scheduling.
"""
import argparse
import hashlib
from pathlib import Path

BASE, START, STOP = 0x8000, 0x13cb4, 0x13cda
MASK = 0xffffffff
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE = bytes.fromhex('b24023aaa114014541016ff03fb0b240814613063002814517050000130545af41016f50efc4')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def word(code, offset):
    return int.from_bytes(code[offset:offset+4], 'little')


def sign(value, bits):
    return value - (1 << bits) if value & (1 << (bits-1)) else value


def jal_target(pc, insn):
    need((insn & 0xfff) == 0x6f, 'expected jal x0')
    imm = (((insn >> 31) & 1) << 20 | ((insn >> 12) & 0xff) << 12 |
           ((insn >> 20) & 1) << 11 | ((insn >> 21) & 0x3ff) << 1)
    return (pc + sign(imm, 21)) & MASK


def decode(code):
    need(code == CODE, 'instruction bytes mismatch')
    store = word(code, 2)
    offset = sign(((store >> 25) << 5) | ((store >> 7) & 31), 12)
    need((store & 0x7f, (store >> 12) & 7, (store >> 15) & 31,
          (store >> 20) & 31, offset) == (0x23, 2, 3, 10, 340), 'sw a0,340(gp)')
    need(code[0:2] == code[14:16] == b'\xb2\x40', 'restore ra from sp+12')
    need(code[6:10] == b'\x01\x45\x41\x01', 'immediate a0/sp')
    need(code[16:18] == b'\x81\x46' and code[22:24] == b'\x81\x45', 'scheduled a3/a1')
    li = word(code, 18)
    need((li & 0x7f, (li >> 7) & 31, (li >> 12) & 7,
          (li >> 15) & 31, li >> 20) == (0x13, 12, 0, 0, 35), 'scheduled a2')
    auipc, addi = word(code, 24), word(code, 28)
    need((auipc & 0xfff) == 0x517 and (addi & 0xfffff) == 0x50513,
         'scheduled a0 instructions')
    argument = (0x13ccc + sign(auipc & 0xfffff000, 32) + sign(addi >> 20, 12)) & MASK
    need(code[32:34] == b'\x41\x01', 'scheduled stack restore')
    direct, scheduled = jal_target(0x13cbe, word(code, 10)), jal_target(0x13cd6, word(code, 34))
    need((direct, scheduled, argument) == (0x137c0, 0x9124, 0x137c0), 'tail addresses')
    return direct, scheduled, argument, offset


def project(code, immediate, gp, sp, current, saved_ra):
    direct, scheduled, argument, offset = decode(code)
    ra = saved_ra & MASK
    restored_sp = (sp + 16) & MASK
    if immediate:
        return (ra, restored_sp, ((gp + offset) & MASK, current & MASK), direct, (0,))
    return (ra, restored_sp, None, scheduled, (argument, 0, 35, 0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    image = args.bin.read_bytes()
    need(hashlib.sha256(image).hexdigest() == SHA256, 'firmware SHA-256')
    code = image[START-BASE:STOP-BASE]
    for v in range(65536):
        gp = (0xffffff00 + v) & MASK
        current = (v * 0x10001) & MASK
        saved_ra = (0xffffffff - v) & MASK
        for immediate in (False, True):
            got = project(code, immediate, gp, 0xfffffff8, current, saved_ra)
            expected = (saved_ra, 8, ((gp + 340) & MASK, current) if immediate else None,
                        0x137c0 if immediate else 0x9124,
                        (0,) if immediate else (0x137c0, 0, 35, 0))
            need(got == expected, 'tail projection')
    for i in range(len(code)):
        bad = bytearray(code)
        bad[i] ^= 1
        try:
            decode(bad)
        except ValueError:
            continue
        raise ValueError('identity mutation accepted: '+str(i))
    print('PASS: 131072 hand-written tail model self-checks; 38 instruction-byte identity mutations rejected')
    print('LIMIT: no target execution, timing, scheduler, faults or reachability')


if __name__ == '__main__':
    main()
