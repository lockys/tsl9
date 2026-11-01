#!/usr/bin/env python3
"""Compare freshly compiled origin and curated data objects, offline."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser()
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
clang = a.tool_dir / ('clang.exe' if (a.tool_dir / 'clang.exe').is_file() else 'clang')
if not clang.is_file():
    raise SystemExit('Compiler not found')
module = runpy.run_path(str(ROOT / 'scripts/verify-curated-source.py'))
manifest = module['metadata']()
reader = runpy.run_path(str(module['PARSER']))['ELF']
resource = Path(subprocess.check_output([str(clang), '-print-resource-dir'], text=True).strip()).resolve()
units = manifest['native_data_units']
def sha(data):
    return hashlib.sha256(data).hexdigest()
def facts(path):
    elf = reader(path)
    if elf.kind != 1 or elf.flags != 1:
        raise ValueError('Not a relocatable RV32 RVC object')
    sections = [(s['name'], s['size'], s['flags'], s['type'], None if s['type'] == 8 else sha(elf.data(s)))
                for s in elf.sections if s['flags'] & 2 and s['size']]
    relocs = [(r['owner'], r['offset'], r['type'], r['addend'], r['symbol']['name']) for r in elf.relocations]
    symbols = sorted((s['name'], s['info'], s['value'], s['size'], s['index'])
                     for s in elf.symbols if s['name'] and s['info'] & 15 != 4)
    return sections, relocs, symbols
def task(job):
    unit, mode, variant = job
    folder = out / unit['name'] / mode / variant
    spec = json.loads((ROOT / unit['spec']).read_text(encoding='utf-8'))
    source = ROOT / unit['origin_unit' if variant == 'origin' else 'curated_unit']
    command = [str(clang), *spec['flags'][mode], '-c', '-MD', '-MF', str(folder / 'unit.d'),
               '-MT', 'unit.o', str(source), '-o', str(folder / 'unit.o')]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Compilation failed for ' + unit['name'] + '/' + mode + '/' + variant + ': ' + result.stderr[:1000])
    module['dependencies'](folder, variant, resource)
    return (unit['name'], mode, variant), facts(folder / 'unit.o')
for unit in units:
    if sha((ROOT / unit['origin_unit']).read_bytes()) != unit['origin_unit_sha256']:
        raise ValueError('Original data source hash mismatch: ' + unit['name'])
jobs = [(u, mode, variant) for u in units for mode in ('c', 'cpp') for variant in ('origin', 'curated')]
out.mkdir(parents=True)
for unit, mode, variant in jobs:
    (out / unit['name'] / mode / variant).mkdir(parents=True, exist_ok=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = dict(pool.map(task, jobs))
for unit in units:
    for mode in ('c', 'cpp'):
        if results[unit['name'], mode, 'origin'] != results[unit['name'], mode, 'curated']:
            raise ValueError('Object mismatch: ' + unit['name'] + '/' + mode)
print(json.dumps({'passed': True, 'data_units': len(units), 'compilations': len(jobs),
                  'firmware_read': False, 'target_execution': False, 'flashable': False}))
