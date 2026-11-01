#!/usr/bin/env python3
"""Compare source-built spans to a reference without reading excluded ranges."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser()
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--reference', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
if a.reference.stat().st_size != 76800:
    raise ValueError('Unexpected reference size')
out.mkdir(parents=True)
build = out / 'spans'
proc = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build-source-spans.py'),
                       '--tool-dir', str(a.tool_dir), '--out', str(build)], capture_output=True, text=True)
if proc.returncode:
    raise ValueError('Source spans build failed: ' + proc.stderr[:1000])
facts = json.loads(proc.stdout)
if not facts['passed'] or facts['candidate_bytes_read'] or facts['excluded_read'] or facts['flashable']:
    raise ValueError('Unexpected source span build')
manifest = json.loads((build / 'NOT-FLASHABLE-spans.json').read_text(encoding='utf-8'))
expected = [(0x8000, 0x14056), (0x14c8a, 0x1a69c), (0x1a6a0, 0x1ac00)]
excluded = ((0x14056, 0x14c8a), (0x1a69c, 0x1a6a0))
comparisons = []
for output in manifest['outputs']:
    payload = (build / output['file']).read_bytes()
    spans = output['spans']
    if len(payload) != 73672 or [(s['start'], s['end']) for s in spans] != expected:
        raise ValueError('Unexpected source span layout')
    differences = []
    checked = 0
    with a.reference.open('rb') as stream:
        for span in spans:
            lo, hi = span['start'], span['end']
            if any(not (hi <= x or lo >= y) for x, y in excluded):
                raise ValueError('Reference read intersects excluded range')
            stream.seek(lo - 0x8000)
            reference = stream.read(hi - lo)
            selected = payload[span['file_offset']:span['file_offset'] + span['length']]
            if len(reference) != hi - lo or len(selected) != len(reference):
                raise ValueError('Short reference or source span')
            differences.extend(lo + i for i, (x, y) in enumerate(zip(reference, selected)) if x != y)
            checked += len(reference)
    intervals = []
    for address in differences:
        if intervals and intervals[-1][1] == address:
            intervals[-1][1] += 1
        else:
            intervals.append([address, address + 1])
    comparisons.append({'mode': output['mode'], 'reference_bytes_checked': checked,
                        'different_bytes': len(differences), 'different_ranges': intervals,
                        'all_differences_within_tx': all(0x8a56 <= x < 0x8b6e for x in differences)})
if len(comparisons) != 2 or comparisons[0]['different_ranges'] != comparisons[1]['different_ranges']:
    raise ValueError('C and C++ comparison results differ')
print(json.dumps({'passed': True, 'results': comparisons, 'excluded_read': False,
                  'complete_firmware': False, 'semantic_equivalence_proved': False, 'flashable': False}))
