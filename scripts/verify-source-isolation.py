#!/usr/bin/env python3
"""Rebuild from a bounded source-only copy without candidate or research trees."""
import argparse
import json
from pathlib import Path
import runpy
import shutil
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
manifest = support['metadata']()
paths = [x['destination'] for x in manifest['files']]
paths += ['src/source-build-manifest.json', 'src/compact-layout.json', 'src/native/tx_candidate/verify-linked.py', 'src/native/tx_candidate/verify.py']
paths += ['src/native/tx_candidate/postpass/' + x for x in ('elf32.py', 'decode.py', 'schedule.py', 'policy.json')]
paths += ['scripts/build-compact-source-layout.py', 'scripts/verify-source-aggregate.py', 'scripts/source-build-support.py']
if len(paths) != 184 or len(paths) != len(set(paths)):
    raise ValueError('Unexpected isolation inventory')
tree = out / 'source-only'
for name in paths:
    source, dest = (ROOT / name).resolve(), (tree / name).resolve()
    if not source.is_relative_to(ROOT) or not dest.is_relative_to(tree) or not source.is_file():
        raise ValueError('Rejected source copy path')
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, dest)
if (tree / 'experiments').exists() or (tree / 'analysis').exists() or (tree / 'artifacts').exists():
    raise ValueError('Isolation contains research or firmware inputs')
result = subprocess.run([sys.executable, '-B', str(tree / 'scripts/build-compact-source-layout.py'),
                         '--tool-dir', str(a.tool_dir), '--out', str(out / 'build')], capture_output=True, text=True)
if result.returncode:
    raise ValueError('Isolated build failed: ' + result.stderr[:1000])
facts = json.loads(result.stdout)
if not facts['passed'] or facts['candidate_bytes_read'] or facts['historical_build_object_read'] or facts['flashable']:
    raise ValueError('Unexpected isolated build result')
print(json.dumps({'passed': True, 'copied_files': len(paths), 'results': facts['results'], 'candidate_bytes_read': 0,
                  'experiments_present': False, 'analysis_present': False, 'firmware_present': False, 'flashable': False}))
