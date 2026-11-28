"""Compile source mutations and check the actual defaults OBJECT contract."""
import argparse
import json
from pathlib import Path
import runpy
import tempfile

import verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-dir', type=Path, required=True)
    args = parser.parse_args()
    clang = next(p for p in [args.tool_dir / 'clang.exe', args.tool_dir / 'clang'] if p.is_file())
    spec = json.loads((verify.HERE / 'inputs.json').read_bytes())
    verify.need(verify.sha(clang) == spec['tools']['clang'], 'pinned compiler')
    ELF = runpy.run_path(str(verify.HERE / 'elf_reader.py'))['ELF']
    source = (verify.HERE / 'defaults.c').read_text('utf-8')
    mutations = {'wrong_byte': source.replace('0x34', '0x35'),
                 'extra_NUL': source.replace('[4]', '[5]'),
                 'wrong_owner': source.replace(verify.NAME, 'unrelated_defaults'),
                 'writable': source.replace('const unsigned char', 'unsigned char'),
                 'changed_alignment': source.replace('aligned(1)', 'aligned(2)')}
    results = []
    with tempfile.TemporaryDirectory(prefix='tsl9-defaults-unit-') as directory:
        folder = Path(directory)
        for mode, language, standard in [('c', 'c', 'c11'), ('cpp', 'c++', 'c++17')]:
            for name, text in [('original', source)] + list(mutations.items()):
                unit, obj = folder / (name + '.c'), folder / (name + '.o')
                unit.write_text(text, encoding='utf-8')
                verify.run([clang, '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32',
                            '-ffreestanding', '-Oz', '-x', language, '-std=' + standard, '-c', unit, '-o', obj])
                try:
                    verify.validate_unit(obj, ELF, verify.facts)
                    accepted = True
                except ValueError:
                    accepted = False
                verify.need(accepted == (name == 'original'), 'mutation check: ' + name)
                results.append({'mode': mode, 'case': name, 'accepted': accepted})
    print(json.dumps({'passed': True, 'compiled_cases': len(results),
                      'source_mutations_rejected': sum(not r['accepted'] for r in results),
                      'cases': results, 'target_executed': False}))


if __name__ == '__main__':
    main()
