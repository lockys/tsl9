#!/usr/bin/env python3
"""Compile model mutants and check they fail the host differential oracle."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clang', type=Path, required=True)
    parser.add_argument('--linker', type=Path, required=True)
    args = parser.parse_args()
    source = (ROOT / 'd14a_model.c').read_text(encoding='utf-8')
    mutations = {
        'wrong-source': ('read_byte(ctx, p + 3u)', 'read_byte(ctx, p + 5u)'),
        'inverted-branch': ('old != a ||', 'old == a ||'),
        'wrong-write': ('write_byte(ctx, gp + 233u, b);', 'write_byte(ctx, gp + 233u, a);'),
        'missing-tail': ('return 0x13c4eu;', 'return 0u;'),
    }
    for old, _ in mutations.values():
        need(source.count(old) == 1, 'mutation anchor')
    with tempfile.TemporaryDirectory(prefix='tsl9-d14a-mutants-') as tmp:
        root = Path(tmp)
        for language, standard in (('c', 'c11'), ('c++', 'c++17')):
            for name in ('positive', *mutations):
                unit, obj, dll = root/'unit.c', root/'unit.obj', root/'unit.dll'
                text = source if name == 'positive' else source.replace(*mutations[name])
                unit.write_text(text, encoding='utf-8')
                subprocess.run([str(args.clang), '--target=x86_64-pc-windows-msvc', '-c', '-x', language,
                                '-std='+standard, str(unit), '-o', str(obj)], check=True)
                subprocess.run([str(args.linker), '/nologo', '/dll', '/noentry', '/nodefaultlib',
                                str(obj), '/out:'+str(dll)], check=True, capture_output=True)
                optimize = ['-' + 'O'*sys.flags.optimize] if sys.flags.optimize else []
                result = subprocess.run([sys.executable, *optimize, str(ROOT/'d14a_model_differential.py'),
                                         '--worker', str(dll)], capture_output=True, text=True)
                if name == 'positive':
                    need(result.returncode == 0 and 'PASS: 4096' in result.stdout, 'positive control failed')
                else:
                    need(result.returncode != 0 and 'ValueError: case ' in result.stderr,
                         'mutant not rejected by differential comparison: '+name)
                print(standard, name, 'passed' if name == 'positive' else 'rejected', flush=True)


if __name__ == '__main__':
    main()
