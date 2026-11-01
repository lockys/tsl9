#!/usr/bin/env python3
"""Build an unplaced aggregate and test evidence-backed candidate aliases offline."""
import argparse
import concurrent.futures
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
p.add_argument('--tx-candidate', type=Path, help='Compare and integrate the bounded 280-byte TX candidate')
p.add_argument('--compact-map', action='store_true', help='Use pinned previously verified mappings without opening the historical build object')
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
tools = {n: a.tool_dir / (n + '.exe' if (a.tool_dir / (n + '.exe')).is_file() else n)
         for n in ('clang', 'ld.lld', 'llvm-objcopy')}
if not all(v.is_file() for v in tools.values()):
    raise SystemExit('LLVM compiler, linker or objcopy missing')
module = runpy.run_path(str(ROOT / 'scripts/verify-curated-source.py'))
manifest = module['metadata']()
reader = runpy.run_path(str(module['PARSER']))['ELF']
resource = Path(subprocess.check_output([str(tools['clang']), '-print-resource-dir'], text=True).strip()).resolve()
compact = None
olddefs = {}
if a.compact_map:
    map_path = ROOT / 'experiments/tsl9-source-aggregate/compact-layout.json'
    if hashlib.sha256(map_path.read_bytes()).hexdigest() != '74d1641e9397a4e623d1a396dda7ceb070ea9b5d11675cdff00600fa5acc32b8':
        raise ValueError('Pinned compact mapping changed')
    compact = json.loads(map_path.read_text(encoding='utf-8'))
    if compact['schema'] != 'tsl9-selected-source-layout-compact-v1':
        raise ValueError('Unknown compact mapping')
else:
    old_path = ROOT / 'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/split-C-payload.o'
    if hashlib.sha256(old_path.read_bytes()).hexdigest() != 'fbfc95442f35275192e698c0252a1540922f342f06562b42817603fda42c6965':
        raise ValueError('Historical object changed')
    old = reader(old_path)
    olddefs = {s['name']: s for s in old.symbols if s['name'] and s['index'] not in (0, 0xfff1) and s['info'] >> 4 in (1, 2)}
data = manifest['native_data_units']
for u in data:
    if hashlib.sha256((ROOT / u['origin_unit']).read_bytes()).hexdigest() != u['origin_unit_sha256']:
        raise ValueError('Data source provenance changed')
window = {'name': 'conditional-window-1ab37', 'curated_unit': 'src/native/receive/conditional_window_1ab37.c',
          'spec': 'experiments/tsl9-input-counter-integration/spec-v1.json'}
jobs = [(u, mode, 'code') for u in manifest['native_units'] for mode in ('c', 'cpp')]
jobs += [(u, mode, 'data') for u in data + [window] for mode in ('c', 'cpp')]
out.mkdir(parents=True)
for unit, mode, kind in jobs:
    (out / mode / unit['name']).mkdir(parents=True, exist_ok=True)
def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Build command failed: ' + result.stderr[:1000])
    return result
def compile_one(job):
    unit, mode, kind = job
    folder = out / mode / unit['name']
    if kind == 'code':
        cmd = module['command']({'clang': tools['clang']}, unit, mode, 'curated', folder)
    else:
        spec = json.loads((ROOT / unit['spec']).read_text(encoding='utf-8'))
        cmd = [tools['clang'], *spec['flags'][mode], '-c', '-MD', '-MF', folder / 'unit.d', '-MT', 'unit.o',
               ROOT / unit['curated_unit'], '-o', folder / 'unit.o']
    run(cmd)
    module['dependencies'](folder, 'curated', resource)
    return (unit['name'], mode), folder / 'unit.o'
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    built = dict(pool.map(compile_one, jobs))
tx = out / 'tx'
if a.tx_candidate:
    tx_result = json.loads(run([sys.executable, '-B', ROOT / 'src/native/tx_candidate/verify-linked.py',
                                '--tool-dir', a.tool_dir, '--candidate', a.tx_candidate, '--out', tx]).stdout)
    if not tx_result['passed'] or tx_result['candidate_bytes_read'] != 280 or tx_result['flashable']:
        raise ValueError('TX compilation failed')
expected = {'tsl9_boot_resident_40000', 'tsl9_incoming_external_14056', 'tsl9_input_state_decoders_static_data_1ab48',
            'tsl9_record_field_transitions_static_data_1a078', 'tsl9_registered_callbacks_static_data_1a638',
            'tsl9_runtime_reset_stack_top', 'tsl9_settings_default_data_1a69c'}
if a.tx_candidate:
    expected.add('__tsl9v4160_data_2000b18c')
helpers = {'ml_port_read8', 'ml_port_read32', 'ml_port_write32'}
results = []
for mode in ('c', 'cpp'):
    objects = []
    transport = reader(built['transport-frame', mode])
    transport_names = {s['name'] for s in transport.symbols if s['name'] and s['index'] not in (0, 0xfff1) and s['info'] >> 4 in (1, 2)}
    external = []
    for unit, jobmode, _ in jobs:
        if jobmode != mode:
            continue
        path = built[unit['name'], mode]
        elf = reader(path)
        if a.tx_candidate and unit['name'] != 'transport-frame':
            external.extend(r['symbol']['name'] for r in elf.relocations if r['symbol']['name'] in transport_names)
        if a.tx_candidate and unit['name'] == 'transport-frame':
            continue
        definitions = {s['name'] for s in elf.symbols if s['name'] in helpers and s['index'] not in (0, 0xfff1) and s['info'] >> 4 in (1, 2)}
        imports = {s['name'] for s in elf.symbols if s['name'] in helpers and s['index'] == 0}
        references = [r for r in elf.relocations if r['symbol']['name'] in helpers]
        if imports or references or definitions != (helpers if unit['name'] in ('adc', 'resident-memory') else set()):
            raise ValueError('Unexpected helper ownership or references')
        if definitions:
            localized = path.with_name('localized.o')
            run([tools['llvm-objcopy'], *['--localize-symbol=' + name for name in sorted(helpers)], path, localized])
            path = localized
        objects.append(path)
    if a.tx_candidate:
        if len(transport_names) != 13 or external != ['tsl9_filter_external_8a56'] * 8:
            raise ValueError('Unexpected external references to the old TX unit')
        composite = out / ('NOT-FLASHABLE-tx-composite-' + mode + '.o')
        run([tools['ld.lld'], '-r', '--no-relax', '-T', tx / 'tx-only.ld', tx / 'pre' / ('entry-' + mode + '.o'),
             tx / ('valid_body-ordered-' + mode + '.o'), tx / 'pre' / ('return_leaf-' + mode + '.o'), '-o', composite])
        tx_obj = reader(composite)
        if tx_obj.byname['.text.tsl9_tx_composite']['size'] != 280:
            raise ValueError('Unexpected TX composite size')
        objects.append(composite)
    if len(objects) != 139:
        raise ValueError('Unexpected source unit count')
    aggregate = out / ('NOT-FLASHABLE-unplaced-' + mode + '.o')
    tx_alias = ['--defsym=tsl9_filter_external_8a56=__tsl9v4160_call_8a56'] if a.tx_candidate else []
    run([tools['ld.lld'], '-m', 'elf32lriscv', '-r', '--no-relax', *tx_alias, *objects, '-o', aggregate])
    elf = reader(aggregate)
    if a.tx_candidate:
        symbols = {s['name']: s for s in elf.symbols if s['name']}
        old_entry, new_entry = symbols['tsl9_filter_external_8a56'], symbols['__tsl9v4160_call_8a56']
        if old_entry['index'] != new_entry['index'] or old_entry['value'] != new_entry['value'] or elf.sections[new_entry['index']]['name'] != '.text.tsl9_tx_composite':
            raise ValueError('TX entry alias does not reference the compiled composite')
    unresolved = {s['name'] for s in elf.symbols if s['name'] and s['index'] == 0 and s['info'] >> 4 in (1, 2)}
    defs = [s for s in elf.symbols if s['name'] and s['index'] not in (0, 0xfff1) and s['info'] >> 4 in (1, 2)]
    aliases = dict(compact['candidate_aliases']) if compact else {}
    for name in sorted(unresolved & set(olddefs)):
        s = olddefs[name]
        section = old.sections[s['index']]
        address = int(section['name'].rsplit('_', 1)[-1], 16) + s['value']
        targets = [x for x in defs if x['name'] == 'tsl9_runtime_reset_initializer'] if name == 'tsl9_boot_initializer_1ab60' else [x for x in defs if x['name'].lower().endswith('_' + format(address, 'x'))]
        if len(targets) != 1:
            raise ValueError('Ambiguous candidate target: ' + name)
        target = targets[0]
        n = target['size']
        prior = old.data(section)[s['value']:s['value'] + n]
        current = elf.data(elf.sections[target['index']])[target['value']:target['value'] + n]
        if not n or len(prior) != n or prior != current:
            raise ValueError('Candidate prelink bytes differ: ' + name)
        aliases[name] = target['name']
    if len(aliases) != 72 or not set(aliases).issubset(unresolved) or not set(aliases.values()).issubset({s['name'] for s in defs}) or unresolved - set(aliases) != expected:
        raise ValueError('Unexpected unresolved inventory')
    linked = out / ('NOT-FLASHABLE-candidate-aliases-' + mode + '.o')
    run([tools['ld.lld'], '-r', '--no-relax', *['--defsym=' + k + '=' + v for k, v in aliases.items()], aggregate, '-o', linked])
    final = reader(linked)
    symbols = {s['name']: s for s in final.symbols if s['name']}
    remaining = {s['name'] for s in final.symbols if s['name'] and s['index'] == 0 and s['info'] >> 4 in (1, 2)}
    if remaining != expected or not all(symbols[k]['index'] not in (0, 0xfff1) and symbols[k]['index'] == symbols[v]['index'] and symbols[k]['value'] == symbols[v]['value'] for k, v in aliases.items()):
        raise ValueError('Candidate alias or unresolved inventory changed')
    results.append({'mode': mode, 'fresh_objects': len(objects), 'candidate_aliases': len(aliases), 'remaining_undefined': len(remaining)})
print(json.dumps({'passed': True, 'results': results, 'uses_historical_object_for_comparison': not a.compact_map,
                  'original_coordinate_layout_proved': False, 'relocation_semantics_proved': False,
                  'tx_candidate_integrated': bool(a.tx_candidate), 'excluded_read': False, 'flashable': False}))
