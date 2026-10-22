#!/usr/bin/env python3
"""Check curated source provenance; optionally compile/read objects, never execute them."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'src/source-manifest.json'
PARSER = ROOT / 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata():
    manifest = json.loads(MANIFEST.read_bytes())
    need(manifest['schema'] == 'TSL9-curated-source-v1', 'Unknown source manifest')
    paths = [x['destination'] for x in manifest['files']]
    need(len(paths) == len(set(paths)), 'Unique destination paths')
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'src').rglob('*') if p.is_file() and p.suffix in {'.c', '.h', '.cc', '.cpp', '.hpp'}}
    need(set(paths) == actual, 'Complete curated C/C++ inventory')
    for item in manifest['files']:
        origin, dest = ROOT / item['origin'], ROOT / item['destination']
        need(origin.resolve().is_relative_to(ROOT / 'experiments') and dest.resolve().is_relative_to(ROOT / 'src'), 'Bounded source paths')
        need(sha(origin) == item['origin_sha256'] and sha(dest) == item['sha256'], 'Source hash: ' + item['destination'])
        expected = origin.read_text(encoding='utf-8').replace('\r\n', '\n').rstrip() + '\n'
        for old, new in item['replacements']:
            need(expected.count(old) == 1, 'Unique recorded source adaptation')
            expected = expected.replace(old, new)
        need(dest.read_bytes() == expected.encode('utf-8'), 'Exact recorded adaptations: ' + item['destination'])
    for unit in manifest['native_units']:
        need(sha(ROOT / unit['origin_unit']) == unit['origin_unit_sha256'], 'Pinned original translation unit')
    need(sha(PARSER) == PARSER_SHA, 'Unchanged separate ELF reader')
    return manifest


def flags(unit, mode):
    kind = unit['profile']
    clock = kind in ('clock-query', 'clock-fields')
    irq = kind in ('irq-bank', 'delay-bank')
    result = ['--target=riscv32-unknown-elf', '-march=' + ('rv32imac' if clock else 'rv32imac_zicsr' if irq else 'rv32imac_zicsr_zifencei'),
              '-mabi=ilp32', '-Os' if clock else '-Oz']
    if not clock:
        result += ['-mllvm', '-enable-machine-outliner=never']
    result += ['-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
               '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror',
               '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17']
    if mode == 'cpp' and not (clock or irq):
        result += ['-fno-exceptions']
    if clock or irq:
        allowed = {10, 12, 13, 14, 15} if kind == 'delay-bank' else {13, 14, 15} if kind == 'clock-query' else {14, 15} if kind == 'clock-fields' else {10, 11, 14, 15}
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in allowed]
    elif kind == 'boot-clock':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {2, 12, 13, 14, 15}]
    elif kind == 'runtime-reset':
        result += ['-ffixed-x' + str(n) for n in range(1, 32) if n not in {2, 5, 10, 11, 12}]
    elif kind == 'adc-bank':
        result += ['-ffixed-x' + str(n) for n in range(5, 32) if n not in range(10, 17)]
    return result


def command(tools, unit, mode, variant, folder):
    source = ROOT / unit['origin_unit' if variant == 'origin' else 'curated_unit']
    return [tools['clang'], *flags(unit, mode), '-c', '-MD', '-MF', folder / 'unit.d', '-MT', 'unit.o', source, '-o', folder / 'unit.o']


def facts(path, reader, allow_data=False):
    elf = reader(path)
    need(elf.kind == 1 and elf.flags == 1, 'Actual RV32 RVC relocatable object')
    funcs = sorted([dict(name=s['name'], binding=s['info'] >> 4, bytes=s['size'], code_sha256=hashlib.sha256(elf.function_bytes(s)).hexdigest())
                    for s in elf.symbols if s['info'] & 15 == 2 and s['size']], key=lambda x: x['name'])
    alloc = [dict(name=s['name'], bytes=s['size'], flags=s['flags'], type=s['type'], sha256=None if s['type']==8 else hashlib.sha256(elf.data(s)).hexdigest())
             for s in elf.sections if s['flags'] & 2 and s['size']]
    reloc = [dict(owner=x['owner'], offset=x['offset'], type=x['type'], addend=x['addend'], symbol=x['symbol']['name']) for x in elf.relocations]
    und = sorted({s['name'] for s in elf.symbols if s['name'] and s['index'] == 0 and s['info'] >> 4 in (1, 2)})
    absolute = sorted({s['name'] for s in elf.symbols if s['index'] == 0xfff1 and s['info'] >> 4 in (1, 2)})
    need((funcs or (allow_data and alloc and not und and not reloc and all(s['flags']==2 or s['type']==8 for s in alloc))) and not absolute,
         'Genuine functions or explicitly admitted data unit without global ABS providers')
    return dict(functions=funcs, allocated_sections=alloc, allocated_bytes=sum(x['bytes'] for x in alloc), relocations=reloc, UND=und, global_ABS=absolute)


def dependencies(folder, variant, resource):
    text = (folder / 'unit.d').read_text(encoding='utf-8').replace('\\\n', ' ')
    target, separator, tail = text.partition(':')
    need(separator and target == 'unit.o', 'Compiler dependency target')
    paths = {Path(re.sub(r'\\(.)', r'\1', token)).resolve() for token in re.findall(r'(?:\\.|[^\s])+', tail)}
    allowed = ROOT / ('src' if variant == 'curated' else 'experiments')
    need(paths and all(p.is_relative_to(allowed) or p.is_relative_to(resource) for p in paths), 'Active include closure stays in selected source tree and compiler resources')
    return {str(p): sha(p) for p in sorted(paths)}


def inventory(base):
    return {p.relative_to(base).as_posix(): sha(p) for p in base.rglob('*') if p.is_file() and p != base / 'verification.json'}


def inputs(manifest):
    paths = {Path(__file__).resolve(), MANIFEST, PARSER}
    for item in manifest['files']:
        paths.update([ROOT / item['origin'], ROOT / item['destination']])
    for unit in manifest['native_units']:
        paths.add(ROOT / unit['origin_unit'])
    return {str(p): sha(p) for p in sorted(paths)}


def audit(base, record, manifest):
    need(record['schema'] == 'TSL9-curated-source-object-comparison-v1', 'Known build schema')
    need(base.is_relative_to(ROOT / 'build/curated-source') and record['inputs'] == inputs(manifest), 'Owned build and exact unchanged inputs')
    tools = {n: Path(v['path']) for n, v in record['tools'].items()}
    need(set(tools) == {'clang'} and all(sha(tools[n]) == record['tools'][n]['sha256'] for n in tools), 'Actual compiler unchanged')
    resource = Path(record['resource_dir'])
    need(sha(base / 'resource.log') == record['resource_log_sha256'], 'Retained compiler resource output')
    need(Path((base / 'resource.log').read_text().strip()).resolve() == resource, 'Actual compiler resource path')
    reader = runpy.run_path(str(PARSER))['ELF']
    results, expected_jobs = [], []
    for unit in manifest['native_units']:
        for mode in ('c', 'cpp'):
            pair = []
            for variant in ('origin', 'curated'):
                folder = base / unit['name'] / mode / variant
                argv = [str(x) for x in command(tools, unit, mode, variant, folder)]
                expected_jobs.append(dict(unit=unit['name'], mode=mode, variant=variant, argv=argv, exit=0, log_sha256=sha(folder / 'compile.log')))
                deps = dependencies(folder, variant, resource)
                pair.append(facts(folder / 'unit.o', reader, unit['name']=='startup-data'))
                need(deps == record['dependencies'][folder.relative_to(base).as_posix()], 'Complete actual header hashes')
            need(pair[0] == pair[1], 'Function code/allocation/relocations differ after source organization: ' + unit['name'] + '/' + mode)
            if unit['name'] == 'init-mask':
                need(pair[1]['functions'] == [dict(name='tsl9_rebuild_register_mask_19106', binding=1, bytes=30,
                     code_sha256='69724f8e22551d238b67e52e25b3c1cbcaa62db28756da9b59a5c96ff7f16d87')], 'Exact original initialization leaf')
            if unit['name'] == 'delay-registers':
                need(pair[1]['functions'] == [dict(name='tsl9_delay_registers_19764', binding=1, bytes=54,
                     code_sha256='0bcb7577e755f1ca9736b0fd0b05e4d3f0a0e1e0cd3a59976b947191d3df74a4')], 'Exact original delay leaf')
            if unit['name'] == 'nv-read-registers':
                need(pair[1]['functions'] == [dict(name='tsl9_nv_read_registers_1979a', binding=1, bytes=30,
                     code_sha256='55eaeff68d528f2e86c97ce41148fa5ef921bd325a35e86d439df5a1cc6dedda')] and
                     not pair[1]['UND'] and not pair[1]['relocations'], 'Measured read register projection; dynamic slot provider and full equivalence remain unknown')
            if unit['name'] == 'nv-read-live-count':
                need(pair[1]['functions'] == [dict(name='tsl9_nv_read_live_count_1979a', binding=1, bytes=30,
                     code_sha256='05b184cb6e192355342a6b6e71a7db136f2d53aa7aa33a341fb1551f4b49f58a')] and
                     not pair[1]['UND'] and not pair[1]['relocations'], 'Measured direct-A2 read call projection only; ordering and dynamic provider remain unknown')
            if unit['name'] == 'boot-clock-prefix':
                need(pair[1]['functions'] == [
                    dict(name='tsl9_clock_prefix_body',binding=1,bytes=220,code_sha256='ec199e4c071f4b65e096b3514dfdf566962581a93f2fc9f52c04d064613b8885'),
                    dict(name='tsl9_clock_prefix_entry',binding=1,bytes=12,code_sha256='235e2cf36d914ddf21c5f547ef9fdac03cbc88074b99075a04d453d053f59b49')]
                    and not pair[1]['UND'] and not pair[1]['relocations']
                    and pair[1]['allocated_bytes']==232
                    and all(x['flags']==6 and x['type']==1 for x in pair[1]['allocated_sections']),
                    'Measured 232B clock entry/body without internal jumps; linked fall-through adjacency needs the separate fit verifier, full IRQ/fault/physical behavior unproved')
            if unit['name'] == 'nv-write-frame-contract':
                need(pair[1]['functions'] == [dict(name='tsl9_nv_write_frame_contract_197be', binding=1, bytes=50,
                     code_sha256='f7d326d05b196a3e08ce65713327008b3709b20903f1dba328546cf3e1ea4e9c')], 'Measured callback frame/source contract, not whole-original code equality')
                callees = ['tsl9_flash_unlock_18e98', 'tsl9_flash_erase_18ec4', 'tsl9_flash_program_18ef2', 'tsl9_flash_lock_18eb6', 'tsl9_delay_registers_19764']
                need(pair[1]['UND'] == sorted(callees) and [x['symbol'] for x in pair[1]['relocations']] == callees and
                     [x['offset'] for x in pair[1]['relocations']] == [10, 16, 26, 30, 36] and
                     all(x['type'] == 17 for x in pair[1]['relocations']), 'Five actual JAL relocations to real provider roles')
            results.append(dict(unit=unit['name'], mode=mode, complete_object_projection_equal=True, facts=pair[1]))
    need(record['commands'] == expected_jobs, 'Complete exact successful compiler recipe list')
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir', type=Path, help='Local LLVM bin directory; no tools are downloaded.')
    p.add_argument('--build-root', type=Path, help='New directory below build/curated-source; defaults to a UUID.')
    p.add_argument('--replay', type=Path, help='Read-only verification.json from an existing build.')
    a = p.parse_args()
    manifest = metadata()
    if a.replay:
        need(not a.tool_dir and not a.build_root, 'Replay does not compile')
        receipt = a.replay.resolve(); base = receipt.parent
        record = json.loads(receipt.read_bytes())
        need(record['artifacts'] == inventory(base), 'Complete actual build inventory')
        results = audit(base, record, manifest)
        need(results == record['results'], 'Read-only replay equality')
        print(json.dumps(dict(passed=True, mode='read-only-replay', comparisons=len(results), target_execution=False)))
        return
    if not a.tool_dir:
        need(not a.build_root, '--build-root requires --tool-dir')
        print(json.dumps(dict(passed=True, mode='source-metadata', source_files=len(manifest['files']), native_units=len(manifest['native_units']), compiler_invoked=False, target_execution=False)))
        return
    tools = {'clang': (a.tool_dir / ('clang.exe' if os.name == 'nt' else 'clang')).resolve()}
    need(all(p.is_file() for p in tools.values()), 'Missing local clang; supply --tool-dir')
    base = (a.build_root or ROOT / 'build/curated-source' / uuid.uuid4().hex).resolve()
    need(base.is_relative_to(ROOT / 'build/curated-source') and base != ROOT / 'build/curated-source' and not base.exists(), 'New owned build directory only')
    base.mkdir(parents=True)
    resource_run = subprocess.run([str(tools['clang']), '-print-resource-dir'], capture_output=True, timeout=30)
    (base / 'resource.log').write_bytes(resource_run.stdout)
    need(resource_run.returncode == 0, 'Compiler resource query failed')
    resource = Path(resource_run.stdout.decode().strip()).resolve()
    record = dict(schema='TSL9-curated-source-object-comparison-v1', inputs=inputs(manifest),
                  tools={n: dict(path=str(v), sha256=sha(v)) for n, v in tools.items()}, resource_dir=str(resource),
                  resource_log_sha256=sha(base / 'resource.log'), commands=[], dependencies={})
    for unit in manifest['native_units']:
        for mode in ('c', 'cpp'):
            for variant in ('origin', 'curated'):
                folder = base / unit['name'] / mode / variant
                folder.mkdir(parents=True)
                argv = [str(x) for x in command(tools, unit, mode, variant, folder)]
                result = subprocess.run(argv, cwd=folder, capture_output=True, timeout=120)
                (folder / 'compile.log').write_bytes(result.stdout + result.stderr)
                need(result.returncode == 0, 'Compilation failed; inspect ' + str(folder / 'compile.log'))
                record['commands'].append(dict(unit=unit['name'], mode=mode, variant=variant, argv=argv, exit=0, log_sha256=sha(folder / 'compile.log')))
                record['dependencies'][folder.relative_to(base).as_posix()] = dependencies(folder, variant, resource)
    record['results'] = audit(base, record, manifest)
    record['artifacts'] = inventory(base)
    (base / 'verification.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
    print(json.dumps(dict(passed=True, mode='actual-object-comparison', comparisons=len(record['results']), receipt=str(base / 'verification.json'),
                          legacy_reference_tests_rerun=False, linked_firmware=False, target_execution=False, network=False)))


if __name__ == '__main__':
    main()
