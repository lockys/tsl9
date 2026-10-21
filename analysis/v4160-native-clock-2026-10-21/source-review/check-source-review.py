#!/usr/bin/env python3
"""Replay immutable clock source proof. No decoding duplication or target execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PROOF_SHA = 'ebf0521f52c5142d1dc7969aaca17bb1c7567065165eba4c88fd4523e30b6a51'
FIRMWARE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--firmware', type=Path, required=True)
    a = p.parse_args()
    project = a.project_root.resolve(strict=True)
    roots = [project / prefix / 'tsl9-v4160-system-clock-query-2026-10-21' / 'source'
             for prefix in ('apk-analysis', 'analysis')]
    found = [r for r in roots if (r / 'final-audit.json').is_file()]
    if len(found) != 1:
        raise ValueError('Expected exactly one known original proof layout')
    source = found[0].resolve(strict=True)
    source.relative_to(project)
    seal = source / 'final-audit.json'
    if sha(seal) != PROOF_SHA:
        raise ValueError('Immutable source seal mismatch')
    old = json.loads(seal.read_text(encoding='utf-8'))
    for member in old['members']:
        target = (source / member['path']).resolve(strict=True)
        target.relative_to(source)
        if target.stat().st_size != member['bytes'] or sha(target) != member['sha256']:
            raise ValueError('Immutable member mismatch: ' + member['path'])
    firmware = a.firmware.resolve(strict=True)
    if firmware.stat().st_size != 76800 or sha(firmware) != FIRMWARE_SHA:
        raise ValueError('Expected exact ID2966 V4.1.60 original image')
    command = [sys.executable, '-X', 'utf8', '-B', str(source / 'inspect-source.py'),
               '--check', '--firmware', str(firmware), '--source-root', str(source)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=True)
    replay = json.loads(result.stdout)
    if not replay.get('passed') or replay.get('target_bytes') != 214 or replay.get('target_instructions') != 69 or replay.get('raw_operand_mutation_rejections') != 50:
        raise ValueError('Unexpected source proof replay result')
    print(json.dumps({'passed': True, 'immutable_proof_sha256': PROOF_SHA,
                      'original_sha256': FIRMWARE_SHA, 'source_replay': replay,
                      'ABI_proved': False, 'hardware': False, 'OTA_ready': False}, sort_keys=True))

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print('Source review failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
