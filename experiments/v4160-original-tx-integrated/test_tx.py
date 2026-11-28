"""Compile real TX instruction mutations and test relocation/entry controls."""
import argparse
import copy
import json
from pathlib import Path
import runpy
import tempfile

ROOT = Path(__file__).resolve().parents[2]
LIB = runpy.run_path(str(ROOT / 'src/native/tx_candidate/verify-original.py'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-dir', type=Path, required=True)
    args = parser.parse_args()
    tools = {n: next(p for p in [args.tool_dir / (n + '.exe'), args.tool_dir / n] if p.is_file()) for n in ('clang', 'ld.lld')}
    need, run, E = LIB['need'], LIB['run'], LIB['ELF']
    source = (ROOT / 'src/native/tx_candidate/original_tx.c').read_text('utf-8')
    mutations = {'guard_limit': source.replace('zero, 1039', 'zero, 1038'),
                 'guard_predicate': source.replace('b 0x63, 6, a5, a3', 'b 0x63, 7, a5, a3'),
                 'payload_offset': source.replace('sb a0, 5(a6)', 'sb a0, 6(a6)'),
                 'return_frame': source.replace('c.addi16sp sp, 32', 'c.addi16sp sp, 16', 1)}
    cases = []
    with tempfile.TemporaryDirectory(prefix='tsl9-original-tx-controls-') as temp:
        d = Path(temp)
        script = d / 'tx.ld'
        script.write_text('SECTIONS { .text.tsl9_tx_composite 0x8a56 : { *(.text.tsl9_tx_composite) } }\n', encoding='utf-8')
        for mode in ('c', 'cpp'):
            for name, text in [('original', source)] + list(mutations.items()):
                src, obj, elf = d / (name + '.c'), d / (name + '.o'), d / (name + '.elf')
                src.write_text(text, encoding='utf-8')
                run([tools['clang'], *LIB['flags'](mode), '-c', src, '-o', obj])
                LIB['check_unit'](E(obj))
                base = [tools['ld.lld'], '--no-undefined', '--no-relax', '-T', script, obj]
                run([*base, '--defsym=' + LIB['RAM'] + '=0x2000b18c', '-o', elf])
                try:
                    LIB['linked_bytes'](E(elf))
                    accepted = True
                except ValueError as error:
                    need(str(error) == 'linked original TX byte identity', 'specific byte-comparison rejection')
                    accepted = False
                need(accepted == (name == 'original'), 'compiled instruction mutation: ' + name)
                cases.append({'mode': mode, 'case': name, 'accepted': accepted})
                if name == 'original':
                    unit = E(obj)
                    for control in ('RAM_relocation_type', 'public_entry_ABS'):
                        altered = copy.deepcopy(unit)
                        if control == 'RAM_relocation_type':
                            altered.relocations[0]['type'] = 24
                        else:
                            next(s for s in altered.symbols if s['name'] == '__tsl9v4160_call_8a56')['index'] = 0xfff1
                        try:
                            LIB['check_unit'](altered)
                        except ValueError:
                            pass
                        else:
                            raise ValueError('metadata mutation accepted: ' + control)
                    wrong = run([*base, '--defsym=unrelated_RAM=0x2000b18c', '-o', d / 'wrong-name.elf'], success=False)
                    need(wrong.returncode != 0 and ('undefined symbol: ' + LIB['RAM']) in wrong.stderr, 'wrong-named RAM cannot satisfy the real provider')
    print(json.dumps({'passed': True, 'compiled_cases': len(cases), 'compiled_mutations_rejected': 8,
                      'metadata_mutations_rejected': 4, 'wrong_named_RAM_links_rejected': 2,
                      'cases': cases, 'target_executed': False}))


if __name__ == '__main__':
    main()
