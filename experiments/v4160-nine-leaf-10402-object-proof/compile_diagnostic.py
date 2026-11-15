#!/usr/bin/env python3
"""Compile the pinned generated 10402 leaf in isolation; not integration proof.

Uses local toolchain/filesystem as trusted inputs. The diagnostic GP and witness
addresses are assumptions, not live register or memory evidence. Leaves the
existing fail-closed nine-leaf gate unchanged and exits 1 even on success.
"""
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import probe as source_check

ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(r'C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin')


def command(args, success=True):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if (p.returncode == 0) != success:
        raise ValueError('unexpected command status: ' + repr(args) + '\n' + p.stdout + p.stderr)
    return p.stdout + p.stderr


def main():
    result = {'passed': False, 'isolated_checks_passed': False}
    try:
        prep = source_check.PREP.read_bytes()
        pure = source_check.PURE.read_bytes()
        source_check.candidate_contract(prep, pure)
        tree = ast.parse(prep)
        leaf = ast.literal_eval(next(x.value for x in tree.body if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'LEAF' for t in x.targets)))
        reference = source_check.BIN.read_bytes()
        if hashlib.sha256(reference).hexdigest() != source_check.PINS['reference'][1] or len(reference) != 76800:
            raise ValueError('reference mismatch')
        spec = importlib.util.spec_from_file_location('isolated_parser', ROOT / 'experiments/v4160-10402-pure-c/probe.py')
        parser = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parser)
        clang, ld, readelf = [TOOLS / (name + '.exe') for name in ('clang', 'ld.lld', 'llvm-readelf')]
        cases = []
        with tempfile.TemporaryDirectory(prefix='tsl9-10402-object-') as tmp:
            d = Path(tmp)
            source = d / 'leaf.c'
            source.write_bytes(leaf)
            for lang, std in (('c', 'c11'), ('c++', 'c++17')):
                obj = d / 'leaf.o'
                command([clang, '--target=riscv32-unknown-elf', '-x', lang, '-std=' + std,
                         '-march=rv32imac_zicsr', '-mabi=ilp32', '-ffreestanding',
                         '-fno-stack-protector', '-Oz', '-fno-pic', '-msmall-data-limit=8',
                         '-c', source, '-o', obj])
                info = command([readelf, '-aW', obj])
                for text in ('tsl9_state_leaf_entry_10402', 'tsl9_witness_10402', 'R_RISCV_HI20', 'R_RISCV_LO12_I', 'R_RISCV_RELAX'):
                    if text not in info:
                        raise ValueError('missing object evidence: ' + text)
                for name, gp, witness, relax, expected in (
                    ('relaxed', 0x20004000, 0x20004050, True, '03d501058280'),
                    ('witness_shift', 0x20004000, 0x20004052, True, '03d521058280'),
                    ('no_relax', 0x20004000, 0x20004050, False, '37450020035505058280'),
                    ('compile_no_relax', 0x20004000, 0x20004050, True, '37450020035505058280'),
                    ('missing', 0x20004000, None, True, None)):
                    case_obj = obj
                    if name == 'compile_no_relax':
                        case_obj = d / 'no-relax.o'
                        command([clang, '--target=riscv32-unknown-elf', '-x', lang, '-std=' + std,
                                 '-march=rv32imac_zicsr', '-mabi=ilp32', '-ffreestanding',
                                 '-fno-stack-protector', '-Oz', '-fno-pic', '-msmall-data-limit=8',
                                 '-mno-relax', '-c', source, '-o', case_obj])
                    script = d / 'layout.ld'
                    script.write_text(f'__global_pointer$ = 0x{gp:x};\n' + (f'tsl9_witness_10402 = 0x{witness:x};\n' if witness is not None else '') + 'SECTIONS { .leaf 0x10402 : { *(.text.tsl9_state_leaf_entry_10402) } }\n')
                    elf = d / 'leaf.elf'
                    cmd = [ld, '--relax' if relax else '--no-relax', '--relax-gp' if relax else '--no-relax-gp', '-T', script, '-o', elf, case_obj]
                    log = command(cmd, success=witness is not None)
                    if witness is None:
                        if 'undefined hidden symbol: tsl9_witness_10402' not in log:
                            raise ValueError('wrong missing witness failure: ' + log)
                        cases.append({'language': std, 'case': name, 'expected_failure': True})
                        continue
                    _, payload = parser.section(elf.read_bytes())
                    if payload.hex() != expected:
                        raise ValueError(f'{std}/{name} unexpected bytes {payload.hex()}')
                    cases.append({'language': std, 'case': name, 'bytes': payload.hex()})
        result.update(isolated_checks_passed=True, leaf_sha256=hashlib.sha256(leaf).hexdigest(), cases=cases,
                      reason='Diagnostic placement assumes GP and witness; not nine-leaf integration or runtime proof.')
    except (OSError, ValueError, SyntaxError, StopIteration) as exc:
        result['reason'] = str(exc)
    print(json.dumps(result, indent=2))
    return 1


if __name__ == '__main__':
    sys.exit(main())
