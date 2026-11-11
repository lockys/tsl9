#!/usr/bin/env python3
"""Offline evidence check; no image generation, hole filling, or device access."""
import hashlib
import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HEX_SHA = '11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5'
MAIN_SHA = '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
TAIL_SHA = '7416a8d7c1d595a759e14b05918b732a9168c6003af658359d8c3f452840b450'

def digest(b):
    return hashlib.sha256(b).hexdigest()

def parse(raw):
    mem = {}; base = 0; eof = False
    lines = raw.decode('ascii').split('\n')
    if lines[-1] == '':
        lines.pop()
    for line in lines:
        if line.endswith('\r'):
            line = line[:-1]
        if eof or not line.startswith(':'):
            raise ValueError('record after EOF or missing colon')
        if any(c not in '0123456789abcdefABCDEF' for c in line[1:]):
            raise ValueError('invalid HEX')
        try:
            r = bytes.fromhex(line[1:])
        except ValueError as e:
            raise ValueError('invalid HEX') from e
        if len(r) < 5 or len(r) != r[0] + 5 or sum(r) % 256:
            raise ValueError('record length/checksum')
        n, addr, typ, data = r[0], int.from_bytes(r[1:3], 'big'), r[3], r[4:-1]
        if typ == 0:
            if addr + n > 0x10000 or base + addr + n > 0x100000000:
                raise ValueError('data address overflow')
            for i, value in enumerate(data):
                p = base + addr + i
                if p in mem: raise ValueError('overlap')
                mem[p] = value
        elif typ in (2, 4) and n == 2 and addr == 0:
            base = int.from_bytes(data, 'big') << (4 if typ == 2 else 16)
        elif typ == 1 and n == 0 and addr == 0:
            eof = True
        elif typ in (3, 5) and n == 4 and addr == 0:
            pass
        else:
            raise ValueError('unsupported or malformed record')
    if not eof: raise ValueError('missing EOF')
    return mem

def coverage(source, extracted, start, end):
    """Return distinct source-absent and extraction-omitted addresses."""
    return ([p for p in range(start, end) if p not in source],
            [p for p in range(start, end) if p in source and p not in extracted])

def main():
    raw = (HERE / 'wchble_rom.hex').read_bytes()
    if digest(raw) != HEX_SHA: raise ValueError('official HEX hash mismatch')
    mem = parse(raw)
    def span(a, b):
        return bytes(mem[p] for p in range(a, b))
    main = span(0x40000, 0x6ea66)
    tail = span(0x6eaa4, 0x6eb2c)
    if len(mem) != 191244 or digest(main) != MAIN_SHA or digest(tail) != TAIL_SHA:
        raise ValueError('source extent or segment hash mismatch')
    # Independently decode the actual entry, arguments, copy helper and inclusive branch.
    gate = runpy.run_path(str(ROOT / 'analysis/resident-entry-reference-2026-10-21/source/inspect-source.py'))['gate']
    gate(main)
    start, end = 0x6eaa4, 0x6eb30
    absent, omitted = coverage(mem, {p: mem[p] for p in range(0x40000, 0x6ea66)}, start, end)
    if absent != list(range(0x6eb2c, end)) or omitted != list(range(start, 0x6eb2c)):
        raise ValueError('startup coverage changed')
    print(json.dumps({'hex_sha256': HEX_SHA, 'main_sha256': MAIN_SHA, 'tail_sha256': TAIL_SHA,
                      'recorded_bytes': len(mem), 'requested': '[0x6eaa4,0x6eb30)',
                      'main_only_extraction_omits': '[0x6eaa4,0x6eb2c)',
                      'absent_from_hex': '[0x6eb2c,0x6eb30)',
                      'source_word_reads_before_missing': 34, 'missing_destination': '0x20002ef8',
                      'target_executed': False, 'flashable': False}, indent=2))

if __name__ == '__main__': main()
