#!/usr/bin/env python3
"""Compare a bounded reference TX window with freshly compiled source TX."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser()
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--reference', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
out = a.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
if a.reference.stat().st_size != 76800:
    raise ValueError('Unexpected reference size')
tools = {n: a.tool_dir.resolve() / (n + '.exe' if (a.tool_dir / (n + '.exe')).is_file() else n)
         for n in ('clang', 'ld.lld', 'llvm-objdump')}
if not all(v.is_file() for v in tools.values()):
    raise SystemExit('LLVM compiler, linker or disassembler missing')
lo, hi = 0x8a56, 0x8b6e
if any(not (hi <= start or lo >= end) for start, end in ((0x14056, 0x14c8a), (0x1a69c, 0x1a6a0))):
    raise ValueError('TX window intersects excluded range')
with a.reference.open('rb') as stream:
    stream.seek(lo - 0x8000)
    original = stream.read(hi - lo)
if len(original) != 280:
    raise ValueError('Short reference window')
out.mkdir(parents=True)
(out / 'NOT-FLASHABLE-reference-tx.bin').write_bytes(original)
(out / 'reference.s').write_text('.section .text.tx,"ax"\n.globl tx_original\n.type tx_original,@function\ntx_original:\n.incbin "NOT-FLASHABLE-reference-tx.bin"\n.size tx_original,.-tx_original\n', encoding='utf-8')
(out / 'reference.ld').write_text('OUTPUT_ARCH(riscv)\nSECTIONS { .text 0x8a56 : { *(.text.tx) } }\n', encoding='utf-8')
def run(args):
    result = subprocess.run([str(x) for x in args], cwd=out, capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Command failed: ' + result.stderr[:1000])
    return result.stdout
run([tools['clang'], '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-c', 'reference.s', '-o', 'reference.o'])
run([tools['ld.lld'], '--no-relax', '-T', 'reference.ld', 'reference.o', '-o', 'NOT-FLASHABLE-reference-tx.elf'])
tx = out / 'tx'
facts = json.loads(run([sys.executable, '-B', ROOT / 'src/native/tx_candidate/verify-linked.py', '--tool-dir', a.tool_dir.resolve(), '--out', tx]))
if not facts['passed'] or not facts['tx_digest_matches'] or facts['candidate_bytes_read'] or facts['flashable']:
    raise ValueError('Unexpected source TX build')
def decode(path):
    text = run([tools['llvm-objdump'], '-d', '--mattr=+m,+a,+c,+zicsr,+zifencei', '--no-show-raw-insn', path])
    rows = []
    for line in text.splitlines():
        m = re.match(r'^\s*([0-9a-f]+):\s+(.*?)\s*$', line)
        if m and lo <= int(m.group(1), 16) < hi:
            if '<unknown>' in m.group(2):
                raise ValueError('Unknown instruction in TX window')
            instruction = re.sub(r'\s+', ' ', re.sub(r'\s*<[^>]*>', '', m.group(2))).strip()
            rows.append((int(m.group(1), 16), instruction))
    if len(rows) != len(dict(rows)):
        raise ValueError('Duplicate instruction boundary')
    return dict(rows)
reference = decode(out / 'NOT-FLASHABLE-reference-tx.elf')
results = []
for mode in ('c', 'cpp'):
    selected = (tx / ('NOT-FLASHABLE-TX-ONLY-' + mode + '.bin')).read_bytes()
    current = decode(tx / ('NOT-FLASHABLE-TX-ONLY-' + mode + '.elf'))
    if len(selected) != 280 or len(reference) != 96 or len(current) != 96:
        raise ValueError('Unexpected TX extent or instruction count')
    changes = [lo + i for i, (x, y) in enumerate(zip(original, selected)) if x != y]
    shared = set(reference) & set(current)
    differences = [pc for pc in shared if reference[pc] != current[pc]]
    if (reference.get(0x8b10) != 'bltu a0, s0, 0x8b52' or current.get(0x8b10) != 'bgeu a0, s0, 0x8b2e' or
        reference.get(0x8b6a) != 'j 0x8b0a' or current.get(0x8b2c) != 'j 0x8b0a'):
        raise ValueError('Unexpected loop branch or backedge')
    results.append({'mode': mode, 'different_bytes': len(changes), 'original_instructions': len(reference),
                    'candidate_instructions': len(current), 'shared_boundaries': len(shared),
                    'different_shared_instructions': len(differences), 'loop_conditions_complementary': True})
print(json.dumps({'passed': True, 'results': results, 'reference_bytes_read': 280, 'excluded_read': False,
                  'full_behavior_equivalence_proved': False, 'target_execution': False, 'flashable': False}))
