#!/usr/bin/env python3
"""Emit address-indexed selected bytes, never a flashable image."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser()
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
support = runpy.run_path(str(ROOT / 'scripts/source-build-support.py'))
support['metadata']()
reader = runpy.run_path(str(support['PARSER']))['ELF']
mapping = json.loads((ROOT / 'src/compact-layout.json').read_text(encoding='utf-8'))
expected = [(0x8000, 0x14056), (0x14c8a, 0x1a69c), (0x1a6a0, 0x1ac00)]
out.mkdir(parents=True)
build = out / 'build'
proc = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build-compact-source-layout.py'),
                       '--tool-dir', str(a.tool_dir), '--out', str(build)], capture_output=True, text=True)
if proc.returncode:
    raise ValueError('Source build failed: ' + proc.stderr[:1000])
facts = json.loads(proc.stdout)
if not facts['passed'] or facts['candidate_bytes_read'] or facts['historical_build_object_read'] or facts['flashable']:
    raise ValueError('Unexpected source build result')
outputs = []
for mode in ('c', 'cpp'):
    elf = reader(build / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf'))
    sections = sorted((s for s in elf.sections if s['flags'] & 2 and s['size']), key=lambda s: s['address'])
    if len(sections) != 6266:
        raise ValueError('Unexpected source section count')
    payload = bytearray()
    spans = []
    for s in sections:
        start, end = s['address'], s['address'] + s['size']
        if s['type'] != 1 or not any(lo <= start < end <= hi for lo, hi in expected):
            raise ValueError('Source section lies outside permitted spans')
        if spans and spans[-1]['end'] == start:
            spans[-1]['end'] = end
            spans[-1]['length'] += s['size']
        else:
            spans.append({'start': start, 'end': end, 'file_offset': len(payload), 'length': s['size']})
        payload.extend(elf.data(s))
    if ([(x['start'], x['end']) for x in spans] != expected or len(payload) != 73672 or
        hashlib.sha256(payload).hexdigest() != mapping['selected_linked_sha256']):
        raise ValueError('Selected source spans or digest differ')
    binary = out / ('NOT-FLASHABLE-selected-spans-' + mode + '.bin')
    with binary.open('xb') as stream:
        stream.write(payload)
    if binary.read_bytes() != payload:
        raise ValueError('Binary readback differs')
    outputs.append({'mode': mode, 'file': binary.name, 'bytes': len(payload),
                    'sha256': hashlib.sha256(payload).hexdigest(), 'spans': spans})
if outputs[0]['sha256'] != outputs[1]['sha256'] or outputs[0]['spans'] != outputs[1]['spans']:
    raise ValueError('C and C++ span outputs differ')
record = {'schema': 'tsl9-selected-source-spans-v1', 'outputs': outputs, 'candidate_bytes_read': 0,
          'excluded_bytes': 3128, 'excluded_read': False, 'complete_firmware': False, 'flashable': False}
with (out / 'NOT-FLASHABLE-spans.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'passed': True, 'bytes_per_mode': 73672, 'spans': len(expected), 'excluded_bytes': 3128,
                  'candidate_bytes_read': 0, 'excluded_read': False, 'complete_firmware': False, 'flashable': False}))
