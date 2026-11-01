#!/usr/bin/env python3
"""Compile and partially link two bounded data windows; never produce firmware."""
import argparse
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
tools = {name: a.tool_dir / (name + '.exe' if (a.tool_dir / (name + '.exe')).is_file() else name)
         for name in ('clang', 'ld.lld')}
if not all(p.is_file() for p in tools.values()):
    raise SystemExit('Compiler or linker missing')
mod = runpy.run_path(str(ROOT / 'scripts/verify-curated-source.py'))
m = mod['metadata']()
reader = runpy.run_path(str(mod['PARSER']))['ELF']
resource = Path(subprocess.check_output([str(tools['clang']), '-print-resource-dir'], text=True).strip()).resolve()
code = {x['name']: x for x in m['native_units']}
data = {x['name']: x for x in m['native_data_units']}
cases = [('input-state-decoders', 'input-counter-data', 'tsl9_input_state_decoders_static_data_1ab48', 'tsl9_input_counter_read_window_1ab48', 8),
         ('registered-callbacks', 'sequence-pattern-data', 'tsl9_registered_callbacks_static_data_1a638', 'tsl9_sequence_compare_read_window_1a638', 48)]
def run(cmd):
    result = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Compile or link failed: ' + result.stderr[:1000])
def symbols(path, names):
    elf = reader(path)
    if elf.kind != 1 or elf.flags != 1:
        raise ValueError('Expected relocatable RV32 object')
    return {s['name']: s for s in elf.symbols if s['name'] in names}
out.mkdir(parents=True)
results = []
for cname, dname, alias, owner, length in cases:
    for mode in ('c', 'cpp'):
        folder = out / cname / mode
        for kind in ('code', 'data'):
            (folder / kind).mkdir(parents=True, exist_ok=True)
        codefolder = folder / 'code'
        run(mod['command']({'clang': tools['clang']}, code[cname], mode, 'curated', codefolder))
        mod['dependencies'](codefolder, 'curated', resource)
        spec = json.loads((ROOT / data[dname]['spec']).read_text(encoding='utf-8'))
        df = folder / 'data'
        run([tools['clang'], *spec['flags'][mode], '-c', '-MD', '-MF', df / 'unit.d', '-MT', 'unit.o',
             ROOT / data[dname]['curated_unit'], '-o', df / 'unit.o'])
        mod['dependencies'](df, 'curated', resource)
        inputs = [codefolder / 'unit.o', df / 'unit.o']
        negative, positive = folder / 'NOT-FLASHABLE-unbound.o', folder / 'NOT-FLASHABLE-conditional.o'
        run([tools['ld.lld'], '-r', '--no-relax', *inputs, '-o', negative])
        ns = symbols(negative, {alias, owner})
        if ns[alias]['index'] != 0 or ns[owner]['size'] != length:
            raise ValueError('Negative link must retain the unresolved consumer')
        run([tools['ld.lld'], '-r', '--no-relax', '--defsym=' + alias + '=' + owner, *inputs, '-o', positive])
        ps = symbols(positive, {alias, owner})
        if ps[alias]['index'] in (0, 0xfff1) or ps[alias]['index'] != ps[owner]['index'] or ps[alias]['value'] != ps[owner]['value'] or ps[owner]['size'] != length:
            raise ValueError('Conditional alias must resolve to the actual bounded object')
        results.append({'consumer': cname, 'provider': dname, 'mode': mode, 'window_bytes': length})
print(json.dumps({'passed': True, 'cases': results, 'global_index_bounds_proved': False,
                  'firmware_read': False, 'target_execution': False, 'flashable': False}))
