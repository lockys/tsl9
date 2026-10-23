#!/usr/bin/env python3
"""Compile/link data only. Never execute firmware, emulate it, or access hardware."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = json.loads((HERE/'spec.json').read_bytes())


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)+'\n').encode()


def portable(value, llvm):
    pairs = [(llvm.parent/'lib/clang/18', '${CLANG_RESOURCE}'),
             (llvm, '${LLVM_BIN}'), (ROOT, '${PROJECT_ROOT}')]
    if isinstance(value, str):
        for path, token in pairs:
            for prefix in (str(path), path.as_posix()):
                value = value.replace(prefix, token)
        return value
    if isinstance(value, list):
        return [portable(v, llvm) for v in value]
    if isinstance(value, dict):
        return {portable(k, llvm): portable(v, llvm) for k, v in value.items()}
    return value


def inputs(llvm, mode):
    paths = [Path(__file__), HERE/'spec.json', HERE/'leaf.ld', HERE/'joined.ld',
             ROOT/SPEC['source'], ROOT/SPEC['curated'], ROOT/SPEC['reader'],
             ROOT/SPEC['firmware'], ROOT/SPEC['curation_root']/'verification.json',
             HERE/'frozen/manifest-before-toggle.json',
             ROOT/'experiments/tsl9-receive-transmit-chain/build/integration-v2'/mode/'UNRESOLVED-FULL-COMPONENT.o',
             llvm.parent/'lib/clang/18/include/stdint.h']
    paths += [llvm/n for n in SPEC['tools']]
    for entry in SPEC['manifest_scope']['files']:
        paths += [ROOT/entry['origin'], ROOT/entry['destination']]
    return {str(p): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(set(paths))}


def build(llvm, output):
    need(not output.exists(), 'Create-only output directory')
    need(output.is_relative_to(HERE/'build'), 'Output stays in this experiment build directory')
    for name, expected in SPEC['tools'].items():
        need(sha(llvm/name) == expected, 'Pinned local tool '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h') == SPEC['stdint_sha256'], 'Pinned stdint')
    for key in ('source', 'curated'):
        need(sha(ROOT/SPEC[key]) == SPEC['source_sha256'], 'Pinned source '+key)
    for mode in ('c', 'cpp'):
        folder = output/mode
        folder.mkdir(parents=True)
        commands = []
        parent = ROOT/'experiments/tsl9-receive-transmit-chain/build/integration-v2'/mode/'UNRESOLVED-FULL-COMPONENT.o'
        need(sha(parent) == SPEC['parent_component_sha256'], 'Pinned genuine parent component')
        before = inputs(llvm, mode)
        clang = str(llvm/'clang.exe')
        flags = SPEC['unit_flags']['gp-word-toggle'][mode]
        source = str(ROOT/SPEC['curated'])

        def run(label, argv):
            result = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            (folder/(label+'.log')).write_bytes(result.stdout)
            commands.append(dict(label=label, argv=argv, exit=result.returncode,
                                 log_sha256=hashlib.sha256(result.stdout).hexdigest()))
            need(result.returncode == 0, 'Command failed; inspect local log '+label)

        run('compile', [clang]+flags+['-c', '-MD', '-MF', str(folder/'native.d'), '-MT', 'native.o', source, '-o', str(folder/'native.o')])
        run('IR', [clang]+flags+['-S', '-emit-llvm', source, '-o', str(folder/'native.ll')])
        run('native-read', [str(llvm/'llvm-objdump.exe'), '-dr', str(folder/'native.o')])
        run('leaf-link', [str(llvm/'ld.lld.exe'), '--no-relax', '-T', str(HERE/'leaf.ld'), str(folder/'native.o'), '-o', str(folder/'LEAF-ONLY-NOT-FIRMWARE.elf')])
        run('leaf-read', [str(llvm/'llvm-objdump.exe'), '-dr', str(folder/'LEAF-ONLY-NOT-FIRMWARE.elf')])
        run('joined-link', [str(llvm/'ld.lld.exe'), '-r', '--no-relax', '-T', str(HERE/'joined.ld'), str(parent), str(folder/'native.o'), '-o', str(folder/'UNRESOLVED-FULL-PLUS-LEAF.o')])
        run('joined-read', [str(llvm/'llvm-objdump.exe'), '-dr', str(folder/'UNRESOLVED-FULL-PLUS-LEAF.o')])
        need(before == inputs(llvm, mode), 'Producer inputs unchanged during commands')
        record = dict(schema='TSL9-gp-word-toggle-build-v1', mode=mode,
                      commands=commands, inputs=before,
                      artifacts={p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()},
                      target_executed=False, ISA_emulated=False, hardware_accessed=False,
                      network=False, firmware_BIN_generated=False, firmware_ready=False)
        (folder/'measurement.json').write_bytes(encode(portable(record, llvm)))
    print(json.dumps(dict(built=True, commands_per_language=7, modes=['c', 'cpp'],
                          output=output.relative_to(ROOT).as_posix(), target_executed=False, firmware_ready=False)))


if __name__ == '__main__':
    try:
        p = argparse.ArgumentParser(description=__doc__)
        p.add_argument('--tool-dir', type=Path, required=True)
        p.add_argument('--output', type=Path, required=True)
        a = p.parse_args()
        build(a.tool_dir.resolve(), a.output.resolve())
    except (ValueError, OSError) as error:
        print('FAIL: '+str(error), file=sys.stderr)
        sys.exit(1)
