#!/usr/bin/env python3
"""Syntactic bounded APP scan; unknown is not evidence of absence."""
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
forward = runpy.run_path(str(ROOT / 'scripts/scan-rf-pointer-forward.py'))['scan']

def verify(data):
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('APP identity mismatch')
    return forward(data, BASE, [(BASE, BASE + len(data))], 32)

if __name__ == '__main__':
    print(json.dumps({'sha256': SHA, 'range': [hex(BASE), hex(BASE + 76800)],
                      'budget': 32, 'exhaustive': False, **verify(APP.read_bytes())}, indent=2))
