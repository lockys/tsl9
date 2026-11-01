#!/usr/bin/env python3
"""Rebuild a pinned selected source layout without historical build objects."""
import argparse
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
p.add_argument('--candidate', type=Path, help='Optionally compare the bounded candidate TX window')
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
path = ROOT / 'src/compact-layout.json'
if hashlib.sha256(path.read_bytes()).hexdigest() != '74d1641e9397a4e623d1a396dda7ceb070ea9b5d11675cdff00600fa5acc32b8':
    raise ValueError('Pinned compact mapping changed')
mapping = json.loads(path.read_text(encoding='utf-8'))
if mapping['schema'] != 'tsl9-selected-source-layout-compact-v1':
    raise ValueError('Unknown compact mapping')
ld = a.tool_dir / ('ld.lld.exe' if (a.tool_dir / 'ld.lld.exe').is_file() else 'ld.lld')
if not ld.is_file():
    raise SystemExit('LLVM linker missing')
module = runpy.run_path(str(ROOT / 'scripts/source-build-support.py'))
module['metadata']()
reader = runpy.run_path(str(module['PARSER']))['ELF']
out.mkdir(parents=True)
source_dir = out / 'source'
aggregate_args = [sys.executable, '-B', str(ROOT / 'scripts/verify-source-aggregate.py'), '--compact-map',
                  '--tool-dir', str(a.tool_dir), '--out', str(source_dir)]
aggregate_args += ['--tx-candidate', str(a.candidate)] if a.candidate else ['--source-tx']
p = subprocess.run(aggregate_args, capture_output=True, text=True)
if p.returncode:
    raise ValueError('Source aggregate failed: ' + p.stderr[:1000])
agg = json.loads(p.stdout)
if not agg['passed'] or agg['uses_historical_object_for_comparison'] or not agg['tx_candidate_integrated']:
    raise ValueError('Unexpected source aggregate')
witnesses = {'tsl9_boot_resident_40000': 0x40000, 'tsl9_incoming_external_14056': 0x14056,
             'tsl9_input_state_decoders_static_data_1ab48': 0x1ab48, 'tsl9_record_field_transitions_static_data_1a078': 0x1a078,
             'tsl9_registered_callbacks_static_data_1a638': 0x1a638, 'tsl9_settings_default_data_1a69c': 0x1a69c,
             '__tsl9v4160_data_2000b18c': 0x2000b18c}
results = []
for mode in ('c', 'cpp'):
    source = source_dir / ('NOT-FLASHABLE-candidate-aliases-' + mode + '.o')
    elf = reader(source)
    selected = []
    for section in elf.sections:
        if not (section['flags'] & 2 and section['size']) or section['type'] == 8 or section['name'] in mapping['exclude_sections']:
            continue
        match = re.search(r'_([0-9a-f]+)$', section['name'])
        if section['name'] in mapping['exceptions']:
            start = mapping['exceptions'][section['name']]
        elif match:
            start = int(match[1], 16)
        else:
            continue
        end = start + section['size']
        if not (0x8000 <= start < end <= 0x1ac00):
            continue
        if any(not (end <= lo or start >= hi) for lo, hi in ((0x14056, 0x14c8a), (0x1a69c, 0x1a6a0))):
            raise ValueError('Selected range intersects an excluded region')
        if not re.fullmatch(r'[.A-Za-z0-9_]+', section['name']):
            raise ValueError('Invalid section name')
        selected.append((start, end, section['name']))
    selected.sort()
    if (len(selected) != mapping['expected_sections'] or sum(b - a for a, b, _ in selected) != mapping['expected_bytes'] or
        len({name for _, _, name in selected}) != len(selected) or
        any(b > c for (_, b, _), (c, _, _) in zip(selected, selected[1:]))):
        raise ValueError('Selected layout overlap or coverage drift')
    pre = hashlib.sha256()
    for _, _, name in selected:
        pre.update(elf.data(elf.byname[name]))
    if pre.hexdigest() != mapping['selected_prelink_sha256']:
        raise ValueError('Selected prelink source bytes differ')
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
    dest = out / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf')
    linked = subprocess.run([*command, *['--defsym=' + k + '=' + hex(v) for k, v in witnesses.items()], '-o', str(dest)], capture_output=True, text=True)
    if linked.returncode:
        raise ValueError('Diagnostic link failed: ' + linked.stderr[:1000])
    result = reader(dest)
    allocated = sorted((s for s in result.sections if s['flags'] & 2 and s['size']), key=lambda s: s['address'])
    if len(allocated) != len(selected) or sum(s['size'] for s in allocated) != mapping['expected_bytes']:
        raise ValueError('Unexpected linked coverage')
    post = hashlib.sha256()
    for s, (start, end, _) in zip(allocated, selected):
        if (s['address'], s['address'] + s['size']) != (start, end):
            raise ValueError('Linked section moved')
        post.update(result.data(s))
    if post.hexdigest() != mapping['selected_linked_sha256']:
        raise ValueError('Relocated section bytes differ')
    phoff = struct.unpack_from('<I', result.raw, 28)[0]
    phsize, phcount = struct.unpack_from('<HH', result.raw, 42)
    if any(struct.unpack_from('<I', result.raw, phoff + i * phsize)[0] == 1 for i in range(phcount)):
        raise ValueError('Unexpected PT_LOAD')
    results.append({'mode': mode, 'source_sections': len(selected), 'matched_bytes': mapping['expected_bytes'], 'strict_undefined': len(missing)})
print(json.dumps({'passed': True, 'results': results, 'historical_build_object_read': False,
                  'candidate_bytes_read': agg['candidate_bytes_read'],
                  'numeric_witnesses_only': True, 'diagnostic_pt_load': 0, 'excluded_read': False,
                  'complete_firmware': False, 'flashable': False}))
