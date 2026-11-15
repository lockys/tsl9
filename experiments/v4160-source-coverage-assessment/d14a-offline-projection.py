#!/usr/bin/env python3
"""Offline RV32 projection for 0xd14a; byte reads/writes assumed successful.

Memory is stable ordinary RAM. No interrupts, MMIO side effects, trap, downstream
0x13c4e behavior, terminal register equivalence, device reachability, or
original-address C integration modeled.
"""
import argparse
import hashlib
from pathlib import Path
import random

BASE = 0x8000
PC = 0xd14a
END = 0xd190
MASK = 0xffffffff
SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE = bytes.fromhex('0346350083c5810e834655000347750083479500639ec50083c5910e639ad50083c5a10e6396e50083c5b10e638cf5002384c10ea384d10e2385e10ea385f10e6f60502c8280')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def run(code, p, gp, initial):
    """Return (terminal PC, memory, ordered accesses) for this fixed sequence."""
    require(code == CODE, 'original code mismatch')
    memory = dict(initial)
    regs = [0] * 32
    regs[10], regs[3] = p & MASK, gp & MASK
    trace = []
    pc = PC
    for _ in range(32):
        if pc == 0xd18e:
            require(code[pc-PC:pc-PC+2] == b'\x82\x80', 'return instruction')
            return 'return', memory, trace
        if pc == 0x13c4e:
            return pc, memory, trace
        require(PC <= pc < END - 2 and (pc-PC) % 4 == 0, 'unexpected PC')
        w = int.from_bytes(code[pc-PC:pc-PC+4], 'little')
        op = w & 0x7f
        rd, f, rs1, rs2 = (w >> 7) & 31, (w >> 12) & 7, (w >> 15) & 31, (w >> 20) & 31
        next_pc = pc + 4
        if op == 0x03 and f == 4:
            addr = (regs[rs1] + signed(w >> 20, 12)) & MASK
            require(addr in memory, 'unmapped synthetic read')
            value = memory[addr]
            trace.append(('read', addr, value))
            if rd:
                regs[rd] = value
        elif op == 0x23 and f == 0:
            imm = ((w >> 25) << 5) | ((w >> 7) & 31)
            addr = (regs[rs1] + signed(imm, 12)) & MASK
            value = regs[rs2] & 255
            trace.append(('write', addr, value))
            memory[addr] = value
        elif op == 0x63 and f in (0, 1):
            imm = (((w >> 31) & 1) << 12 | ((w >> 7) & 1) << 11 |
                   ((w >> 25) & 63) << 5 | ((w >> 8) & 15) << 1)
            if (regs[rs1] == regs[rs2]) == (f == 0):
                next_pc = pc + signed(imm, 13)
        elif op == 0x6f and rd == 0:
            imm = (((w >> 31) & 1) << 20 | ((w >> 12) & 255) << 12 |
                   ((w >> 20) & 1) << 11 | ((w >> 21) & 1023) << 1)
            next_pc = pc + signed(imm, 21)
        else:
            raise ValueError('unsupported instruction at ' + hex(pc))
        pc = next_pc & MASK
    raise ValueError('instruction limit')


def reference(p, gp, initial):
    """Independent expression of access order; all source bytes precede writes."""
    mem = dict(initial)
    t = []
    def read(address):
        address &= MASK
        value = mem[address]
        t.append(('read', address, value))
        return value
    a = read(p+3)
    old = read(gp+232)
    b, c, d = read(p+5), read(p+7), read(p+9)
    changed = old != a
    if not changed:
        changed = read(gp+233) != b
    if not changed:
        changed = read(gp+234) != c
    if not changed:
        changed = read(gp+235) != d
    if changed:
        for off, value in enumerate((a, b, c, d), 232):
            addr = (gp + off) & MASK
            mem[addr] = value
            t.append(('write', addr, value))
    return (0x13c4e if changed else 'return'), mem, t


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('bin', type=Path)
    args = ap.parse_args()
    image = args.bin.read_bytes()
    require(hashlib.sha256(image).hexdigest() == SHA256, 'firmware SHA-256')
    code = image[PC-BASE:END-BASE]
    require(code == CODE, 'firmware bytes')
    rng = random.Random(0xd14a)
    for i in range(65536):
        gp = (0xffffff70, 0, 0x20004000, rng.getrandbits(32))[i % 4]
        p = (gp + 232 + (i % 25) - 12) & MASK
        addresses = {(p + k) & MASK for k in (3, 5, 7, 9)} | {(gp + k) & MASK for k in range(232, 236)}
        memory = {a: rng.randrange(256) for a in sorted(addresses)}
        # Mix equal and unequal paths without requiring non-aliasing.
        if i % 2 == 0:
            for s, d in zip((3, 5, 7, 9), range(232, 236)):
                memory[(gp+d) & MASK] = memory[(p+s) & MASK]
        require(run(code, p, gp, memory) == reference(p, gp, memory), 'differential case '+str(i))
    for i in range(len(code)):
        mutant = bytearray(code)
        mutant[i] ^= 1
        try:
            run(mutant, 0, 0, {})
        except ValueError:
            continue
        raise ValueError('accepted code mutation '+str(i))
    print('PASS: 65536 shared-memory projections; identity guard rejected 70 byte mutations')
    print('LIMIT: stable RAM only; no terminal register, hardware, downstream tail, or reachability evidence')


if __name__ == '__main__':
    main()
