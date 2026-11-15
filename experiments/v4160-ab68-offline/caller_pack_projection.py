#!/usr/bin/env python3
"""Finite decoder for 0x13aca..0x13af0 after AB68 returns.

Assumes successful ordinary byte memory accesses and stable code. It stops before
0xab72. The three compressed opcodes are intentionally exact-match instructions,
not a general RV32C decoder. This is not device execution or a reachability proof.
"""
import hashlib
from pathlib import Path

PC = 0x13aca
MASK = 0xffffffff
CODE = bytes.fromhex('93771500139777008347b10205813d8993f7f707d98fa305f1028347c102c19b5d8d2306a102')
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BIN = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'


def run(code, v, sp, memory):
    if code != CODE:
        raise ValueError('instruction bytes')
    r = [0] * 32
    r[10], r[2] = v & MASK, sp & MASK
    mem = dict(memory)
    events = []
    pos = 0
    while pos < len(code):
        h = int.from_bytes(code[pos:pos+2], 'little')
        if h & 3 != 3:
            if h == 0x8105:  # c.srli a0,1
                r[10] >>= 1
            elif h == 0x893d:  # c.andi a0,15
                r[10] &= 15
            elif h == 0x8fd9:  # c.or a5,a4
                r[15] |= r[14]
            elif h == 0x9bc1:  # c.andi a5,-16
                r[15] &= 0xfffffff0
            elif h == 0x8d5d:  # c.or a0,a5
                r[10] |= r[15]
            else:
                raise ValueError('compressed instruction')
            pos += 2
            continue
        w = int.from_bytes(code[pos:pos+4], 'little')
        op, rd, f, rs1, rs2 = w & 127, (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31
        imm = w >> 20
        signed = imm - 4096 if imm & 2048 else imm
        if op == 0x13 and f == 7:
            r[rd] = r[rs1] & (signed & MASK)
        elif op == 0x13 and f == 1 and (imm >> 5) == 0:
            r[rd] = (r[rs1] << (imm & 31)) & MASK
        elif op == 0x03 and f == 4:
            addr = (r[rs1] + signed) & MASK
            r[rd] = mem[addr]
            events.append(('read', addr, r[rd]))
        elif op == 0x23 and f == 0:
            off = ((w >> 25) << 5) | ((w >> 7) & 31)
            off = off - 4096 if off & 2048 else off
            addr = (r[rs1] + off) & MASK
            mem[addr] = r[rs2] & 255
            events.append(('write', addr, mem[addr]))
        else:
            raise ValueError('unsupported instruction')
        r[0] = 0
        pos += 4
    return mem, events


def main():
    image = BIN.read_bytes()
    if hashlib.sha256(image).hexdigest() != SHA or image[PC-0x8000:0x13af0-0x8000] != CODE:
        raise ValueError('original firmware identity')
    cases = 0
    for v in range(256):
        for old in range(256):
            sp = (0x20001000, 0xffffffd5)[old & 1]
            a, b = (sp+43) & MASK, (sp+44) & MASK
            initial = {a: old, b: old ^ 0xa5}
            mem, events = run(CODE, v, sp, initial)
            expected_a = (initial[a] & 0x7f) | ((v & 1) << 7)
            expected_b = (initial[b] & 0xf0) | ((v >> 1) & 15)
            expected = [('read', a, initial[a]), ('write', a, expected_a),
                        ('read', b, initial[b]), ('write', b, expected_b)]
            if events != expected or mem != {a: expected_a, b: expected_b}:
                raise ValueError('projection mismatch')
            cases += 1
    print(f'PASS: {cases} original-instruction fragment / handwritten oracle cases')
    print('LIMIT: synthetic ordinary memory; stops before 0xab72; not device execution')


if __name__ == '__main__':
    main()
