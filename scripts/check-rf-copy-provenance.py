#!/usr/bin/env python3
"""Connect the RF call site to the public V1.31 loader and copy-body evidence."""
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bulk = runpy.run_path(str(ROOT / 'scripts/check-rf-3534-bulk.py'))
source_dir = ROOT / 'analysis/resident-copy-reference-2026-10-21/source'
source = runpy.run_path(str(source_dir / 'inspect-source.py'))
sparse = runpy.run_path(str(ROOT / 'analysis/v131-startup-source/check.py'))


def check(image, header, raw_hex):
    bulk['verify'](image, header)
    if hashlib.sha256(raw_hex).hexdigest() != sparse['HEX_SHA']:
        raise ValueError('HEX identity mismatch')
    mem = sparse['parse'](raw_hex)
    if len(mem) != 191244 or any(mem.get(0x40000 + i) != b for i, b in enumerate(image)):
        raise ValueError('carrier does not match sparse HEX')
    return check_raw(image, mem)


def check_raw(image, mem):
    # Raw operand gates run independently of full-file identity, enabling mutation tests.
    bulk['verify_instructions'](image)
    mapping = source['gate'](image)
    target = source['pair'](image, 0x64e20, 0x64e24, 1, True, True)
    if target != mapping['slot'] or mapping['mapped_helper_source'] != 0x405a2:
        raise ValueError('call/loader mapping mismatch')
    start, end = 0x405a2, 0x405dc
    if any(mem.get(p) != image[p - 0x40000] for p in range(start, end)):
        raise ValueError('helper source absent or mismatched')
    if mapping['source'] + (target - mapping['destination']) != start:
        raise ValueError('mapping arithmetic mismatch')
    if target + end - start > mapping['destination'] + mapping['bytes']:
        raise ValueError('first copy does not cover helper')
    absent, _ = sparse['coverage'](mem, mem, mapping['source2'], mapping['source2'] + mapping['bytes2'])
    if absent != list(range(0x6eb2c, 0x6eb30)):
        raise ValueError('second-copy sparse completeness changed')
    return {'call_target': hex(target), 'helper_source': '[0x405a2,0x405dc)',
            'helper_ram': '[0x20000332,0x2000036c)', 'second_copy_missing': '[0x6eb2c,0x6eb30)',
            'conditional_mapping_only': True, 'hardware_execution': False}


if __name__ == '__main__':
    image = bulk['base']['base']['IMAGE'].read_bytes()
    header = bulk['base']['base']['HEADER'].read_bytes()
    raw_hex = (ROOT / 'analysis/v131-startup-source/wchble_rom.hex').read_bytes()
    # Also replay complete helper CFG, fixed rows and 23 operand mutations.
    source['run'](bulk['base']['base']['IMAGE'], source_dir, ROOT)
    print(json.dumps(check(image, header, raw_hex), indent=2))
