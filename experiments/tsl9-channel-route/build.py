#!/usr/bin/env python3
"""Compile LLVM IR and link genuine source objects; never execute target code."""
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


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)+'\n').encode()


def portable(value, llvm):
    pairs = [(llvm.parent/'lib/clang/18', '$'+'{CLANG_RESOURCE}'), (llvm, '$'+'{LLVM_BIN}'), (ROOT, '$'+'{PROJECT_ROOT}')]
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
    return ROOT/'experiments/tsl9-record-program/build/formal-v1'/mode/'UNRESOLVED-PROGRAM-GRAPH.o'


def obj(unit, mode):
    return ROOT/S['curation_root']/unit['name']/mode/'curated/unit.o'


def inputs(llvm, mode):
    paths = [HERE/n for n in ('spec.json', 'build.py', 'nominal.ld', 'joined.ld')]
    paths += [ROOT/S[k] for k in ('firmware', 'reader', 'parent_checker', 'curation_checker')]
    paths += [parent(mode), parent(mode).parent/'verification-v2.json',
              ROOT/S['curation_root']/'verification.json', ROOT/'src/source-manifest.json',
              llvm.parent/'lib/clang/18/include/stdint.h']
    for u in S['units']:
        paths += [ROOT/u['source'], ROOT/u['origin'], obj(u, mode),
                  obj(u, mode).parent/'unit.d', obj(u, mode).parent/'compile.log']
    paths += [llvm/n for n in S['tools']]
    return {str(p): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(set(paths))}


def recipes(llvm, output, mode):
    C = runpy.run_path(str(ROOT/S['curation_checker']))
    commands = []
    for u in S['units']:
        commands.append(('IR-'+u['name'], [str(llvm/'clang.exe')]+C['flags'](u, mode)+[
            '-S', '-emit-llvm', str(ROOT/u['source']), '-o', str(output/(u['name']+'.ll'))]))
    commands += [
        ('nominal-link', [str(llvm/'ld.lld.exe'), '--no-relax', '-T', str(HERE/'nominal.ld')]+
         [str(obj(u, mode)) for u in S['units']]+['-o', str(output/'ORIGINAL-PC-COMPONENT-NOT-FIRMWARE.elf')]),
        ('nominal-read', [str(llvm/'llvm-objdump.exe'), '-dr', '-t', '-h', str(output/'ORIGINAL-PC-COMPONENT-NOT-FIRMWARE.elf')]),
        ('joined-link', [str(llvm/'ld.lld.exe'), '-r', '--no-relax', '-T', str(HERE/'joined.ld'), str(parent(mode))]+
         [str(obj(u, mode)) for u in S['units'] if u['name'] in S['new_units']]+
         ['-o', str(output/'UNRESOLVED-CHANNEL-GRAPH.o')]),
        ('joined-read', [str(llvm/'llvm-objdump.exe'), '-dr', '-t', '-h', str(output/'UNRESOLVED-CHANNEL-GRAPH.o')])]
    return commands


def build(llvm, output):
    need(not output.exists() and output.is_relative_to(HERE/'build'), 'Create-only local output')
    for n, pin in S['tools'].items():
        need(sha(llvm/n) == pin, 'Pinned existing tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h') == S['stdint_sha256'], 'Pinned compiler header')
    for k in ('reader', 'parent_checker', 'curation_checker', 'firmware'):
        need(sha(ROOT/S[k]) == S[k+'_sha256'], 'Pinned '+k)
    need(sha(ROOT/S['curation_root']/'verification.json') == S['curation_receipt_sha256'], 'Current source curation receipt')
    for mode in ('c', 'cpp'):
        need(sha(parent(mode)) == S['parent_object_sha256'], 'Genuine2250B parent')
        folder = output/mode
        folder.mkdir(parents=True)
        before = inputs(llvm, mode)
        commands = []
        for label, argv in recipes(llvm, folder, mode):
            p = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (folder/(label+'.log')).write_bytes(p.stdout)
            commands.append(dict(label=label, argv=argv, exit=p.returncode, log_sha256=hashlib.sha256(p.stdout).hexdigest()))
            need(p.returncode == 0, 'Failed actual command '+label+'; inspect retained local log')
        need(before == inputs(llvm, mode), 'Inputs unchanged during actual production')
        record = dict(schema='TSL9-channel-filter-build-v1', mode=mode, inputs=before, commands=commands,
                      artifacts={p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()},
                      target_executed=False, HOST_model_executed=False, ISA_emulated=False, network=False,
                      firmware_BIN_generated=False, firmware_ready=False)
        (folder/'measurement.json').write_bytes(encode(portable(record, llvm)))
    print(json.dumps(dict(built=True, languages=['c', 'cpp'], commands_per_language=13, firmware_ready=False)))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    build(a.tool_dir.resolve(), a.output.resolve())
