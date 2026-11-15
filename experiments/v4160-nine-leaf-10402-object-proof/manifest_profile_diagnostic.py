#!/usr/bin/env python3
"""Offline 10402 compilation under the current manifest profile and a proposed override.

This does not alter the manifest or assert integration. GP and witness are
synthetic linker assumptions; the manifest and local tools are not trust roots.
"""
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import compile_diagnostic as diag
import probe as source_check


def main():
    result = {'passed': False, 'cases': []}
    try:
        raw = (diag.ROOT / 'src/source-build-manifest.json').read_bytes()
        manifest = json.loads(raw)
        profile = manifest['code_profiles']['queue-consumer-a0-a5']
        prep, pure = source_check.PREP.read_bytes(), source_check.PURE.read_bytes()
        source_check.candidate_contract(prep, pure)
        reference = source_check.BIN.read_bytes()
        if len(reference) != 76800 or hashlib.sha256(reference).hexdigest() != source_check.PINS['reference'][1]:
            raise ValueError('reference mismatch')
        original = reference[0x10402 - 0x8000:0x10408 - 0x8000]
        if original.hex() != '03d501058280':
            raise ValueError('reference leaf mismatch')
        leaf = ast.literal_eval(next(n.value for n in ast.parse(prep).body if isinstance(n, ast.Assign)
                                and any(isinstance(t, ast.Name) and t.id == 'LEAF' for t in n.targets)))
        clang, linker, objcopy = (diag.TOOLS / n for n in ('clang.exe', 'ld.lld.exe', 'llvm-objcopy.exe'))
        result['manifest_sha256'] = hashlib.sha256(raw).hexdigest()
        result['tool_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (clang, linker, objcopy)}
        with tempfile.TemporaryDirectory(prefix='tsl9-10402-profile-') as temp:
            d = Path(temp)
            source, obj, elf, binary, layout = (d / n for n in ('leaf.c', 'leaf.o', 'leaf.elf', 'leaf.bin', 'layout.ld'))
            source.write_bytes(leaf)
            layout.write_text('__global_pointer$ = 0x20004000;\n'
                              'tsl9_witness_10402 = 0x20004050;\n'
                              'SECTIONS { .leaf 0x10402 : { *(.text.tsl9_state_leaf_entry_10402) } }\n')
            for language in ('c', 'cpp'):
                for override in (False, True):
                    flags = profile[language] + (['-fno-pic', '-Oz', '-mrelax'] if override else [])
                    compile_result = subprocess.run([str(clang), *flags, '-c', str(source), '-o', str(obj)], capture_output=True, text=True)
                    case = {'language': language, 'proposed_suffix': override, 'flags': flags,
                            'compile_returncode': compile_result.returncode, 'compile_stderr': compile_result.stderr}
                    result['cases'].append(case)
                    if compile_result.returncode:
                        continue
                    link = subprocess.run([str(linker), '--relax', '--relax-gp', '-T', str(layout), '-o', str(elf), str(obj)], capture_output=True, text=True)
                    case['link_returncode'] = link.returncode
                    case['link_stderr'] = link.stderr
                    if link.returncode:
                        continue
                    copy = subprocess.run([str(objcopy), '-O', 'binary', '--only-section=.leaf', str(elf), str(binary)], capture_output=True, text=True)
                    case['objcopy_returncode'] = copy.returncode
                    if copy.returncode:
                        case['objcopy_stderr'] = copy.stderr
                    else:
                        case['linked_hex'] = binary.read_bytes().hex()
                        case['matches_original_leaf'] = case['linked_hex'] == original.hex()
        result['reason'] = 'Diagnostic only: inherited parent profile and proposed suffix do not establish the official nine-leaf build or actual GP.'
    except (OSError, ValueError, KeyError, SyntaxError, StopIteration) as exc:
        result['reason'] = 'diagnostic failed: ' + str(exc)
    print(json.dumps(result, indent=2))
    return 1


if __name__ == '__main__':
    sys.exit(main())
