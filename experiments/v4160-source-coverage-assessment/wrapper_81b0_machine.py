#!/usr/bin/env python3
"""Finite RV32/RVC decoder for 81b0; injected call, not a CPU emulator.

Only the instruction forms used by this wrapper are supported. Data accesses
are assumed to succeed; interrupts, faults, instruction mutation and other
registers are excluded. The call returns to its link address; it may change
sp and data memory. Instruction fields and immediates are decoded separately
from wrapper-81b0.py's fixed-instruction projection.
"""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import random

spec = importlib.util.spec_from_file_location('wrapper', Path(__file__).with_name('wrapper-81b0.py'))
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sext(value, width):
    return value - (1 << width) if value & (1 << (width-1)) else value


def machine(code, mem, sp, ra, provider):
    r = [0] * 32
    r[2], r[1] = sp & w.MASK, ra & w.MASK
    pc = w.START
    for _ in range(20):
        offset = pc-w.START
        need(0 <= offset and offset+2 <= len(code), 'instruction fetch')
        h = int.from_bytes(code[offset:offset+2], 'little')
        q, f = h & 3, h >> 13
        if q == 3:
            need(offset+4 <= len(code), 'truncated instruction')
            inst = int.from_bytes(code[offset:offset+4], 'little')
            opcode, rd = inst & 127, (inst >> 7) & 31
            if opcode == 0x37:  # lui
                r[rd] = inst & 0xfffff000
            elif opcode == 0x33 and (inst >> 25) == 1 and ((inst >> 12) & 7) == 0:
                r[rd] = (r[(inst >> 15) & 31] * r[(inst >> 20) & 31]) & w.MASK
            else:
                raise ValueError('unsupported 32-bit instruction')
            pc += 4
        elif q == 0 and f == 2:  # c.lw
            rd, rs1 = 8+((h >> 2) & 7), 8+((h >> 7) & 7)
            imm = (((h >> 10) & 7) << 3) | (((h >> 6) & 1) << 2) | (((h >> 5) & 1) << 6)
            r[rd] = w.load32(mem, (r[rs1]+imm) & w.MASK)
            pc += 2
        elif q == 2 and f == 6:  # c.swsp
            rs2 = (h >> 2) & 31
            imm = (((h >> 9) & 15) << 2) | (((h >> 7) & 3) << 6)
            w.store32(mem, (r[2]+imm) & w.MASK, r[rs2])
            pc += 2
        elif q == 2 and f == 2:  # c.lwsp
            rd = (h >> 7) & 31
            need(rd != 0, 'reserved c.lwsp')
            imm = (((h >> 12) & 1) << 5) | (((h >> 4) & 7) << 2) | (((h >> 2) & 3) << 6)
            r[rd] = w.load32(mem, (r[2]+imm) & w.MASK)
            pc += 2
        elif q == 1 and f in (0, 2):  # c.addi / c.li
            rd = (h >> 7) & 31
            imm = sext(((h >> 2) & 31) | (((h >> 12) & 1) << 5), 6)
            r[rd] = ((r[rd] if f == 0 else 0) + imm) & w.MASK
            pc += 2
        elif q == 1 and f == 4 and ((h >> 10) & 3) == 0:  # c.srli
            rd = 8+((h >> 7) & 7)
            shift = ((h >> 2) & 31) | (((h >> 12) & 1) << 5)
            need(shift < 32, 'reserved RV32 shift')
            r[rd] >>= shift
            pc += 2
        elif q == 2 and f == 4 and ((h >> 2) & 31) == 0:
            rs1 = (h >> 7) & 31
            need(rs1 != 0, 'reserved indirect jump')
            target = r[rs1] & ~1
            if (h >> 12) & 1:  # c.jalr; injected provider returns to link
                r[1] = pc+2
                r[10], r[2] = provider(target, r[2], mem)
                r[10] &= w.MASK
                r[2] &= w.MASK
                pc += 2
            else:  # c.jr
                return r[10], r[2], r[1], target
        else:
            raise ValueError('unsupported compressed instruction')
        r[0] = 0
    raise ValueError('instruction limit')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bin', type=Path)
    args = parser.parse_args()
    image = args.bin.read_bytes()
    need(hashlib.sha256(image).hexdigest() == w.SHA256, 'firmware SHA-256')
    code = image[w.START-w.BASE:w.END-w.BASE]
    need(code == w.CODE, 'wrapper instruction identity')
    cases = 0
    for raw in range(65536):
        left, right = {}, {}
        w.store32(left, w.SLOT, 0x12345679)
        w.store32(right, w.SLOT, 0x12345679)
        def provider(target, frame, mem):
            need(target == 0x12345678, 'provider target')
            return raw, frame
        expected = w.project(code, left, 0x20001000, 0x87654321, provider)
        got = machine(code, right, 0x20001000, 0x87654321, provider)
        need(expected == got and left == right, 'machine projection mismatch')
        cases += 1
    rng = random.Random(0x81b0)
    for i in range(4096):
        left, right = {}, {}
        target, raw, ra = (rng.getrandbits(32) for _ in range(3))
        sp = 0x40080 if i % 2 else rng.getrandbits(30) << 2
        relocated_sp = 0x5000 if i % 4 == 0 else None
        for memory in (left, right):
            w.store32(memory, w.SLOT, target)
        def provider(address, frame, mem):
            need(address == target & ~1, 'indirect target')
            if relocated_sp is not None:
                w.store32(mem, relocated_sp+12, 0xabcdef01)
                return raw, relocated_sp
            return raw, frame
        expected = w.project(code, left, sp, ra, provider)
        got = machine(code, right, sp, ra, provider)
        need(expected == got and left == right, 'varied machine projection mismatch')
    print(f'PASS: {cases} finite-decoder comparisons plus 4096 varied full-width/alias cases')
    print('LIMIT: injected callee, successful data accesses, no target or device execution')


if __name__ == '__main__':
    main()
