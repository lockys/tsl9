#!/usr/bin/env python3
"""Compile one declared callback candidate; retain outputs without executing it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--tool-dir', required=True, type=Path)
    p.add_argument('--build-root', required=True, type=Path)
    a = p.parse_args()
    root, output = a.project_root.resolve(), a.build_root.resolve()
    if HERE != root / 'experiments/tsl9-nv-read-live-count' or output.exists() or not output.is_relative_to(HERE / 'build'):
        raise ValueError('New owned build directory in the canonical model only')
    tools = {n: a.tool_dir / (n + ('.exe' if os.name == 'nt' else '')) for n in ['clang', 'llvm-objdump']}
    prior = runpy.run_path(str(root / 'experiments/tsl9-delay-register-contract/verify.py'))
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    if not all(sha(path) == prior['TOOLS'][n] for n, path in tools.items()):
        raise ValueError('Declared local LLVM hashes')
    flags = ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr_zifencei', '-mabi=ilp32', '-Oz', '-mllvm', '-enable-machine-outliner=never',
             '-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
             '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror']
    output.mkdir(parents=True)
    for mode in ['c', 'cpp']:
        folder = output / mode
        folder.mkdir()
        language = ['-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17'] + (['-fno-exceptions'] if mode == 'cpp' else [])
        source = HERE / 'src/read_live_count.c'
        recipes = [('compile', [tools['clang'], *flags, *language, '-c', '-MD', '-MF', folder / 'native.d', '-MT', 'native.o', source, '-o', folder / 'native.o']),
                   ('IR', [tools['clang'], *flags, *language, '-S', '-emit-llvm', source, '-o', folder / 'native.ll']),
                   ('disassembly', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r', folder / 'native.o'])]
        commands = []
        for label, argv in recipes:
            run = subprocess.run([str(x) for x in argv], capture_output=True, timeout=120)
            log = folder / (label + '.log')
            log.write_bytes(run.stdout + run.stderr)
            commands.append(dict(label=label, argv=[str(x) for x in argv], exit=run.returncode, log_sha256=sha(log)))
            if run.returncode:
                raise ValueError('See retained ' + str(log))
        record = dict(schema='TSL9-read-live-count-candidate-compile-v1', mode=mode,
                      inputs={str(f): sha(f) for f in [Path(__file__).resolve(), source, *tools.values()]}, commands=commands,
                      target_execution=False, full_ABI_proved=False, linked=False, BIN_generated=False)
        (folder / 'compile-receipt.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(compiled=True, build_root=str(output), equivalence_proved=False, target_execution=False)))


if __name__ == '__main__':
    main()
