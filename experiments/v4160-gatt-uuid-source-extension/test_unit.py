"""Compile real source mutations in a temporary directory; never run target code."""
import argparse
import json
import tempfile
from pathlib import Path

import verify
from elf_reader import ELF


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-dir', type=Path, required=True)
    args = parser.parse_args()
    source = (verify.root / 'src/native/receive/gatt_write_uuid.c').read_text('utf-8')
    mutations = {
        'wrong_value': source.replace('0xfff1', '0xfff0'),
        'wrong_width': source.replace('uint16_t', 'uint32_t'),
        'wrong_owner': source.replace('tsl9_gatt_write_UUID_1ab44 =', 'unexpected_UUID ='),
        'wrong_section': source.replace('.rodata.tsl9_gatt_write_UUID_1ab44', '.rodata.unexpected'),
        'wrong_alignment': source.replace('aligned(2)', 'aligned(4)'),
    }
    results = []
    with tempfile.TemporaryDirectory(prefix='tsl9-uuid-mutations-') as folder:
        base = Path(folder)
        for mode, language, standard in [('c', 'c', 'c11'), ('cpp', 'c++', 'c++17')]:
            for name, text in [('original', source)] + list(mutations.items()):
                unit, obj = base / (name + '.c'), base / (name + '.o')
                unit.write_text(text, encoding='utf-8')
                verify.run([verify.tool(args.tool_dir, 'clang'), '-target', 'riscv32',
                            '-march=rv32imac_zicsr', '-mabi=ilp32', '-ffreestanding',
                            '-Oz', '-x', language, '-std=' + standard, '-c', unit, '-o', obj])
                try:
                    verify.validate_unit(obj, ELF)
                    accepted = True
                except ValueError:
                    accepted = False
                verify.need(accepted == (name == 'original'), 'unit mutation detection: ' + name)
                results.append({'mode': mode, 'case': name, 'accepted': accepted})
    print(json.dumps({'passed': True, 'compiled_cases': len(results),
                      'mutations_rejected': sum(not r['accepted'] for r in results),
                      'target_executed': False, 'cases': results}))


if __name__ == '__main__':
    main()
