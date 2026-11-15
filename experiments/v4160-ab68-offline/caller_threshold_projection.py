#!/usr/bin/env python3
"""Bounded decoder for the post-getter fragment at 0x10398..0x103ae.

Successful ordinary byte load and stable instruction bytes are assumed. This is
not a full CPU, a provider model, a reachability proof, or device execution.
"""
import hashlib
from pathlib import Path

START = 0x10398
CODE = bytes.fromhex('95473305f50203c7411329051375f50f93170501c183')
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BIN = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
MASK = 0xffffffff


def run(code, returned, gp, memory):
    if code != CODE:
        raise ValueError('instruction bytes')
    r = [0] * 32
    r[10], r[3] = returned & MASK, gp & MASK
    events = []
    offset = 0
    while offset < len(code):
        half = int.from_bytes(code[offset:offset + 2], 'little')
        if half & 3 != 3:
            if half == 0x4795:  # c.li a5,5
                r[15] = 5
            elif half == 0x0529:  # c.addi a0,10
                r[10] = (r[10] + 10) & MASK
            elif half == 0x83c1:  # c.srli a5,16
                r[15] >>= 16
            else:
                raise ValueError('unsupported compressed instruction')
            offset += 2
            continue
        word = int.from_bytes(code[offset:offset + 4], 'little')
        op, rd, funct, rs1, rs2, upper = (word & 127, (word >> 7) & 31,
            (word >> 12) & 7, (word >> 15) & 31, (word >> 20) & 31, word >> 25)
        imm = word >> 20
        signed = imm - 4096 if imm & 2048 else imm
        if op == 0x33 and funct == 0 and upper == 1:  # mul
            r[rd] = (r[rs1] * r[rs2]) & MASK
        elif op == 0x03 and funct == 4:  # lbu
            address = (r[rs1] + signed) & MASK
            r[rd] = memory[address]
            events.append(('read', address, r[rd]))
        elif op == 0x13 and funct == 7:  # andi
            r[rd] = r[rs1] & (signed & MASK)
        elif op == 0x13 and funct == 1 and upper == 0:  # slli
            r[rd] = (r[rs1] << (rs2 & 31)) & MASK
        else:
            raise ValueError('unsupported instruction')
        r[0] = 0
        offset += 4
    return r[10], r[14], r[15], events


def main():
    image = BIN.read_bytes()
    if hashlib.sha256(image).hexdigest() != SHA or image[START-0x8000:START-0x8000+len(CODE)] != CODE:
        raise ValueError('original firmware identity')
    cases = 0
    for value in range(256):
        for state in range(256):
            gp = (0x20004000, 0xfffffed0)[state & 1]
            addr = (gp + 308) & MASK
            threshold = (5 * value + 10) & 255
            expected = (threshold, state, threshold, [('read', addr, state)])
            if run(CODE, value, gp, {addr: state}) != expected:
                raise ValueError('projection mismatch')
            cases += 1
    print(f'PASS: {cases} finite decoder / arithmetic oracle cases')
    print('LIMIT: stops before branch at 0x103ae; synthetic ordinary memory only')


if __name__ == '__main__':
    main()
