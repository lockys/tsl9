#!/usr/bin/env python3
"""Fail-closed audit of the V1.31 sparse diagnostic ELF, not a flash gate."""
import argparse
import hashlib
import json
import runpy
from pathlib import Path

from sparse_resident_evidence import validate

ROOT = Path(__file__).resolve().parents[1]
APP_SHA = '28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89'
# Conservative superset: every recorded segment, plus both copy sources and helper seed.
COPY = [(0x40280, 0x402b0), (0x402b0, 0x430e4), (0x6eaa4, 0x6eb30)]
RESIDENT = (0x40000, 0x6eb30)


def ranges(points):
    points = sorted(points)
    result = []
    for p in points:
        if result and result[-1][1] == p:
            result[-1][1] += 1
        else:
            result.append([p, p + 1])
    return [[hex(a), hex(b)] for a, b in result]


def audit(source, actual, copy=COPY):
    required = set(source)
    for start, end in copy:
        required.update(range(start, end))
    missing_source = required - source.keys()
    missing_elf = required - actual.keys()
    mismatch = {p for p in required & source.keys() & actual.keys() if source[p] != actual[p]}
    unexplained = actual.keys() - source.keys()
    return {'passed': not (missing_source or missing_elf or mismatch or unexplained),
            'missing_source': ranges(missing_source), 'missing_elf': ranges(missing_elf),
            'mismatch': ranges(mismatch), 'unproven_elf_bytes': ranges(unexplained)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--reference-dir', type=Path, required=True)
    a = p.parse_args()
    ref = a.reference_dir.resolve()
    segments = validate(ROOT, ref)
    source = {s['start'] + i: b for s in segments for i, b in enumerate((ref / s['path']).read_bytes())}
    reader = runpy.run_path(str(ROOT / 'src/native/tx_candidate/postpass/elf32.py'))['ELF']
    e = reader(a.elf)
    if e.kind != 2:
        raise ValueError('expected linked executable ELF')
    actual, app = {}, {}
    for sec in e.sections:
        if not sec['flags'] & 2 or not sec['size']:
            continue
        start, end = sec['address'], sec['address'] + sec['size']
        if end > 0x100000000:
            raise ValueError('section address overflow')
        for lo, hi, target in [(0x8000, 0x1ac00, app), (*RESIDENT, actual)]:
            if start < hi and end > lo:
                if start < lo or end > hi or sec['type'] != 1:
                    raise ValueError('invalid allocated section crossing audited boundary or not PROGBITS')
                for i, byte in enumerate(e.data(sec)):
                    addr = start + i
                    if addr in target:
                        raise ValueError('overlapping allocated sections')
                    target[addr] = byte
    if len(app) != 0x1ac00 - 0x8000 or hashlib.sha256(bytes(app[p] for p in range(0x8000, 0x1ac00))).hexdigest() != APP_SHA:
        raise ValueError('APP identity mismatch')
    entry = [s for s in e.symbols if s['name'] == 'tsl9_boot_resident_40000' and s['index'] not in (0, 0xfff1)]
    if len(entry) != 1 or entry[0]['value'] != 0x40000 or entry[0]['index'] >= len(e.sections) or e.sections[entry[0]['index']]['address'] != 0x40000:
        raise ValueError('resident entry is not uniquely section-backed')
    result = audit(source, actual)
    result.update({'reference_hex_sha256': '11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5',
                   'reference_segments': [{'path': s['path'], 'start': hex(s['start']), 'end_exclusive': hex(s['end_exclusive']), 'sha256': s['sha256']} for s in segments],
                   'elf_sha256': hashlib.sha256(e.raw).hexdigest(), 'scope': 'V1.31 reference diagnostic only; all recorded bytes conservatively required',
                   'installed_rom_proved': False, 'hardware_validated': False, 'flashable': False})
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, IndexError) as exc:
        print(json.dumps({'passed': False, 'error': str(exc), 'flashable': False}))
        raise SystemExit(1)
