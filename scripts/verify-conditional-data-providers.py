#!/usr/bin/env python3
"""Link bounded DATA windows and TX RAM only under explicit conditions."""
import argparse
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
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
ld = a.tool_dir / ('ld.lld.exe' if (a.tool_dir / 'ld.lld.exe').is_file() else 'ld.lld')
if not ld.is_file():
    raise SystemExit('LLVM linker missing')
support = runpy.run_path(str(ROOT / 'scripts/source-build-support.py'))
support['metadata']()
reader = runpy.run_path(str(support['PARSER']))['ELF']
out.mkdir(parents=True)
base = out / 'ram-model'
p = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/verify-conditional-tx-storage.py'),
                    '--tool-dir', str(a.tool_dir), '--out', str(base)], capture_output=True, text=True)
if p.returncode:
    raise ValueError('Conditional RAM model failed: ' + p.stderr[:1000])
facts = json.loads(p.stdout)
if not facts['passed'] or facts['ram_ownership_proved'] or facts['candidate_bytes_read'] or facts['flashable']:
    raise ValueError('Unexpected RAM model result')
aliases = {'tsl9_input_state_decoders_static_data_1ab48': ('tsl9_input_counter_read_window_1ab48', 0, 8, 0x1ab48),
           'tsl9_registered_callbacks_static_data_1a638': ('tsl9_sequence_compare_read_window_1a638', 0, 48, 0x1a638),
           'tsl9_record_field_transitions_static_data_1a078': ('tsl9_grid_read_data_pool_19ed8', 416, 432, 0x1a078)}
witnesses = {'tsl9_boot_resident_40000': 0x40000, 'tsl9_incoming_external_14056': 0x14056,
             'tsl9_settings_default_data_1a69c': 0x1a69c}
results = []
for mode in ('c', 'cpp'):
    folder = base / mode
    aggregate = base / 'base/source' / ('NOT-FLASHABLE-candidate-aliases-' + mode + '.o')
    alias_flags = ['--defsym=' + name + '=' + target + ('+' + str(offset) if offset else '')
                   for name, (target, offset, _, _) in aliases.items()]
    cmd = [str(ld), '--no-undefined', '--no-relax', '-T', str(folder / 'conditional.ld'), str(aggregate),
           str(folder / 'conditional-storage.o'), *alias_flags]
    strict = subprocess.run([*cmd, '-o', str(out / ('STRICT-' + mode + '.elf'))], capture_output=True, text=True)
    missing = set(re.findall(r'undefined symbol: ([^\r\n]+)', strict.stderr))
    if strict.returncode == 0 or missing != set(witnesses):
        raise ValueError('Strict conditional link must retain three dependencies')
    dest = out / ('NOT-FLASHABLE-conditional-data-' + mode + '.elf')
    proc = subprocess.run([*cmd, *['--defsym=' + k + '=' + hex(v) for k, v in witnesses.items()], '-o', str(dest)], capture_output=True, text=True)
    if proc.returncode:
        raise ValueError('Conditional link failed: ' + proc.stderr[:1000])
    elf = reader(dest)
    symbols = {s['name']: s for s in elf.symbols if s['name']}
    for name, (target, offset, size, address) in aliases.items():
        alias, owner = symbols[name], symbols[target]
        if (alias['index'] in (0, 0xfff1) or alias['index'] != owner['index'] or owner['size'] != size or
            alias['value'] != owner['value'] + offset or alias['value'] != address):
            raise ValueError('Conditional alias is not backed by its bounded source object')
    prior = reader(folder / 'NOT-FLASHABLE-conditional.elf')
    previous = {s['name']: s for s in prior.sections if s['flags'] & 2 and s['size'] and s['type'] != 8}
    flash = [s for s in elf.sections if s['flags'] & 2 and s['size'] and s['type'] != 8]
    if (len(flash) != 6235 or sum(s['size'] for s in flash) != 73551 or
        not all(s['name'] in previous and s['address'] == previous[s['name']]['address'] and elf.data(s) == prior.data(previous[s['name']]) for s in flash)):
        raise ValueError('Selected flash sections changed')
    for row in range(6):
        start, end = 0x1a078 + 16 * row, 0x1a078 + 16 * (row + 1)
        if sum(s['address'] <= start and end <= s['address'] + s['size'] for s in flash) != 1:
            raise ValueError('Conditional mode row lacks a unique selected owner')
    phoff = struct.unpack_from('<I', elf.raw, 28)[0]
    phsize, phcount = struct.unpack_from('<HH', elf.raw, 42)
    if any(struct.unpack_from('<I', elf.raw, phoff + i * phsize)[0] == 1 for i in range(phcount)):
        raise ValueError('Unexpected PT_LOAD')
    results.append({'mode': mode, 'conditional_data_aliases': len(aliases), 'mode_rows_covered': 6,
                    'strict_undefined': len(missing), 'flash_bytes_unchanged': 73551})
print(json.dumps({'passed': True, 'results': results, 'global_index_bounds_proved': False, 'ram_ownership_proved': False,
                  'candidate_bytes_read': 0, 'excluded_read': False, 'diagnostic_pt_load': 0, 'flashable': False}))
