"""Decode 0x90b0's lookup up to first match or no-match return.

Table words are synthetic, stable and readable; the matching continuation and
all device, scheduler and concurrency behavior are outside this projection.
"""
import hashlib
import random
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
MASK = 0xffffffff
BASE = 0x2000be08


def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits - 1)) else n


def run(image, key, entries):
    if not 0 <= key <= MASK or len(entries) != 15 or any(not 0 <= x <= MASK for x in entries):
        raise ValueError('invalid inputs')
    r = [0] * 32
    r[1], r[2], r[8], r[9], r[10] = 0x14800, 0x20002000, 0x22222222, 0x33333333, key
    table = {BASE + 4 + i * 12: value for i, value in enumerate(entries)}
    stack, reads, pc = {}, [], 0x90b0
    for _ in range(100):
        if pc == 0x90cc:
            return 'match', r[8], reads, (r[2], r[9], r[10])
        if pc == 0x14800:
            return 'miss', r[10], reads, (r[2], r[8], r[9])
        if not 0x90b0 <= pc < 0x9124 or pc & 1: raise ValueError(f'unexpected PC {pc:#x}')
        off = pc - 0x8000
        h = int.from_bytes(image[off:off+2], 'little')
        if h & 3 != 3:
            if h == 0x1141: r[2] -= 16
            elif h == 0xc422: stack[r[2] + 8] = r[8]
            elif h == 0xc226: stack[r[2] + 4] = r[9]
            elif h == 0xc606: stack[r[2] + 12] = r[1]
            elif h == 0x4401: r[8] = 0
            elif h == 0x84be: r[9] = r[15]
            elif h == 0x473d: r[14] = 15
            elif h == 0x43d4:
                address = (r[15] + 4) & MASK
                if address not in table: raise ValueError(f'unexpected table address {address:#x}')
                reads.append(address)
                r[13] = table[address]
            elif h == 0x0405: r[8] = (r[8] + 1) & MASK
            elif h == 0x07b1: r[15] = (r[15] + 12) & MASK
            elif h == 0x40b2: r[1] = stack[r[2] + 12]
            elif h == 0x4422: r[8] = stack[r[2] + 8]
            elif h == 0x4492: r[9] = stack[r[2] + 4]
            elif h == 0x4505: r[10] = 1
            elif h == 0x0141: r[2] += 16
            elif h == 0x8082:
                pc = r[1] & ~1
                continue
            else: raise ValueError(f'unsupported compressed instruction {h:#x} at {pc:#x}')
            pc += 2
        else:
            w = int.from_bytes(image[off:off+4], 'little')
            op, rd, f3, rs1, rs2 = w & 127, w >> 7 & 31, w >> 12 & 7, w >> 15 & 31, w >> 20 & 31
            if op == 0x17:
                r[rd] = (pc + (w & 0xfffff000)) & MASK
                pc += 4
            elif op == 0x13 and f3 == 0:
                r[rd] = (r[rs1] + signed(w >> 20, 12)) & MASK
                pc += 4
            elif op == 0x63 and f3 == 1:
                imm = (w >> 31 & 1) << 12 | (w >> 7 & 1) << 11 | (w >> 25 & 63) << 5 | (w >> 8 & 15) << 1
                pc = (pc + signed(imm, 13)) & MASK if r[rs1] != r[rs2] else pc + 4
            else: raise ValueError(f'unsupported instruction {w:#x} at {pc:#x}')
        r[0] = 0
    raise ValueError('instruction budget exceeded')


def check(image, key, entries):
    result, value, reads, state = run(image, key, entries)
    index = next((i for i, item in enumerate(entries) if item == key), None)
    expected_reads = [BASE + 4 + 12*i for i in range(15 if index is None else index + 1)]
    if reads != expected_reads: raise ValueError('read sequence mismatch')
    if index is None:
        if (result, value, state) != ('miss', 1, (0x20002000, 0x22222222, 0x33333333)):
            raise ValueError('miss state mismatch')
    elif (result, value, state) != ('match', index, (0x20001ff0, BASE, key)):
        raise ValueError('match state mismatch')


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA: raise ValueError('firmware identity mismatch')
    for i in range(15):
        entries = [0] * 15
        entries[i] = 0xffffffff
        check(image, 0xffffffff, entries)
        entries[-1] = 0xffffffff
        check(image, 0xffffffff, entries)
    check(image, 0xffffffff, [0] * 15)
    check(image, 0, [0] * 15)
    rng = random.Random(0x90b0)
    for _ in range(4096):
        entries = [rng.getrandbits(32) for _ in range(15)]
        key = rng.choice(entries + [rng.getrandbits(32)])
        check(image, key, entries)
    mutant = bytearray(image)
    mutant[0x90c8 - 0x8000 + 1] ^= 0x10
    try: check(mutant, 0, [0] * 15)
    except ValueError: pass
    else: raise ValueError('comparison mutation undetected')
    print('PASS: 15 positions, duplicate priority, miss and 4096 seeded synthetic table scans; match continuation not executed')


if __name__ == '__main__': main()
