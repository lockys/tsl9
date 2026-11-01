#!/usr/bin/env python3
"""Compile source-owned TX fragments only; never read firmware or create a flashable image."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
parts = (
    ('entry', '.text.tsl9_tx_entry', 8, '487c6497a4cdd3be5d1018e698b41718911d4f4e55c950749df0587a5b69fb99', ((4, 'R_RISCV_BRANCH', 'tsl9_tx_oversized_return', '+', '0'),)),
    ('valid_body', '.text.tsl9_tx_valid_body', 270, '8813de5f1bc77d34baf8528c694c0f111c7dec5eef18cb388253a2c8e7b1b9d3', ((120, 'R_RISCV_PCREL_HI20', '__tsl9v4160_data_2000b18c', '+', '0'), (124, 'R_RISCV_PCREL_LO12_I', '.Lpcrel_hi0', '+', '0'))),
    ('return_leaf', '.text.tsl9_tx_oversized_return', 2, '7529d4e6ceb037815e2664a7277abb404b02f0bf9ddbf5c11658f52448221cba', ()),
)
parser = argparse.ArgumentParser()
parser.add_argument('--tool-dir', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True, help='new, empty output directory outside the source tree')
args = parser.parse_args()
out = args.out.resolve()
if out.exists() or out == HERE or HERE in out.parents:
    raise SystemExit('Output must be a new path outside the source tree')
out.mkdir(parents=True)
def tool(name):
    p = args.tool_dir / (name + ('.exe' if (args.tool_dir / (name + '.exe')).is_file() else ''))
    if not p.is_file(): raise SystemExit('Missing tool: ' + name)
    return str(p)
allowed = {1, 2, 5, 6, 7, *range(10, 18), *range(28, 32)}
common = ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-Oz', '-mllvm', '-enable-machine-outliner=never', '-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables', '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror'] + ['-ffixed-x'+str(i) for i in range(1, 32) if i not in allowed]
digests = []
for mode in ('c', 'cpp'):
    payload = bytearray()
    for name, section, size, expected, markers in parts:
        obj = out / (name + '-' + mode + '.o')
        fragment = out / (name + '-' + mode + '.fragment')
        flags = ['-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17'] + (['-fno-exceptions'] if mode == 'cpp' else [])
        subprocess.run([tool('clang'), *common, *flags, '-c', str(HERE / (name + '.c')), '-o', str(obj)], check=True)
        subprocess.run([tool('llvm-objcopy'), '-O', 'binary', '--only-section='+section, str(obj), str(fragment)], check=True)
        data = fragment.read_bytes()
        if len(data) != size or hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit('Pre-pass section mismatch: '+mode+'/'+name)
        rel = subprocess.check_output([tool('llvm-readelf'), '-r', str(obj)], text=True, encoding='utf-8')
        parsed = [(int(offset, 16), kind, symbol, sign, addend) for offset, kind, symbol, sign, addend in re.findall(r'^\s*([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+(R_RISCV_\w+)\s+[0-9a-fA-F]+\s+(\S+)\s+([+-])\s+(\w+)', rel, re.MULTILINE)]
        if tuple(parsed) != markers or rel.count('R_RISCV_') != len(parsed): raise SystemExit('Relocation mismatch: '+mode+'/'+name)
        payload.extend(data)
    # Unlinked, pre-pass bytes are deliberately labelled; relocations have NOT been applied.
    diagnostic = out / ('NOT-FLASHABLE-unlinked-TX-' + mode + '.bin')
    diagnostic.write_bytes(payload)
    digests.append(hashlib.sha256(payload).hexdigest())
if digests[0] != digests[1]: raise SystemExit('C and C++ fragments differ')
print(json.dumps({'passed': True, 'fragment_bytes': 280, 'unlinked_sha256': digests[0], 'relocations_applied': False, 'frame_postpass_applied': False, 'flashable': False, 'firmware_read': False}))
