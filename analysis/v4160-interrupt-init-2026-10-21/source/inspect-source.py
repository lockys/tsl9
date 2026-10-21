#!/usr/bin/env python3
"""Read-only source-specific RV32I/C decoding; never executes target code."""
import argparse
import hashlib
import json
from pathlib import Path

IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
RANGES = {'entry_9a42': (0x9a42, 0x9ad2), 'rcc_19124': (0x19124, 0x19142),
          'rcc_19142': (0x19142, 0x19160), 'rcc_19160': (0x19160, 0x1917e),
          'rcc_1917e': (0x1917e, 0x1919c)}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value

def decode(raw, pc):
    """Decode only actually retained opcodes; names/operands from raw bits."""
    x = int.from_bytes(raw, 'little')
    if len(raw) == 2:
        q, f = x & 3, x >> 13
        rd, rs2 = (x >> 7) & 31, (x >> 2) & 31
        if q == 1 and f == 0:
            return ['addi', rd, rd, sx(((x >> 12) & 1) * 32 + rs2, 6)]
        if q == 1 and f == 2:
            return ['addi', rd, 0, sx(((x >> 12) & 1) * 32 + rs2, 6)]
        if q == 1 and f == 3 and rd not in (0, 2):
            return ['lui', rd, (sx(((x >> 12) & 1) * 32 + rs2, 6) << 12) & 0xffffffff]
        if q == 2 and f == 6:
            imm = ((x >> 9) & 15) * 4 + ((x >> 7) & 3) * 64
            return ['sw', rs2, 2, imm]
        if q == 2 and f == 2:
            imm = ((x >> 12) & 1) * 32 + ((x >> 4) & 7) * 4 + ((x >> 2) & 3) * 64
            return ['lw', rd, 2, imm]
        if q == 1 and f == 6:
            imm = ((x >> 12) & 1) * 256 + ((x >> 10) & 3) * 8 + ((x >> 5) & 3) * 64 + ((x >> 3) & 3) * 2 + ((x >> 2) & 1) * 32
            return ['beq', 8 + ((x >> 7) & 7), 0, (pc + sx(imm, 9)) & 0xffffffff]
        if q == 0 and f in (2, 6):
            imm = ((x >> 10) & 7) * 8 + ((x >> 6) & 1) * 4 + ((x >> 5) & 1) * 64
            return ['lw' if f == 2 else 'sw', 8 + ((x >> 2) & 7), 8 + ((x >> 7) & 7), imm]
        if q == 1 and f == 4 and ((x >> 10) & 7) == 3:
            op = {2: 'or', 3: 'and'}.get((x >> 5) & 3)
            if op:
                return [op, 8 + ((x >> 7) & 7), 8 + ((x >> 7) & 7), 8 + ((x >> 2) & 7)]
        if x == 0x8082:
            return ['jalr', 0, 1, 0]
    else:
        op, rd, f3, rs1, rs2 = x & 127, (x >> 7) & 31, (x >> 12) & 7, (x >> 15) & 31, (x >> 20) & 31
        if op == 0x37:
            return ['lui', rd, x & 0xfffff000]
        if op == 0x13 and f3 in (0, 4):
            return ['addi' if f3 == 0 else 'xori', rd, rs1, sx(x >> 20, 12)]
        if op == 0x23 and f3 in (0, 2):
            return ['sb' if f3 == 0 else 'sw', rs2, rs1, sx(((x >> 25) << 5) + ((x >> 7) & 31), 12)]
        if op == 0x73 and f3 in (2, 3):
            return ['csrrs' if f3 == 2 else 'csrrc', rd, x >> 20, rs1]
        if op == 0x6f:
            imm = ((x >> 31) & 1) * 0x100000 + ((x >> 21) & 1023) * 2 + ((x >> 20) & 1) * 2048 + ((x >> 12) & 255) * 4096
            return ['jal', rd, (pc + sx(imm, 21)) & 0xffffffff]
    raise ValueError('Unsupported instruction at ' + hex(pc) + ': ' + raw.hex())

def capture(data):
    groups = {}
    for key, (start, end) in RANGES.items():
        pc, rows = start, []
        while pc < end:
            off = pc - BASE
            size = 4 if data[off] & 3 == 3 else 2
            if pc + size > end:
                raise ValueError('Instruction crosses fixed extent')
            raw = data[off:off + size]
            rows.append({'addr': pc, 'size': size, 'bytes': raw.hex(), 'decoded': decode(raw, pc)})
            pc += size
        groups[key] = rows
    return groups

def validate(data, reference, check_identity=True):
    if reference.get('schema') != 'TSL9-raw-source-instructions-v1' or reference.get('firmware_sha256') != IMAGE_SHA or reference.get('base') != BASE:
        raise ValueError('Retained source metadata mismatch')
    if check_identity and (len(data) != 76800 or sha(data) != IMAGE_SHA):
        raise ValueError('Original image identity mismatch')
    actual = capture(data)
    if actual != reference['groups']:
        raise ValueError('Raw decoded source mismatch')
    return actual

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--check', action='store_true', required=True)
    a = p.parse_args()
    data = a.firmware.read_bytes()
    reference = json.loads((a.source_root / 'retained-instructions.json').read_text(encoding='utf-8'))
    groups = validate(data, reference)
    source_map = json.loads((a.source_root / 'source-map.json').read_text(encoding='utf-8'))
    if source_map['original'] != {'sha256': IMAGE_SHA, 'bytes': 76800, 'base': BASE}:
        raise ValueError('Source map original identity mismatch')
    mapped = []
    calls = []
    for key, rows in groups.items():
        raw = b''.join(bytes.fromhex(row['bytes']) for row in rows)
        mapped.append({'id': key, 'start': rows[0]['addr'], 'end_exclusive': rows[-1]['addr'] + rows[-1]['size'],
                       'bytes': len(raw), 'instructions': len(rows), 'sha256': sha(raw)})
        calls.extend({'pc': row['addr'], 'target': row['decoded'][2], 'return_pc': row['addr'] + row['size']}
                     for row in rows if row['decoded'][0] == 'jal')
    if mapped != source_map['ranges'] or calls != source_map['direct_calls']:
        raise ValueError('Source map extent/call mismatch')
    rejected = 0
    for rows in groups.values():
        for row in rows:
            mutated = bytearray(data)
            mutated[row['addr'] - BASE] ^= 0x10
            try:
                validate(mutated, reference, check_identity=False)
            except ValueError:
                rejected += 1
            else:
                raise ValueError('Unrejected raw instruction mutation')
    print(json.dumps({'passed': True, 'firmware_sha256': sha(data), 'ranges': len(groups),
        'source_bytes': sum(b-a for a,b in RANGES.values()), 'instructions': sum(map(len, groups.values())),
        'raw_negative_controls_rejected': rejected, 'target_executed': False, 'ISA_emulation': False,
        'network': False, 'hardware': False, 'OTA_ready': False}, sort_keys=True))

if __name__ == '__main__':
    main()
