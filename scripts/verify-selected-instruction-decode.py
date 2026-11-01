#!/usr/bin/env python3
"""Disassemble selected source-built code under an explicit RV32 feature set."""
import argparse
import bisect
import collections
import json
from pathlib import Path
import re
import runpy
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
tools = {n: a.tool_dir / (n + '.exe' if (a.tool_dir / (n + '.exe')).is_file() else n) for n in ('clang', 'llvm-objdump')}
if not all(v.is_file() for v in tools.values()):
    raise SystemExit('LLVM compiler or disassembler missing')
support = runpy.run_path(str(ROOT / 'scripts/source-build-support.py'))
support['metadata']()
reader = runpy.run_path(str(support['PARSER']))['ELF']
out.mkdir(parents=True)
def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Command failed: ' + result.stderr[:1000])
    return result.stdout
features = '--mattr=+m,+a,+c,+zicsr,+zifencei'
def disassemble(path):
    text = run([tools['llvm-objdump'], '-d', features, '--no-show-raw-insn', path])
    return [(int(m.group(1), 16), m.group(2).lower()) for line in text.splitlines()
            if (m := re.match(r'^\s*([0-9a-f]+):\s+(\S+)', line))]
def unknown(mnemonic):
    return mnemonic.startswith(('<unknown>', '.word', '.short', '.byte', '.2byte', '.4byte'))
fixture = out / 'synthetic-invalid.s'
fixture.write_text('.text\n.globl invalid_fixture\ninvalid_fixture:\n.4byte 0xffffffff\n', encoding='utf-8')
fixture_obj = out / 'NOT-FLASHABLE-invalid-fixture.o'
run([tools['clang'], '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr_zifencei', '-mabi=ilp32', '-c', fixture, '-o', fixture_obj])
probe = disassemble(fixture_obj)
if not probe or not any(unknown(op) for _, op in probe):
    raise ValueError('Invalid-instruction negative control was not detected')
base = out / 'build'
facts = json.loads(run([sys.executable, '-B', ROOT / 'scripts/build-compact-source-layout.py', '--tool-dir', a.tool_dir, '--out', base]))
if not facts['passed'] or facts['candidate_bytes_read'] or facts['excluded_read'] or facts['flashable']:
    raise ValueError('Unexpected source build')
results = []
for mode in ('c', 'cpp'):
    path = base / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf')
    elf = reader(path)
    executable = sorted((s['address'], s['address'] + s['size']) for s in elf.sections if s['flags'] & 4 and s['size'])
    starts = [start for start, _ in executable]
    if not executable or any(b > c for (_, b), (c, _) in zip(executable, executable[1:])):
        raise ValueError('Invalid executable section layout')
    decoded = disassemble(path)
    counts = collections.Counter()
    for pc, op in decoded:
        i = bisect.bisect_right(starts, pc) - 1
        if i < 0 or not executable[i][0] <= pc < executable[i][1] or 0x14056 <= pc < 0x14c8a or 0x1a69c <= pc < 0x1a6a0:
            raise ValueError('Disassembly outside the selected executable ranges')
        counts[op] += 1
    unknown_count = sum(n for op, n in counts.items() if unknown(op))
    if len(decoded) != 23602 or unknown_count:
        raise ValueError('Unexpected decoded instruction count or unknown instruction')
    results.append({'mode': mode, 'decoded_instructions': len(decoded), 'unknown_instructions': unknown_count,
                    'fence_i_instructions': counts['fence.i']})
print(json.dumps({'passed': True, 'results': results, 'feature_set': 'rv32imac+zicsr+zifencei',
                  'invalid_instruction_control_detected': True, 'candidate_bytes_read': 0,
                  'excluded_read': False, 'hardware_execution': False, 'flashable': False}))
