#!/usr/bin/env python3
"""Compile/read/link only. No target execution, emulation, network or hardware."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = json.loads((HERE/'spec.json').read_bytes())
P = json.loads((HERE/'proof-spec.json').read_bytes())


def need(ok, text):
    if not ok:
        raise ValueError(text)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)+'\n').encode()


def portable(value, llvm):
    pairs = [(llvm.parent/'lib/clang/18', '${CLANG_RESOURCE}'), (llvm, '${LLVM_BIN}'), (ROOT, '${PROJECT_ROOT}')]
    if isinstance(value, str):
        for path, token in pairs:
            for prefix in (str(path), path.as_posix()):
                value = value.replace(prefix, token)
        return value
    if isinstance(value, list):
        return [portable(x, llvm) for x in value]
    if isinstance(value, dict):
        return {portable(k, llvm): portable(v, llvm) for k, v in value.items()}
    return value


def parent(mode):
    return ROOT/'experiments/tsl9-gp-word-toggle/build/formal-v1'/mode/'UNRESOLVED-FULL-PLUS-LEAF.o'


def inputs(llvm, mode):
    paths = [HERE/n for n in ('build.py', 'verify.py', 'spec.json', 'proof-spec.json', 'nominal.ld', 'joined.ld')]
    paths += [ROOT/S[k] for k in ('source', 'curated', 'reader', 'firmware')]
    paths += [ROOT/P['previous_checker'], parent(mode), parent(mode).parent/'verification-v3.json',
              ROOT/P['curation_root']/'verification.json', llvm.parent/'lib/clang/18/include/stdint.h']
    paths += [llvm/n for n in S['tools']]
    for name in ('unit.o', 'unit.d', 'compile.log'):
        paths.append(ROOT/P['curation_root']/'record-program'/mode/'curated'/name)
    return {str(p): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(set(paths))}


def recipes(llvm, folder, mode):
    compiler = str(llvm/'clang.exe')
    reader = str(llvm/'llvm-objdump.exe')
    linker = str(llvm/'ld.lld.exe')
    source = str(ROOT/S['curated'])
    return [
        ('compile', [compiler]+S['flags'][mode]+['-c', '-MD', '-MF', str(folder/'native.d'), '-MT', 'native.o', source, '-o', str(folder/'native.o')]),
        ('IR', [compiler]+S['flags'][mode]+['-S', '-emit-llvm', source, '-o', str(folder/'native.ll')]),
        ('native-read', [reader, '-dr', str(folder/'native.o')]),
        ('nominal-link', [linker, '--no-relax', '-T', str(HERE/'nominal.ld'), str(folder/'native.o'), '-o', str(folder/'PROGRAM-ONLY-NOT-FIRMWARE.elf')]),
        ('nominal-read', [reader, '-dr', str(folder/'PROGRAM-ONLY-NOT-FIRMWARE.elf')]),
        ('joined-link', [linker, '-r', '--no-relax', '-T', str(HERE/'joined.ld'), str(parent(mode)), str(folder/'native.o'), '-o', str(folder/'UNRESOLVED-PROGRAM-GRAPH.o')]),
        ('joined-read', [reader, '-dr', str(folder/'UNRESOLVED-PROGRAM-GRAPH.o')])]


def build(llvm, output):
    need(not output.exists() and output.is_relative_to(HERE/'build'), 'Create-only local output')
    for name, pin in S['tools'].items():
        need(sha(llvm/name) == pin, 'Pinned existing tool '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h') == S['stdint_sha256'], 'Pinned stdint')
    for key in ('source', 'curated'):
        need(sha(ROOT/S[key]) == S['source_sha256'], 'Exact current source '+key)
    need(sha(ROOT/P['previous_checker']) == P['previous_checker_sha256'], 'Frozen previous proof')
    for mode in ('c', 'cpp'):
        folder = output/mode
        folder.mkdir(parents=True)
        need(sha(parent(mode)) == P['parent_component_sha256'], 'Genuine parent object')
        before = inputs(llvm, mode)
        commands = []
        for label, argv in recipes(llvm, folder, mode):
            result = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            (folder/(label+'.log')).write_bytes(result.stdout)
            commands.append(dict(label=label, argv=argv, exit=result.returncode, log_sha256=hashlib.sha256(result.stdout).hexdigest()))
            need(result.returncode == 0, 'Failed command; inspect local log '+label)
        need(before == inputs(llvm, mode), 'Producer inputs unchanged during actual commands')
        record = dict(schema='TSL9-record-program-build-v1', mode=mode, inputs=before, commands=commands,
                      artifacts={p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()},
                      target_executed=False, ISA_emulated=False, hardware_accessed=False, network=False,
                      firmware_BIN_generated=False, firmware_ready=False)
        (folder/'measurement.json').write_bytes(encode(portable(record, llvm)))
    print(json.dumps(dict(built=True, commands_per_language=7, modes=['c', 'cpp'], target_executed=False, firmware_ready=False)))


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
