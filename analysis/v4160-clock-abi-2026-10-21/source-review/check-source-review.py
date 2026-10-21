#!/usr/bin/env python3
"""Source-bound destination-field inspection; no instruction execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SEAL = 'ebf0521f52c5142d1dc7969aaca17bb1c7567065165eba4c88fd4523e30b6a51'
ORIGINAL = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def destination(raw):
    """Architectural integer destination for only the sealed source opcodes."""
    x = int.from_bytes(bytes.fromhex(raw), 'little')
    if len(raw) == 8:
        op = x & 127
        if op in (0x03, 0x13, 0x33, 0x37):
            rd = (x >> 7) & 31
            return rd if rd else None
        if op in (0x23, 0x63):
            return None
    elif len(raw) == 4:
        q, f = x & 3, x >> 13
        if q == 0 and f == 2:
            return 8 + ((x >> 2) & 7)
        if q == 1 and f in (0, 2, 3):
            rd = (x >> 7) & 31
            return rd if rd else None
        if q == 1 and f == 4:
            return 8 + ((x >> 7) & 7)
        if q == 1 and f in (5, 6, 7):
            return None
        if q == 2 and f == 4 and (x >> 12) & 1 and (x >> 2) & 31:
            rd = (x >> 7) & 31
            return rd if rd else None
        if x == 0x8082:
            return None
    raise ValueError('Unrecognized sealed-source destination encoding: ' + raw)

def inspect(source):
    retained = json.loads((source / 'retained-source.json').read_text(encoding='utf-8'))
    facts = {}
    for name, allow in [('query18834', [12, 13, 14, 15]), ('derive1973c', [14, 15])]:
        rows = retained['groups'][name]
        writes = [{'pc': row['addr'], 'register': destination(row['bytes'])} for row in rows
                  if destination(row['bytes']) is not None]
        actual = sorted(set(row['register'] for row in writes))
        if actual != allow:
            raise ValueError('Original destination allowlist mismatch')
        facts[name] = {'instructions': len(rows), 'may_write_integer_registers': actual, 'writes': writes,
                       'ret_pc': 0x18876 if name == 'query18834' else 0x19762,
                       'return_encoding': '8280', 'return_target': 'live_RA & 0xfffffffe'}
    return facts

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--review-root', type=Path, default=Path(__file__).resolve().parent)
    a = p.parse_args()
    project = a.project_root.resolve(strict=True)
    choices = [project / x / 'tsl9-v4160-system-clock-query-2026-10-21' / 'source'
               for x in ('apk-analysis', 'analysis')]
    choices = [x for x in choices if (x / 'final-audit.json').is_file()]
    if len(choices) != 1:
        raise ValueError('Expected one known immutable source proof layout')
    source = choices[0].resolve(strict=True)
    source.relative_to(project)
    seal = source / 'final-audit.json'
    if sha(seal) != SEAL:
        raise ValueError('Immutable source seal mismatch')
    for f in json.loads(seal.read_text(encoding='utf-8'))['members']:
        item = (source / f['path']).resolve(strict=True)
        item.relative_to(source)
        if item.stat().st_size != f['bytes'] or sha(item) != f['sha256']:
            raise ValueError('Immutable source member mismatch')
    firmware = a.firmware.resolve(strict=True)
    if firmware.stat().st_size != 76800 or sha(firmware) != ORIGINAL:
        raise ValueError('Original image mismatch')
    run = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(source / 'inspect-source.py'),
                          '--check', '--firmware', str(firmware), '--source-root', str(source)],
                         capture_output=True, text=True, timeout=60, check=True)
    replay = json.loads(run.stdout)
    if not replay.get('passed') or replay.get('target_bytes') != 214 or replay.get('target_instructions') != 69 or replay.get('raw_operand_mutation_rejections') != 50:
        raise ValueError('Unexpected immutable proof replay')
    facts = inspect(source)
    expected = json.loads((a.review_root / 'source-facts.json').read_text(encoding='utf-8'))
    if expected['destination_fields'] != facts:
        raise ValueError('Review destination fields mismatch')
    print(json.dumps({'passed': True, 'immutable_seal_sha256': SEAL, 'source_replay': replay,
                      'destination_instruction_counts': {k: len(v['writes']) for k, v in facts.items()},
                      'integer_allowlists': {k: v['may_write_integer_registers'] for k, v in facts.items()},
                      'residue_formulas_static_review_only': True, 'native_binary_checked': False,
                      'target_execution': False, 'hardware': False, 'OTA_ready': False}, sort_keys=True))

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as e:
        print('Clock ABI source review failed: ' + str(e), file=sys.stderr)
        sys.exit(1)
