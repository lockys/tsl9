#!/usr/bin/env python3
"""Derive compact source build metadata from the independently curated inventory."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser()
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents or not out.parent.is_dir():
    raise SystemExit('Output must be a new file outside the project')
module = runpy.run_path(str(ROOT / 'scripts/verify-curated-source.py'))
manifest = module['metadata']()
profiles, units = {}, []
for unit in manifest['native_units']:
    flags = {mode: module['flags'](unit, mode) for mode in ('c', 'cpp')}
    profile = unit['profile']
    if profile in profiles and profiles[profile] != flags:
        raise ValueError('Inconsistent code profile: ' + profile)
    profiles[profile] = flags
    units.append({k: unit[k] for k in ('name', 'curated_unit', 'profile')})
data, data_profiles = [], {}
for unit in manifest['native_data_units']:
    flags = json.loads((ROOT / unit['spec']).read_text(encoding='utf-8'))['flags']
    if set(flags) != {'c', 'cpp'}:
        raise ValueError('Unknown data compiler modes')
    profile = hashlib.sha256(json.dumps(flags, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    data_profiles[profile] = flags
    data.append({'name': unit['name'], 'curated_unit': unit['curated_unit'], 'profile': profile})
counter = next(x for x in data if x['name'] == 'input-counter-data')
window = {'name': 'conditional-window-1ab37', 'curated_unit': 'src/native/receive/conditional_window_1ab37.c', 'profile': counter['profile']}
opaque = {'name': 'opaque-allowed-gaps', 'curated_unit': 'src/native/receive/opaque_allowed_gaps.c', 'profile': counter['profile']}
record = {'schema': 'tsl9-source-build-v1', 'files': [{k: x[k] for k in ('destination', 'sha256')} for x in manifest['files']],
          'native_units': units, 'code_profiles': profiles, 'native_data_units': data, 'data_profiles': data_profiles, 'window': window, 'opaque': opaque}
if len(record['files']) != 173 or len(units) != 125 or len(data) != 13:
    raise ValueError('Unexpected source inventory')
with out.open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(record, stream, sort_keys=True, indent=2)
    stream.write('\n')
print(json.dumps({'passed': True, 'files': len(record['files']), 'code_units': len(units), 'data_units': len(data),
                  'sha256': hashlib.sha256(out.read_bytes()).hexdigest(), 'firmware_read': False}))
