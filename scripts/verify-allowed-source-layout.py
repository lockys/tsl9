#!/usr/bin/env python3
"""Compare selected source layout to the candidate without reading excluded ranges."""
import argparse
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser()
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
if a.candidate.stat().st_size != 76800:
    raise ValueError('Unexpected candidate size')
module = runpy.run_path(str(ROOT / 'scripts/source-build-support.py'))
module['metadata']()
reader = runpy.run_path(str(module['PARSER']))['ELF']
out.mkdir(parents=True)
base = out / 'build'
proc = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build-compact-source-layout.py'),
                       '--tool-dir', str(a.tool_dir), '--out', str(base)], capture_output=True, text=True)
if proc.returncode:
    raise ValueError('Source layout failed: ' + proc.stderr[:1000])
facts = json.loads(proc.stdout)
if not facts['passed'] or facts['candidate_bytes_read'] or facts['flashable']:
    raise ValueError('Unexpected baseline')
excluded = ((0x14056, 0x14c8a), (0x1a69c, 0x1a6a0))
results = []
for mode in ('c', 'cpp'):
    elf = reader(base / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf'))
    sections = sorted((s for s in elf.sections if s['flags'] & 2 and s['size']), key=lambda s: s['address'])
    if len(sections) != 6266 or sum(s['size'] for s in sections) != 73672:
        raise ValueError('Unexpected selected coverage')
    checked = 0
    with a.candidate.open('rb') as stream:
        for section in sections:
            start, end = section['address'], section['address'] + section['size']
            if (section['type'] != 1 or not 0x8000 <= start < end <= 0x1ac00 or
                any(not (end <= lo or start >= hi) for lo, hi in excluded)):
                raise ValueError('Rejected excluded or invalid section')
            stream.seek(start - 0x8000)
            expected = stream.read(section['size'])
            if len(expected) != section['size'] or expected != elf.data(section):
                raise ValueError('Candidate mismatch at ' + hex(start))
            checked += len(expected)
    results.append({'mode': mode, 'checked_candidate_bytes': checked, 'sections': len(sections)})
print(json.dumps({'passed': True, 'results': results, 'excluded_bytes': sum(hi - lo for lo, hi in excluded),
                  'excluded_read': False, 'complete_firmware': False, 'flashable': False}))
