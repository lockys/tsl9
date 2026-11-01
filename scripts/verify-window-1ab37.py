#!/usr/bin/env python3
"""Compile and place a conditional window in a nonloadable diagnostic layout."""
import argparse
import json
from pathlib import Path
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
tools = {n: a.tool_dir / (n + '.exe' if (a.tool_dir / (n + '.exe')).is_file() else n) for n in ('clang', 'ld.lld')}
if not all(x.is_file() for x in tools.values()):
    raise SystemExit('Compiler or linker missing')
module = runpy.run_path(str(ROOT / 'scripts/verify-curated-source.py'))
module['metadata']()
reader = runpy.run_path(str(module['PARSER']))['ELF']
out.mkdir(parents=True)
def run(cmd):
    r = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if r.returncode:
        raise ValueError('Build failed: ' + r.stderr[:1000])
    return r.stdout
base = out / 'base'
result = json.loads(run([sys.executable, '-B', ROOT / 'src/native/tx_candidate/integrate-diagnostic.py',
                         '--tool-dir', a.tool_dir, '--candidate', a.candidate, '--out', base]))
if not result['passed'] or result['excluded_read'] or result['flashable'] or result['strict_link_undefined'] != 6:
    raise ValueError('Baseline verification failed')
source = ROOT / 'src/native/receive/conditional_window_1ab37.c'
spec = json.loads((ROOT / 'experiments/tsl9-input-counter-integration/spec-v1.json').read_text(encoding='utf-8'))
lo, hi = 0x1ab37, 0x1ab44
if any(not (hi <= start or lo >= end) for start, end in ((0x14056, 0x14c8a), (0x1a69c, 0x1a6a0))):
    raise ValueError('Excluded range')
with a.candidate.open('rb') as stream:
    stream.seek(lo - 0x8000)
    reference = stream.read(hi - lo)
if len(reference) != 13:
    raise ValueError('Candidate is too short')
layout = ROOT / 'experiments/tsl9-original-layout/build/event-word-table-data-v1/c/original-layout.ld'
text = layout.read_text(encoding='utf-8')
anchor = 'SECTIONS\n{\n'
if text.count(anchor) != 1:
    raise ValueError('Unexpected pinned layout')
new_layout = out / 'diagnostic.ld'
new_layout.write_text(text.replace(anchor, anchor + ' .conditional_window_1ab37 0x1ab37 : { *(.rodata.tsl9_conditional_window_1ab37) } :NONE\n'), encoding='utf-8')
prior = reader(base / 'NOT-FLASHABLE-ORIGINAL-LAYOUT.elf')
before = {s['name']: (s['address'], prior.data(s)) for s in prior.sections if s['flags'] & 2 and s['size']}
names = {'tsl9_boot_resident_40000': 0x40000, 'tsl9_incoming_external_14056': 0x14056,
         'tsl9_input_state_decoders_static_data_1ab48': 0x1ab48, 'tsl9_record_field_transitions_static_data_1a078': 0x1a078,
         'tsl9_registered_callbacks_static_data_1a638': 0x1a638, 'tsl9_settings_default_data_1a69c': 0x1a69c}
for mode in ('c', 'cpp'):
    obj = out / ('NOT-FLASHABLE-window-' + mode + '.o')
    run([tools['clang'], *spec['flags'][mode], '-c', source, '-o', obj])
    unit = reader(obj)
    sections = [s for s in unit.sections if s['flags'] & 2 and s['size']]
    if len(sections) != 1 or unit.data(sections[0]) != reference or unit.relocations:
        raise ValueError('Window compilation differs from the allowed candidate bytes')
    dest = out / ('NOT-FLASHABLE-layout-' + mode + '.elf')
    run([tools['ld.lld'], '--no-undefined', '--no-relax', '-T', new_layout,
         base / 'NOT-FLASHABLE-source-with-TX.o', obj,
         *['--defsym=' + key + '=' + hex(value) for key, value in names.items()], '-o', dest])
    elf = reader(dest)
    allocated = [s for s in elf.sections if s['flags'] & 2 and s['size']]
    after = {s['name']: (s['address'], elf.data(s)) for s in allocated}
    spans = sorted((s['address'], s['address'] + s['size']) for s in allocated)
    phoff = struct.unpack_from('<I', elf.raw, 28)[0]
    phsize, phcount = struct.unpack_from('<HH', elf.raw, 42)
    if (len(allocated) != 41 or sum(s['size'] for s in allocated) != 73551 or
        any(after[k] != v for k, v in before.items()) or
        after['.conditional_window_1ab37'] != (lo, reference) or
        any(b > c for (_, b), (c, _) in zip(spans, spans[1:])) or
        any(struct.unpack_from('<I', elf.raw, phoff + i * phsize)[0] == 1 for i in range(phcount))):
        raise ValueError('Diagnostic layout invariant failed')
print(json.dumps({'passed': True, 'modes': ['c', 'cpp'], 'extra_bytes': 13,
                  'checked_candidate_bytes': 73551, 'strict_link_undefined': 6,
                  'diagnostic_pt_load': 0, 'excluded_read': False, 'flashable': False}))
