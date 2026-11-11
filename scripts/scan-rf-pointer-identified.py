#!/usr/bin/env python3
"""Scan only the two existing RF disassembly windows, not the entire carrier."""
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
forward = runpy.run_path(str(ROOT / 'scripts/scan-rf-pointer-forward.py'))
direct = forward['DIRECT']
# Evidence: analysis/rf-status-provenance-2026-10-24.md, carrier windows.
RANGES = [(0x645dc, 0x646a8), (0x64bae, 0x64cec)]
BUDGET = 32


def verify(data):
    direct['verify'](data)
    return forward['scan'](data, direct['BASE'], RANGES, BUDGET)


if __name__ == '__main__':
    print(json.dumps({'sha256': direct['SHA'], 'base': hex(direct['BASE']),
                      'ranges_end_exclusive': [[hex(a), hex(b)] for a, b in RANGES],
                      'range_evidence': 'analysis/rf-status-provenance-2026-10-24.md',
                      'budget': BUDGET, 'exhaustive': False, 'hardware_executed': False,
                      **verify(direct['IMAGE'].read_bytes())}, indent=2))
