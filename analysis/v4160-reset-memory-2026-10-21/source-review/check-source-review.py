#!/usr/bin/env python3
"""Read-only raw inspection of the 17-instruction ID2966 memory slice."""
import argparse
import hashlib
import json
from pathlib import Path

IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RESET_SHA = '9507502c874a03e2c64a28b186a1f56aba9e85c9989dbf0cc053dabc4045bb4d'
INITIALIZER_SHA = 'd2f2eac71b3c4f04686d1179aebb430b70088394c46552914bec908c98558e0c'
BASE, START, END = 0x8000, 0x186ba, 0x186f8

def sha(data):
    return hashlib.sha256(data).hexdigest()

def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

def decode(raw, pc):
    x = int.from_bytes(raw, 'little')
    if len(raw) == 2 and x & 3 == 1 and x >> 13 == 0:
        rd = (x >> 7) & 31
        imm = sx(((x >> 12) & 1) * 32 + ((x >> 2) & 31), 6)
        return ['addi', rd, rd, imm]
    if len(raw) == 4:
        op, rd, f3, rs1, rs2 = x & 127, (x >> 7) & 31, (x >> 12) & 7, (x >> 15) & 31, (x >> 20) & 31
        if op == 0x17:
            return ['auipc', rd, x & 0xfffff000]
        if op == 0x13 and f3 == 0:
            return ['addi', rd, rs1, sx(x >> 20, 12)]
        if op == 0x03 and f3 == 2:
            return ['lw', rd, rs1, sx(x >> 20, 12)]
        if op == 0x23 and f3 == 2:
            return ['sw', rs2, rs1, sx(((x >> 25) << 5) | ((x >> 7) & 31), 12)]
        if op == 0x63 and f3 in (6, 7):
            imm = ((x >> 31) & 1) * 4096 + ((x >> 7) & 1) * 2048 + ((x >> 25) & 63) * 32 + ((x >> 8) & 15) * 2
            return ['bltu' if f3 == 6 else 'bgeu', rs1, rs2, (pc + sx(imm, 13)) & 0xffffffff]
    raise ValueError('Unexpected memory-slice encoding at ' + hex(pc))

def inspect(data):
    rows = []
    pc = START
    while pc < END:
        off = pc - BASE
        size = 4 if data[off] & 3 == 3 else 2
        if pc + size > END:
            raise ValueError('Instruction crosses selected extent')
        raw = data[off:off + size]
        rows.append({'pc': pc, 'bytes': raw.hex(), 'size': size, 'decoded': decode(raw, pc)})
        pc += size
    return rows

def validate(data, retained, identity=True):
    if identity and (len(data) != 76800 or sha(data) != IMAGE_SHA):
        raise ValueError('Exact original image identity mismatch')
    rows = inspect(data)
    if rows != retained['instructions']:
        raise ValueError('Raw instruction/operand mismatch')
    return rows

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--review-root', type=Path, default=Path(__file__).resolve().parent)
    a = p.parse_args()
    data = a.firmware.read_bytes()
    retained = json.loads((a.review_root / 'retained-source.json').read_text(encoding='utf-8'))
    if retained['original_image_sha256'] != IMAGE_SHA or retained['start'] != START or retained['end_exclusive'] != END:
        raise ValueError('Review metadata identity mismatch')
    rows = validate(data, retained)
    if sha(data[0x186aa-BASE:0x18734-BASE]) != RESET_SHA:
        raise ValueError('Full reset context identity mismatch')
    if sha(data[0x1ab60-BASE:0x1abe0-BASE]) != INITIALIZER_SHA:
        raise ValueError('Initializer identity mismatch')
    rejected = 0
    for row in rows:
        mutant = bytearray(data)
        mutant[row['pc'] - BASE] ^= 0x10
        try:
            validate(mutant, retained, identity=False)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('Raw mutation was not rejected')
    print(json.dumps({'passed': True, 'source_bytes': END-START, 'instructions': len(rows),
                      'raw_mutations_rejected': rejected, 'original_sha256': IMAGE_SHA,
                      'reset_context_bytes': 138, 'initializer_bytes': 128,
                      'target_execution': False, 'ISA_emulation': False,
                      'network': False, 'hardware': False, 'OTA_ready': False}, sort_keys=True))

if __name__ == '__main__':
    main()
