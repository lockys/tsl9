#!/usr/bin/env python3
"""Offline bounded encoding scan for stores overlapping the RF pointer word."""
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
forward = runpy.run_path(str(ROOT / 'scripts/scan-rf-pointer-forward.py'))
direct = forward['DIRECT']
alias = runpy.run_path(str(ROOT / 'scripts/check-rf-3538-api-alias.py'))
TARGET = 0x20003534
RANGES = [(0x645dc, 0x646a8), (0x64bae, 0x64cec), (0x64cec, 0x64f04)]
# run_path functions use their own globals, not the returned dictionary.
direct['scan'].__globals__['TARGET'] = TARGET
forward['scan'].__globals__['TARGET'] = TARGET


def scan(data):
    return {'adjacent': direct['scan'](data),
            'forward': forward['scan'](data, direct['BASE'], RANGES, 32)}


def verify(data, header):
    alias['verify'](data, header)
    return scan(data)


if __name__ == '__main__':
    print(json.dumps({'sha256': direct['SHA'], 'target': hex(TARGET),
                      'ranges_end_exclusive': [[hex(a), hex(b)] for a, b in RANGES],
                      'result': verify(direct['IMAGE'].read_bytes(), alias['HEADER'].read_bytes())}, indent=2))
