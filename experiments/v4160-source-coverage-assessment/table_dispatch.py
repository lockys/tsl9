#!/usr/bin/env python3
"""Bounded decode of the original five-way table dispatch (not a CPU emulator)."""
import hashlib
import struct
from pathlib import Path

IMAGE = Path(__file__).resolve().parents[2] / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
START = 0x14512
EXPECTED = bytes.fromhex('834704001147e360f7b817670000130787188a07ba979c43ba978287')
TARGETS = (0x1452e, 0x1453e, 0x1454a, 0x1473e, 0x14748)


def dispatch(code, table, index):
    if code != EXPECTED or len(table) != 20 or not 0 <= index <= 255:
        raise ValueError('instruction, table length or index invalid')
    branch, auipc, addi = struct.unpack_from('<III', code, 6)
    # The exact compressed and load sequence is pinned above; decode the PC-relative fields.
    imm = ((branch >> 31 & 1) << 12) | ((branch >> 7 & 1) << 11) | ((branch >> 25 & 63) << 5) | ((branch >> 8 & 15) << 1)
    imm -= (imm & 0x1000) * 2
    if index > 4:
        return 0x14518 + imm
    signed12 = addi >> 20
    signed12 -= (signed12 & 0x800) * 2
    base = (0x1451c + (auipc & 0xfffff000) + signed12) & 0xffffffff
    offset = struct.unpack_from('<i', table, index * 4)[0]
    return (base + offset) & 0xffffffff


def main():
    image = IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('APP identity mismatch')
    code = image[START-0x8000:START-0x8000+len(EXPECTED)]
    table = image[0x1a6a4-0x8000:0x1a6b8-0x8000]
    for index in range(256):
        expected = TARGETS[index] if index < 5 else 0x14098
        if dispatch(code,table,index) != expected:
            raise ValueError(f'dispatch mismatch for {index}')
    for i in range(len(code)):
        mutant=bytearray(code); mutant[i]^=1
        try: dispatch(mutant,table,0)
        except ValueError: continue
        raise ValueError(f'instruction mutation {i} accepted')
    for index in range(5):
        mutant=bytearray(table); mutant[index*4]^=1
        if dispatch(code,mutant,index)==TARGETS[index]:
            raise ValueError(f'table mutation {index} not observed')
    print(f'PASS: 256 byte indices, {len(code)} instruction mutations and five table-entry mutations')
    print('Indices 0..4 select five relative targets; indices 5..255 branch to 0x14098.')
    print('Static bounded projection assumes successful reads and no asynchronous changes; no reachability or hardware claim.')

if __name__ == '__main__': main()
