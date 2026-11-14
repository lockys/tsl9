"""Decode 0x1070a call sequence with synthetic call stubs, not provider bodies."""
import hashlib
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
TARGETS = {0x10032, 0x1061c, 0x9af0, 0x90b0, 0x13572468}
VOLATILE = (5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 28, 29, 30, 31)


def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n


def run(image, a0, a1, seed):
    r = [0] * 32
    r[1], r[2], r[8], r[9], r[18], r[10], r[11] = 0x14800, 0x20002000, 0x1111, 0x2222, 0x3333, a0, a1
    stack = {}
    events = []
    pc = 0x1070a
    for _ in range(80):
        if pc == 0x14800:
            return events, (r[1], r[2], r[8], r[9], r[18]), stack
        if pc in TARGETS:
            events.append((pc, r[10], r[11], r[12], r[1], r[2]))
            # Stub convention: preserve sp and callee-saved registers, return via ra;
            # intentionally poison caller-saved registers to expose dependencies.
            for reg in VOLATILE:
                r[reg] = (seed + reg * 0x10203 + len(events)) & MASK
            pc = r[1]
            continue
        if not 0x1070a <= pc < 0x1074c or pc & 1:
            raise ValueError(f'unexpected PC {pc:#x}')
        off = pc - 0x8000
        h = int.from_bytes(image[off:off+2], 'little')
        if h & 3 != 3:
            if h == 0x1141: r[2] = (r[2] - 16) & MASK
            elif h == 0xc606: stack[(r[2] + 12) & MASK] = r[1]
            elif h == 0x4501: r[10] = 0
            elif h == 0x47bc:
                if (r[15] + 72) & MASK != 0x40048: raise ValueError('unexpected indirect pointer address')
                r[15] = 0x13572468
            elif h == 0x4631: r[12] = 12
            elif h == 0x4581: r[11] = 0
            elif h == 0x9782:
                target = r[15] & ~1
                r[1] = pc + 2
                pc = target
                continue
            elif h == 0x40b2:
                address = (r[2] + 12) & MASK
                if address not in stack: raise ValueError('missing saved return address')
                r[1] = stack[address]
            elif h == 0x0141: r[2] = (r[2] + 16) & MASK
            else: raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
            pc += 2
        else:
            w = int.from_bytes(image[off:off+4], 'little')
            op, rd, f3, rs1 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31
            if op == 0x17:
                r[rd] = (pc + (w & 0xfffff000)) & MASK
                pc += 4
            elif op == 0x37:
                r[rd] = w & 0xfffff000
                pc += 4
            elif op == 0x13 and f3 == 0:
                r[rd] = (r[rs1] + signed(w >> 20, 12)) & MASK
                pc += 4
            elif op == 0x6f:
                imm = (w >> 31 & 1) << 20 | (w >> 12 & 255) << 12 | (w >> 20 & 1) << 11 | (w >> 21 & 1023) << 1
                target = (pc + signed(imm, 21)) & MASK
                if rd: r[rd] = pc + 4
                pc = target
            else: raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        r[0] = 0
    raise ValueError('instruction budget exceeded')


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    for a0 in (0, 1, 0xffff, 0x10000, MASK):
        for a1 in (0, 2, MASK):
            for seed in (0, 0x55555555, MASK):
                events, preserved, stack = run(image, a0, a1, seed)
                if [e[0] for e in events] != [0x10032, 0x1061c, 0x13572468, 0x9af0, 0x90b0, 0x90b0]:
                    raise ValueError('call sequence mismatch')
                if events[0][1:3] != (a0, a1) or events[1][1] != 0 or events[2][1:4] != (0x2000bfb8, 0, 12):
                    raise ValueError('call arguments mismatch')
                if events[4][1] != 0x9b36 or events[5][1] != 0x107c0:
                    raise ValueError('callback argument mismatch')
                if events[-1][4:6] != (0x14800, 0x20002000) or preserved != (0x14800, 0x20002000, 0x1111, 0x2222, 0x3333):
                    raise ValueError('tail call or callee-saved registers mismatch')
                if stack != {0x20001ffc: 0x14800}: raise ValueError('stack projection mismatch')
    mutant = bytearray(image)
    mutant[0x1072a - 0x8000] ^= 4
    try: run(mutant, 7, 2, 0)
    except ValueError: pass
    else: raise ValueError('indirect call opcode mutation missed')
    print('PASS: 45 synthetic callback traces, caller-saved clobbers, indirect arguments and tail return; provider bodies not executed')


if __name__ == '__main__': main()
