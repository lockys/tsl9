#!/usr/bin/env python3
"""Check the sparse candidate's missing startup word against a conditional map."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--reference-dir', type=Path, required=True)
a = p.parse_args()
raw = (a.reference_dir / 'source-map.json').read_bytes()
if hashlib.sha256(raw).hexdigest() != '96ff0490ccd196ee97655a80ed44ea2b1ceee53b84ca3bad8f8f74525031c0ba':
    raise ValueError('Reference map changed')
manifest = json.loads(raw)
segments = manifest['segments']
if not manifest['passed'] or len(segments) != 17:
    raise ValueError('Unexpected reference segments')
for segment in segments:
    path = (a.reference_dir / segment['path']).resolve()
    if path.parent != a.reference_dir.resolve() or path.suffix != '.bin':
        raise ValueError('Invalid segment path')
    data = path.read_bytes()
    if (len(data) != segment['bytes'] or segment['end_exclusive'] - segment['start'] != len(data)
            or hashlib.sha256(data).hexdigest() != segment['sha256']):
        raise ValueError('Invalid segment')
if any(x['end_exclusive'] > y['start'] for x, y in zip(segments, segments[1:])):
    raise ValueError('Overlapping or unordered segments')

start, end = 0x6eaa4, 0x6eb30
missing = [x for x in range(start, end)
           if not any(s['start'] <= x < s['end_exclusive'] for s in segments)]
if missing != list(range(0x6eb2c, 0x6eb30)):
    raise ValueError('Startup source coverage changed')

def contained(lo, hi, base, size):
    return base <= lo < hi <= base + size

maximum = 480 * 1024
alias_base = 0x08000000
lo, hi = missing[0], missing[-1] + 1
if not contained(lo, hi, 0, maximum):
    raise ValueError('Missing word outside conditional family maximum')
if not contained(alias_base + lo, alias_base + hi, alias_base, maximum):
    raise ValueError('High alias arithmetic mismatch')
if not (hi <= 0x8000 or lo >= 0x1ac00):
    raise ValueError('Missing word overlaps candidate APP interval')
if contained(maximum - 2, maximum + 2, 0, maximum) or contained(2, 2, 0, maximum):
    raise ValueError('Boundary controls failed')
print(json.dumps({'passed': True, 'reference_segments': len(segments),
                  'startup_source_bytes': end - start, 'missing_bytes': len(missing),
                  'missing_inside_family_maximum_model': True,
                  'missing_disjoint_from_candidate_app_interval': True,
                  'boundary_controls': 2, 'boot_alias_proved': False,
                  'physical_mapping_or_readability_proved': False,
                  'installed_rom_proved': False, 'target_executed': False,
                  'hardware_validated': False, 'flashable': False}))
