#!/usr/bin/env python3
"""Offline finite instruction decoder for the two-record gate at 13c4e.

Assumes successful little-endian ordinary memory reads and no asynchronous
interference. Stops before either 13c9a or 13cda; does not execute the callee,
model faults, infer field names or prove reachability on the actual device.
"""
import argparse
import hashlib
from pathlib import Path

BASE, START, STOP = 0x8000, 0x13c4e, 0x13c9a
DATA = 0x2000c794
MASK = 0xffffffff
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE = bytes.fromhex('41679796ff1f83d666b479179797ff1f9387a7b3638ce60003c7570085466397e60003c747001377f70f0de383d6670041677917630cd70403c7970085466397e60483c7870093f7f70fa9c3')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits-1)) else value


def machine(code, memory):
    """Decode supported instructions only; return terminal PC and read trace."""
    need(code == CODE, 'gate instruction identity')
    regs = [0] * 32
    pc = START
    trace = []
    for _ in range(32):
        if pc in (0x13c9a, 0x13cda):
            return pc, trace
        off = pc-START
        need(0 <= off < len(code), 'pc outside window')
        ins = int.from_bytes(code[off:off+2], 'little')
        if ins & 3 != 3:
            # This window has only these four compressed encodings.
            if ins == 0x6741: regs[14] = 0x10000
            elif ins == 0x1779: regs[14] = (regs[14]-2) & MASK
            elif ins == 0x4685: regs[13] = 1
            elif ins == 0xe30d:
                pc = 0x13c9a if regs[14] != 0 else pc+2
                continue
            elif ins == 0xc3a9:
                pc = 0x13cda if regs[15] == 0 else pc+2
                continue
            else: raise ValueError('unsupported compressed instruction')
            pc += 2
            continue
        need(off+4 <= len(code), 'truncated word')
        ins = int.from_bytes(code[off:off+4], 'little')
        op, rd, f3, rs1, rs2 = ins & 127, (ins >> 7) & 31, (ins >> 12) & 7, (ins >> 15) & 31, (ins >> 20) & 31
        if op == 0x17:
            regs[rd] = (pc + sx(ins & 0xfffff000, 32)) & MASK
        elif op == 0x13 and f3 in (0, 7):
            imm = sx(ins >> 20, 12)
            regs[rd] = ((regs[rs1]+imm) if f3 == 0 else (regs[rs1] & imm)) & MASK
        elif op == 0x03 and f3 in (4, 5):
            address = (regs[rs1] + sx(ins >> 20, 12)) & MASK
            width = 1 if f3 == 4 else 2
            trace.append((address, width))
            try:
                regs[rd] = sum(memory[(address+i) & MASK] << (8*i) for i in range(width))
            except KeyError as exc:
                raise ValueError('unmapped synthetic read') from exc
        elif op == 0x63 and f3 in (0, 1):
            imm = (((ins >> 31) & 1) << 12 | ((ins >> 7) & 1) << 11 |
                   ((ins >> 25) & 63) << 5 | ((ins >> 8) & 15) << 1)
            equal = regs[rs1] == regs[rs2]
            pc = (pc + sx(imm, 13)) if equal == (f3 == 0) else pc+4
            continue
        else:
            raise ValueError('unsupported instruction')
        regs[0] = 0
        pc += 4
    raise ValueError('instruction budget exceeded')


def oracle(first, second):
    """Separately specified short-circuit behavior and actual read order."""
    trace = []
    for off, (word, tag, flag) in ((0, first), (4, second)):
        trace.append((DATA+2+off, 2))
        if word == 0xfffe:
            continue
        trace.append((DATA+5+off, 1))
        if tag != 1:
            continue
        trace.append((DATA+4+off, 1))
        if flag:
            return 0x13c9a, trace
    return 0x13cda, trace


def fixture(first, second):
    memory = {}
    for off, (word, tag, flag) in ((0, first), (4, second)):
        memory[DATA+2+off] = word & 255
        memory[DATA+3+off] = word >> 8
        memory[DATA+5+off] = tag
        memory[DATA+4+off] = flag
    return memory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    image = args.bin.read_bytes()
    need(hashlib.sha256(image).hexdigest() == SHA256, 'firmware SHA-256')
    code = image[START-BASE:STOP-BASE]
    cases = 0
    for first_word in (0, 0xfffe, 0xffff):
        for second_word in (0, 0xfffe, 0xffff):
            for tag in range(256):
                for flag in (0, 1, 255):
                    first = (first_word, tag, flag)
                    second = (second_word, 1 if tag != 1 else 0, flag)
                    need(machine(code, fixture(first, second)) == oracle(first, second), 'gate mismatch')
                    cases += 1
    for i in range(len(code)):
        bad = bytearray(code)
        bad[i] ^= 1
        try:
            machine(bad, {})
        except ValueError:
            continue
        raise ValueError('identity mutation accepted: '+str(i))
    print(f'PASS: {cases} decoded gate/trace cases; {len(code)} instruction-byte identity mutations rejected')
    print('LIMIT: static synthetic memory only; no device, callee, faults or reachability')


if __name__ == '__main__':
    main()
