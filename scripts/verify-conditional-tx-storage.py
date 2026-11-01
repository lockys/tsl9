#!/usr/bin/env python3
"""Test a bounded TX RAM object in a nonflashable conditional layout."""
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
tools = {n: a.tool_dir / (n + '.exe' if (a.tool_dir / (n + '.exe')).is_file() else n) for n in ('clang', 'ld.lld')}
if not all(v.is_file() for v in tools.values()):
    raise SystemExit('Compiler or linker missing')
module = runpy.run_path(str(ROOT / 'scripts/source-build-support.py'))
manifest = module['metadata']()
reader = runpy.run_path(str(module['PARSER']))['ELF']
resource = Path(subprocess.check_output([str(tools['clang']), '-print-resource-dir'], text=True).strip()).resolve()
counter = next(x for x in manifest['native_data_units'] if x['name'] == 'input-counter-data')
out.mkdir(parents=True)
base = out / 'base'
proc = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build-compact-source-layout.py'),
                       '--tool-dir', str(a.tool_dir), '--out', str(base)], capture_output=True, text=True)
if proc.returncode:
    raise ValueError('Source layout failed: ' + proc.stderr[:1000])
facts = json.loads(proc.stdout)
if not facts['passed'] or facts['candidate_bytes_read'] or facts['flashable']:
    raise ValueError('Unexpected baseline')
witnesses = {'tsl9_boot_resident_40000': 0x40000, 'tsl9_incoming_external_14056': 0x14056,
             'tsl9_input_state_decoders_static_data_1ab48': 0x1ab48, 'tsl9_record_field_transitions_static_data_1a078': 0x1a078,
             'tsl9_registered_callbacks_static_data_1a638': 0x1a638, 'tsl9_settings_default_data_1a69c': 0x1a69c}
results = []
for mode in ('c', 'cpp'):
    folder = out / mode
    folder.mkdir()
    obj = folder / 'conditional-storage.o'
    cmd = [tools['clang'], *module['data_flags'](counter, mode), '-c', '-MD', '-MF', folder / 'unit.d',
           '-MT', 'unit.o', ROOT / 'src/native/tx_candidate/conditional_storage.c', '-o', obj]
    proc = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if proc.returncode:
        raise ValueError('Storage compile failed: ' + proc.stderr[:1000])
    module['dependencies'](folder, 'curated', resource)
    unit = reader(obj)
    alloc = [s for s in unit.sections if s['flags'] & 2 and s['size']]
    symbols = [s for s in unit.symbols if s['name'] == '__tsl9v4160_data_2000b18c']
    if (len(alloc) != 1 or alloc[0]['type'] != 8 or alloc[0]['size'] != 2124 or alloc[0]['alignment'] != 4 or
        len(symbols) != 1 or symbols[0]['index'] != alloc[0]['index'] or symbols[0]['size'] != 2124 or unit.relocations):
        raise ValueError('Unexpected conditional storage object')
    layout_text = (base / ('diagnostic-' + mode + '.ld')).read_text(encoding='utf-8')
    anchor = 'SECTIONS {\n'
    if layout_text.count(anchor) != 1:
        raise ValueError('Unexpected baseline layout')
    layout = folder / 'conditional.ld'
    layout.write_text(layout_text.replace(anchor, anchor + ' .tx_storage 0x2000b18c (NOLOAD) : SUBALIGN(4) { KEEP(*(.bss.tsl9_tx_storage)) } :NONE\n'), encoding='utf-8')
    aggregate = base / 'source' / ('NOT-FLASHABLE-candidate-aliases-' + mode + '.o')
    cmd = [str(tools['ld.lld']), '--no-undefined', '--no-relax', '-T', str(layout), str(aggregate), str(obj)]
    strict = subprocess.run([*cmd, '-o', str(folder / 'STRICT.elf')], capture_output=True, text=True)
    missing = set(re.findall(r'undefined symbol: ([^\r\n]+)', strict.stderr))
    if strict.returncode == 0 or missing != set(witnesses):
        raise ValueError('Strict link must retain exactly six APP dependencies')
    dest = folder / 'NOT-FLASHABLE-conditional.elf'
    linked = subprocess.run([*cmd, *['--defsym=' + k + '=' + hex(v) for k, v in witnesses.items()], '-o', str(dest)], capture_output=True, text=True)
    if linked.returncode:
        raise ValueError('Conditional link failed: ' + linked.stderr[:1000])
    result = reader(dest)
    ram = result.byname['.tx_storage']
    if ram['type'] != 8 or ram['address'] != 0x2000b18c or ram['size'] != 2124:
        raise ValueError('Unexpected conditional RAM placement')
    original = reader(base / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf'))
    prior = {s['name']: s for s in original.sections if s['flags'] & 2 and s['size'] and s['type'] != 8}
    flash = [s for s in result.sections if s['flags'] & 2 and s['size'] and s['type'] != 8]
    if len(flash) != 6266 or sum(s['size'] for s in flash) != 73672 or not all(s['name'] in prior and s['address'] == prior[s['name']]['address'] and result.data(s) == original.data(prior[s['name']]) for s in flash):
        raise ValueError('Selected flash sections changed')
    phoff = struct.unpack_from('<I', result.raw, 28)[0]
    phsize, phcount = struct.unpack_from('<HH', result.raw, 42)
    if any(struct.unpack_from('<I', result.raw, phoff + i * phsize)[0] == 1 for i in range(phcount)):
        raise ValueError('Unexpected PT_LOAD')
    results.append({'mode': mode, 'conditional_ram_bytes': ram['size'], 'strict_undefined': len(missing), 'flash_bytes_unchanged': 73672})
print(json.dumps({'passed': True, 'results': results, 'ram_ownership_proved': False, 'candidate_bytes_read': 0,
                  'diagnostic_pt_load': 0, 'excluded_read': False, 'flashable': False}))
