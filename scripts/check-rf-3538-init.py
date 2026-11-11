#!/usr/bin/env python3
"""Bounded V1.31 HEX startup and RF_Config coverage, not target execution."""
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEX = ROOT / 'analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.hex'
SHA = '11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5'
BASE = 0x40000
TARGET = (0x20003538, 0x2000353c)
# Complete argument setup and both AUIPC/JALR pairs; raw bytes, not inferred ROM.
RF = bytes.fromhex('373900201306000281451305095497b0f91fe780007c13060002a6851305095497b0f91fe7804074')

def overlap(a, b):
    return max(a[0], b[0]) < min(a[1], b[1])

def inspect(mem):
    def span(start, end):
        try:
            return bytes(mem[p] for p in range(start, end))
        except KeyError as exc:
            raise ValueError('uncaptured byte') from exc
    carrier = span(BASE, 0x6ea66)
    gate = runpy.run_path(str(ROOT / 'analysis/resident-entry-reference-2026-10-21/source/inspect-source.py'))['gate']
    v = gate(carrier)
    if span(0x64bce, 0x64bf6) != RF:
        raise ValueError('RF_Config argument/call window mismatch')
    copies = [(d, end + 4) for _, d, end in (v['first'], v['second'])]
    zero = (v['zero'][0], v['zero'][1] + 4)
    rf = (0x20003540, 0x20003540 + 32)
    requested = range(v['second'][0], v['second'][0] + copies[1][1] - copies[1][0])
    missing = [p for p in requested if p not in mem]
    if missing != list(range(0x6eb2c, 0x6eb30)):
        raise ValueError('unexpected second-copy source coverage')
    return {'copy_ranges': copies, 'zero_range': zero, 'rf_range': rf,
            'copy_overlaps': [overlap(x, TARGET) for x in copies],
            'zero_overlaps': overlap(zero, TARGET), 'rf_overlaps': overlap(rf, TARGET),
            'missing_source': [0x6eb2c, 0x6eb30], 'target_executed': False}

def verify(raw):
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('HEX identity mismatch')
    parser = runpy.run_path(str(ROOT / 'analysis/v131-startup-source/check.py'))['parse']
    return inspect(parser(raw))

if __name__ == '__main__':
    print(json.dumps(verify(HEX.read_bytes()), indent=2))
