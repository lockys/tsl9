#!/usr/bin/env python3
"""Place selected freshly built source sections in a nonloadable diagnostic ELF."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
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
ld = a.tool_dir / ('ld.lld.exe' if (a.tool_dir / 'ld.lld.exe').is_file() else 'ld.lld')
if not ld.is_file():
    raise SystemExit('LLVM linker missing')
module = runpy.run_path(str(ROOT / 'scripts/verify-curated-source.py'))
module['metadata']()
reader = runpy.run_path(str(module['PARSER']))['ELF']
old_path = ROOT / 'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/split-C-payload.o'
if hashlib.sha256(old_path.read_bytes()).hexdigest() != 'fbfc95442f35275192e698c0252a1540922f342f06562b42817603fda42c6965':
    raise ValueError('Historical object changed')
old = reader(old_path)
olddefs = {s['name']: s for s in old.symbols if s['name'] and s['index'] not in (0, 0xfff1) and s['info'] >> 4 in (1, 2)}
regions = []
for s in old.sections:
    if s['flags'] & 2 and s['size'] and s['type'] != 8 and '_span_' in s['name']:
        start = int(s['name'].rsplit('_', 1)[-1], 16)
        regions.append((start, start + s['size'], s))
out.mkdir(parents=True)
def run(args):
    r = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if r.returncode:
        raise ValueError('Build failed: ' + r.stderr[:1000])
    return json.loads(r.stdout)
reference_dir, aggregate_dir = out / 'reference', out / 'source'
ref_result = run([sys.executable, '-B', ROOT / 'scripts/verify-window-1ab37.py', '--tool-dir', a.tool_dir,
                  '--candidate', a.candidate, '--out', reference_dir])
agg_result = run([sys.executable, '-B', ROOT / 'scripts/verify-source-aggregate.py', '--tool-dir', a.tool_dir,
                  '--tx-candidate', a.candidate, '--out', aggregate_dir])
if not ref_result['passed'] or ref_result['checked_candidate_bytes'] != 73551 or not agg_result['passed'] or not agg_result['tx_candidate_integrated']:
    raise ValueError('Reference or source build failed')
reference = reader(reference_dir / 'NOT-FLASHABLE-layout-c.elf')
ref_sections = [s for s in reference.sections if s['flags'] & 2 and s['size']]
witnesses = {'tsl9_boot_resident_40000': 0x40000, 'tsl9_incoming_external_14056': 0x14056,
             'tsl9_input_state_decoders_static_data_1ab48': 0x1ab48, 'tsl9_record_field_transitions_static_data_1a078': 0x1a078,
             'tsl9_registered_callbacks_static_data_1a638': 0x1a638, 'tsl9_settings_default_data_1a69c': 0x1a69c,
             '__tsl9v4160_data_2000b18c': 0x2000b18c}
results = []
for mode in ('c', 'cpp'):
    source = aggregate_dir / ('NOT-FLASHABLE-candidate-aliases-' + mode + '.o')
    elf = reader(source)
    candidates = collections.defaultdict(set)
    for symbol in elf.symbols:
        if symbol['name'] in olddefs and symbol['index'] not in (0, 0xfff1) and symbol['info'] >> 4 in (1, 2):
            previous = olddefs[symbol['name']]
            section = old.sections[previous['index']]
            if '_span_' in section['name']:
                candidates[symbol['index']].add(int(section['name'].rsplit('_', 1)[-1], 16) + previous['value'] - symbol['value'])
    selected = []
    for section in elf.sections:
        if not (section['flags'] & 2 and section['size']):
            continue
        if section['name'] == '.text.tsl9_tx_composite':
            start = 0x8a56
        elif section['name'] == '.rodata.tsl9_conditional_window_1ab37':
            start = 0x1ab37
        else:
            choices = candidates[section['index']]
            if len(choices) != 1 or section['type'] == 8:
                continue
            start = next(iter(choices))
            matches = [(lo, s) for lo, hi, s in regions if lo <= start and start + section['size'] <= hi]
            if len(matches) != 1:
                continue
            lo, previous = matches[0]
            if elf.data(section) != old.data(previous)[start - lo:start - lo + section['size']]:
                continue
        end = start + section['size']
        if (not re.fullmatch(r'[.A-Za-z0-9_]+', section['name']) or not 0x8000 <= start < end <= 0x1ac00 or
            any(not (end <= lo or start >= hi) for lo, hi in ((0x14056, 0x14c8a), (0x1a69c, 0x1a6a0)))):
            raise ValueError('Rejected section or range')
        selected.append((start, end, section['name']))
    selected.sort()
    if (len(selected) != 6235 or sum(b - a for a, b, _ in selected) != 73551 or
        len({name for _, _, name in selected}) != len(selected) or
        any(b > c for (_, b, _), (c, _, _) in zip(selected, selected[1:]))):
        raise ValueError('Selected layout overlap or unexpected coverage')
    layout = out / ('diagnostic-' + mode + '.ld')
    lines = ['OUTPUT_ARCH(riscv)', 'PHDRS { evidence PT_NULL FLAGS(0); }', 'SECTIONS {']
    lines += [f' .output_{i} 0x{start:x} : SUBALIGN(1) {{ KEEP(*({name})) }} :NONE' for i, (start, _, name) in enumerate(selected)]
    lines += [' /DISCARD/ : { *(.text*) *(.rodata*) *(.data*) *(.bss*) *(.sdata*) *(.sbss*) *(.eh_frame*) *(.comment) *(.note*) *(.riscv.attributes) *(.llvm_addrsig) }', '}']
    layout.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    command = [str(ld), '--no-undefined', '--no-relax', '-T', str(layout), str(source)]
    strict = subprocess.run([*command, '-o', str(out / ('STRICT-' + mode + '.elf'))], capture_output=True, text=True)
    missing = set(re.findall(r'undefined symbol: ([^\r\n]+)', strict.stderr))
    if strict.returncode == 0 or missing != set(witnesses):
        raise ValueError('Strict link must report exactly seven dependencies')
    dest = out / ('NOT-FLASHABLE-source-layout-' + mode + '.elf')
    run_result = subprocess.run([*command, *['--defsym=' + k + '=' + hex(v) for k, v in witnesses.items()], '-o', str(dest)], capture_output=True, text=True)
    if run_result.returncode:
        raise ValueError('Diagnostic link failed: ' + run_result.stderr[:1000])
    result = reader(dest)
    allocated = [s for s in result.sections if s['flags'] & 2 and s['size']]
    if len(allocated) != len(selected) or sum(s['size'] for s in allocated) != 73551:
        raise ValueError('Unexpected linked coverage')
    compared = 0
    for s in allocated:
        start, end = s['address'], s['address'] + s['size']
        owners = [x for x in ref_sections if x['address'] <= start and end <= x['address'] + x['size']]
        if len(owners) != 1:
            raise ValueError('Reference ownership missing')
        owner = owners[0]
        if result.data(s) != reference.data(owner)[start - owner['address']:end - owner['address']]:
            raise ValueError('Linked bytes differ: ' + hex(start))
        compared += s['size']
    phoff = struct.unpack_from('<I', result.raw, 28)[0]
    phsize, phcount = struct.unpack_from('<HH', result.raw, 42)
    if any(struct.unpack_from('<I', result.raw, phoff + i * phsize)[0] == 1 for i in range(phcount)):
        raise ValueError('Unexpected PT_LOAD')
    results.append({'mode': mode, 'source_sections': len(selected), 'matched_bytes': compared, 'strict_undefined': len(missing)})
print(json.dumps({'passed': True, 'results': results, 'numeric_witnesses_only': True, 'diagnostic_pt_load': 0,
                  'excluded_read': False, 'complete_firmware': False, 'flashable': False}))
