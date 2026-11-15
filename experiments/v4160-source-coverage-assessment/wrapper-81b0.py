#!/usr/bin/env python3
"""Bounded 0x81b0 wrapper projection; no actual resident or target execution.

Assumes successful little-endian word accesses and a callee that returns to
0x81bc. The injected callee may alter modeled data and sp; it must not alter
subsequently executed instruction bytes. Resulting ra is loaded from that live
sp. Alignment, traps, interrupts and other registers are not modeled. The
main loop compares two hand-written formulas, not independent ISA execution.
Multiplication is modulo 2^32 before logical shift, not wide math.
"""
import argparse
import hashlib
from pathlib import Path

BASE, START, END = 0x8000, 0x81b0, 0x81ca
MASK, SLOT = 0xffffffff, 0x4007c
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE = bytes.fromhex('b7070400fc5f411106c68297a9473305f502b240410111818280')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load32(mem, address):
    try:
        return sum(mem[(address+i) & MASK] << (i*8) for i in range(4))
    except KeyError as exc:
        raise ValueError('unmapped synthetic read') from exc


def store32(mem, address, value):
    for i in range(4):
        mem[(address+i) & MASK] = (value >> (8*i)) & 255


def validate(code):
    need(code == CODE, 'wrapper instruction identity')
    # Decode the uncompressed LUI and MUL register fields; the remaining
    # compressed instructions are recognized by exact halfword encoding.
    lui = int.from_bytes(code[:4], 'little')
    need((lui & 0x7f, (lui >> 7) & 31, lui >> 12) == (0x37, 15, 0x40), 'slot base')
    mul = int.from_bytes(code[14:18], 'little')
    need((mul & 0x7f, (mul >> 7) & 31, (mul >> 12) & 7,
          (mul >> 15) & 31, (mul >> 20) & 31, mul >> 25) ==
         (0x33, 10, 0, 10, 15, 1), 'mul a0,a0,a5')
    need(code[4:14] == bytes.fromhex('fc5f411106c68297a947') and
         code[18:] == bytes.fromhex('b240410111818280'), 'compressed operations')


def project(code, mem, sp, ra, provider):
    validate(code)
    target = load32(mem, SLOT)  # fetched before frame store, including alias
    frame = (sp-16) & MASK
    saved_address = (frame+12) & MASK
    store32(mem, saved_address, ra)
    raw, live_sp = provider(target & ~1, frame, mem)
    scaled = ((raw & MASK) * 10 & MASK) >> 4
    restored_ra = load32(mem, (live_sp+12) & MASK)
    return scaled, (live_sp+16) & MASK, restored_ra, restored_ra & ~1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    image = args.bin.read_bytes()
    need(hashlib.sha256(image).hexdigest() == SHA256, 'firmware SHA-256')
    code = image[START-BASE:END-BASE]
    for raw in range(65536):
        mem = {}
        store32(mem, SLOT, 0x12345679)
        def provider(target, frame, bus):
            need(target == 0x12345678 and frame == 0x20000ff0, 'provider boundary')
            return raw, frame
        result = project(code, mem, 0x20001000, 0x87654321, provider)
        need(result == (((raw * 10) & MASK) >> 4, 0x20001000, 0x87654321, 0x87654320),
             'projection mismatch')
    for raw in (0x19999999, 0x1999999a, 0x7fffffff, 0x80000000, 0xffffffff):
        mem = {}
        store32(mem, SLOT, 0)
        result = project(code, mem, 0x20001000, 0, lambda target, frame, bus: (raw, frame))
        need(result[0] == ((raw*10) & MASK) >> 4 and result[0] <= 0x0fffffff, 'overflow')
    for i in range(len(code)):
        bad = bytearray(code)
        bad[i] ^= 1
        try:
            validate(bad)
        except ValueError:
            continue
        raise ValueError('identity mutation accepted: '+str(i))
    print('PASS: 65536 wrapper projections, 5 overflow cases, 26 byte-identity mutations')
    print('LIMIT: injected callee; no real ROM, ISA execution, faults, interrupts or device')


if __name__ == '__main__':
    main()
