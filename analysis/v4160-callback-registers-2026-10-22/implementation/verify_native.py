#!/usr/bin/env python3
"""Fresh native C/C++ compilation, explicit save ordering and read-only replay.

Only compiler/linker/Python validation processes run. RV32 code never runs.
"""
import argparse
import copy
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
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-v4160-callback-registers'
FRAME = 'f5f17633570540f838399e30d932e5eca439eae1239a9429c6b89560d4476f02'
PARSER = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
RESOURCE = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
BASE = '783918ed872b02c62321d1997bb4be2db08447f0f1d1def10a722c209f06fa8f'
TOOLS = {'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
INDEPENDENT = {'review.py': '57da439732bbfed651f6b7d82fd46762db3dbe1920e7555ddae5430ff62cd6b0',
               'frame.py': '8b8c9e3bee89287a1e41c394e5fe7a1ed7a8624f0bf80def7dc55c05fce2557d',
               'fields.py': '373d78c75feb58fcbf621d924733249786c8243197f8eef4e0a52e33e304b413',
               'llvm.py': 'c52cc458441eab2038ff4bb5064666ec87af3b2345f5c8b99cf9fdcc0ffb0fd5',
               'baselines.json': '98dbf5266165e6971e486691bf2ee5b11a9c025fe48b349885d852a8c379dd0d'}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    with path.open('xb') as stream:
        stream.write((json.dumps(value, indent=2) + '\n').encode('utf8'))


def case(root, slug):
    return next(p for p in (root / 'analysis' / slug, root / 'apk-analysis' / ('tsl9-' + slug)) if p.is_dir())


def context(root):
    base = case(root, 'v4160-event-callback-2026-10-22') / 'implementation'
    profile = base / 'verify_native.py'
    helper = case(root, 'v4160-ota-tx-2026-10-22') / 'implementation/verify_native.py'
    parser = case(root, 'v4160-irq-native-2026-10-21') / 'compiler-review/elf32.py'
    frame = root / MODEL / 'postpass/frame.py'
    independent = case(root, 'v4160-callback-registers-2026-10-22') / 'ABI-review'
    for name, pin in INDEPENDENT.items():
        need(sha(independent / name) == pin, 'Frozen independent native/ordering gate ' + name)
    for path, pin in ((profile, BASE), (parser, PARSER), (frame, FRAME),
                      (helper, '253b5fb067d5f5c90e517e2df4593381ef807dfbdd6143de2526c97a84744525'),
                      (base / 'seal.json', 'ba10071d511399e4be47c4cc7432121e0ddc386cd4a0b6f7abcabca5fe3935cf')):
        need(sha(path) == pin, 'Immutable profile/parser/frame/baseline identity ' + str(path))
    return dict(base=base, profile=profile, helper=helper, parser=parser, frame=frame, independent=independent,
                A=runpy.run_path(str(independent / 'review.py')),
                AF=runpy.run_path(str(independent / 'frame.py')),
                M=runpy.run_path(str(profile)), F=runpy.run_path(str(frame)),
                E=runpy.run_path(str(parser))['ELF'],
                machine=runpy.run_path(str(HERE / 'machine.py')),
                source=runpy.run_path(str(HERE / 'source_gate.py')))


def pins(root, ctx, tools):
    paths = [Path(__file__), HERE / 'probe_gp.py', HERE / 'machine.py', HERE / 'source_gate.py',
             ctx['profile'], ctx['helper'], ctx['parser'], ctx['base'] / 'seal.json', ctx['frame'],
             Path(sys.executable), *tools.values(),
             *[root / MODEL / 'src' / n for n in ('callback.c', 'callback.h', 'io.h')],
             *[ctx['independent'] / n for n in INDEPENDENT],
             *[case(root, slug) / relative for slug, relative in
               [('v4160-ota-tx-2026-10-22', 'source-review/raw.py'),
                ('v4160-event-callback-2026-10-22', 'source-review/raw.py')]],
             *[root / 'experiments/tsl9-v4160-event-callback/src' / n
               for n in ('callback.c', 'callback.h', 'io.h')]]
    return {str(p.resolve()): sha(p) for p in paths}


def artifact_map(folder):
    return {p.relative_to(folder).as_posix(): dict(bytes=p.stat().st_size, sha256=sha(p))
            for p in sorted(folder.rglob('*')) if p.is_file() and p.name != 'verification.json'}


def flags(ctx, mode):
    return ctx['M']['flags'](mode) + ['-ffixed-x26', '-ffixed-x27']


def raw_recipes(root, folder, mode, tools, ctx):
    source = root / MODEL / 'src/callback.c'
    return [('compiler-resource-dir', [tools['clang'], '-print-resource-dir']),
            ('native-object', [tools['clang'], *flags(ctx, mode), '-c', '-MD', '-MF', folder / 'callback.d',
                               '-MT', 'callback.o', source, '-o', folder / 'callback.o']),
            ('native-IR', [tools['clang'], *flags(ctx, mode), '-S', '-emit-llvm', source, '-o', folder / 'callback.ll']),
            ('strict-component-link', [tools['ld.lld'], '-m', 'elf32lriscv', '--no-relax', '--build-id=none',
                                       '-T', folder / 'component.ld', folder / 'callback.o', '-o',
                                       folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
            ('complete-static-disassembly', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr', '-d',
                                              folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf'])]


def ordered_recipes(root, raw, folder, tools, ctx, python):
    return [('existing-save-word-order', [python, '-B', ctx['frame'], '--project-root', root,
                                           '--input', raw / 'callback.o', '--output', folder / 'callback-ordered.o',
                                           '--receipt', folder / 'frame-order.json']),
            ('strict-ordered-link', [tools['ld.lld'], '-m', 'elf32lriscv', '--no-relax', '--build-id=none',
                                     '-T', folder / 'component.ld', folder / 'callback-ordered.o', '-o',
                                     folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
            ('complete-static-disassembly', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr', '-d',
                                              folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf'])]


def command_gate(folder, commands, expected):
    need([(x['label'], x['argv']) for x in commands] ==
         [(name, [str(v) for v in argv]) for name, argv in expected], 'Exact actual command chronology/argv')
    for row in commands:
        log = (folder / row['log']).resolve()
        need(log.parent == folder and row['exit'] == 0 and sha(log) == row['sha256'],
             'Actual successful command log identity')


def dependencies(root, folder, text=None):
    resource = Path((folder / 'compiler-resource-dir.log').read_text().strip()).resolve() / 'include/stdint.h'
    need(sha(resource) == RESOURCE, 'Actual observed compiler resource header')
    if text is None:
        text = (folder / 'callback.d').read_text()
    text = text.replace('\\\n', ' ').replace('\\\r\n', ' ')
    target, _, tail = text.partition(':')
    need(target == 'callback.o', 'Actual compiler -MT association')
    actual = {Path(re.sub(r'\\(.)', r'\1', t)).resolve() for t in re.findall(r'(?:\\.|[^\s])+', tail)}
    required = {root / MODEL / 'src' / n for n in ('callback.c', 'callback.h', 'io.h')} | {resource}
    need(actual == required, 'Exact three project sources plus one observed resource header closure')
    return [dict(path=str(p), sha256=sha(p)) for p in sorted(actual)]


def ir_gate(path):
    text = path.read_text()
    need(text.count('asm sideeffect "", "={x3},~{memory}"') == 6 and
         'asm sideeffect "mv $0,gp"' not in text, 'Six live fixed-GP IR sites, no snapshots')
    calls = [s for s in text.splitlines() if 'asm sideeffect "jalr ra,a' in s]
    need(len(calls) == 15, 'Fifteen actual opaque IR calls')
    for line in calls:
        for register in range(10, 18):
            need('={x' + str(register) + '}' in line and ',{x' + str(register) + '}' in line,
                 'Eight arguments remain explicit read/write operands')
        for register in (1, 5, 6, 7, 28, 29, 30, 31):
            need('~{x' + str(register) + '}' in line, 'Honest opaque caller clobber')
    for width in (8, 16, 32):
        need('load volatile i' + str(width) in text and 'store volatile i' + str(width) in text,
             'Actual typed volatile width')
    return dict(fresh_GP_IR_sites=6, opaque_calls=15, argument_GPRs=list(range(10, 18)),
                volatile_widths=[8, 16, 32], full_physical_register_prefix_proved=False)


def substage_gate(root, raw, mode, tools, ctx):
    report = read(raw / 'probe.json')
    need(report['passed'] and report['mode'] == mode and report['source_changes'] and
         report['profile_additions'] == ['-ffixed-x26', '-ffixed-x27'], 'Exact source/profile diagnostic')
    command_gate(raw, report['commands'], raw_recipes(root, raw, mode, tools, ctx))
    resource = Path((raw / 'compiler-resource-dir.log').read_text().strip()) / 'include/stdint.h'
    inputs = [ctx['profile'], ctx['helper'], ctx['parser'], ctx['base'] / 'seal.json', HERE / 'probe_gp.py',
              *[root / MODEL / 'src' / n for n in ('callback.c', 'callback.h', 'io.h')],
              *tools.values(), resource]
    need(report['source_pins'] == {str(p.resolve()): sha(p) for p in inputs},
         'Complete actual generator before/after source/tool/resource pins')
    need(set(report['artifacts']) == {p.name for p in raw.iterdir() if p.is_file() and p.name != 'probe.json'},
         'Complete raw generator artifact inventory')
    for name, pin in report['artifacts'].items():
        path = raw / name
        need(sha(path) == pin['sha256'] and path.stat().st_size == pin['bytes'], 'Actual raw generator artifact')
    need((raw / 'component.ld').read_bytes() == ctx['M']['LAYOUT'].encode(), 'Unchanged scratch-only layout')
    return report


def checks(root, raw, folder, mode, commands, tools, python, ctx):
    substage_gate(root, raw, mode, tools, ctx)
    command_gate(folder, commands, ordered_recipes(root, raw, folder, tools, ctx, python))
    need((folder / 'component.ld').read_bytes() == ctx['M']['LAYOUT'].encode(), 'Exact ordered scratch layout')
    frame = ctx['F']['replay'](root, folder / 'frame-order.json')
    independent_pre = ctx['A']['inspect'](root, raw)
    independent_frame = ctx['AF']['audit'](root, raw / 'callback.o', folder / 'callback-ordered.o',
                                          folder / 'frame-order.json')
    pre = ctx['machine']['inspect'](root, raw)
    post = ctx['machine']['inspect'](root, folder, ordered=True)
    need(pre['bytes'] == post['bytes'] == 624 and pre['instructions'] == post['instructions'] == 223,
         'Only actual measured 624-byte conditional component')
    object_elf = ctx['E'](folder / 'callback-ordered.o')
    linked_elf = ctx['E'](folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf')
    object_section = next(s for s in object_elf.sections if s['flags'] & 2 and s['size'])
    linked_section = next(s for s in linked_elf.sections if s['flags'] & 2 and s['size'])
    need(object_elf.data(object_section) == linked_elf.data(linked_section), 'No link-time code substitute/padding')
    return dict(source=ctx['source']['inspect'](root), dependency_inputs=dependencies(root, raw),
                IR=ir_gate(raw / 'callback.ll'), before=pre, after=post, frame_order=frame,
                independent_pre=independent_pre, independent_frame=independent_frame,
                disassembly_controls=ctx['machine']['transcript_controls'](root, folder, ordered=True),
                native_recipes=8, whole632_storage_covered=False, original_ABI_admitted=False,
                original_placement_admitted=False, hardware_OTA_proved=False,
                HOST_suite_rerun=False, target_execution=False, BIN_exported=False)


def record_controls(root, raw, folder, mode, commands, tools, python, ctx):
    cases = []
    def reject(name, fn):
        try:
            fn()
        except ValueError as error:
            cases.append(dict(name=name, rejected=True, reason=str(error)))
            return
        raise ValueError('Malformed record accepted ' + name)
    expected = ordered_recipes(root, raw, folder, tools, ctx, python)
    bad = copy.deepcopy(commands); bad[1]['argv'].insert(1, '--allow-shlib-undefined')
    reject('extra_linker_flag', lambda: command_gate(folder, bad, expected))
    reject('missing_explicit_order_stage', lambda: command_gate(folder, commands[1:], expected))
    bad = copy.deepcopy(commands); bad[0], bad[1] = bad[1], bad[0]
    reject('ordering_after_link', lambda: command_gate(folder, bad, expected))
    reject('wrong_MD_target', lambda: dependencies(root, raw, (raw / 'callback.d').read_text().replace('callback.o:', 'other.o:', 1)))
    return cases


def invocation(root, receipt, report):
    folder = receipt.parent
    base = folder.parent.parent
    item = report['generation']; python = report['python']['path']
    expected = [python, '-B', str(HERE / 'probe_gp.py'), '--project-root', str(root), '--tool-dir',
                report['tool_dir'], '--build-root', str(base / 'pre'), '--language', report['generation_language']]
    need(item['argv'] == expected and item['exit'] == 0 and item['log'] == str(base / 'fresh-generation.log') and
         sha(base / 'fresh-generation.log') == item['sha256'], 'Exact actual generator command and outer log')
    output = read(base / 'fresh-generation.log')
    modes = ('c', 'cpp') if report['generation_language'] == 'both' else (report['generation_language'],)
    need(output['passed'] and [(r['mode'], r['receipt']) for r in output['results']] ==
         [(m, str(base / 'pre' / m / 'probe.json')) for m in modes], 'Actual complete raw generation results')
    for row in output['results']:
        need(sha(Path(row['receipt'])) == row['sha256'], 'Actual generated receipt hash')
    need(Path(report['raw_folder']).resolve() == base / 'pre' / report['mode'] and
         folder == base / 'ordered' / report['mode'], 'Exact pre/ordered output associations')


def replay(root, receipt):
    receipt = receipt.resolve(); report = read(receipt); folder = receipt.parent; ctx = context(root)
    tools = {n: Path(row['path']) for n, row in report['tools'].items()}
    need(set(tools) == set(TOOLS) and all(sha(p) == TOOLS[n] == report['tools'][n]['sha256'] for n, p in tools.items()),
         'Pinned actual LLVM executables')
    need(report['passed'] and report['source_pins'] == pins(root, ctx, tools), 'Current exact formal source/tool inputs')
    need(report['python']['sha256'] == sha(Path(report['python']['path'])), 'Actual Python stage identity')
    raw = Path(report['raw_folder']).resolve()
    for where, key in ((raw, 'raw_artifacts'), (folder, 'artifacts')):
        need(report[key] == artifact_map(where), 'Complete actual artifact set and byte identities')
    invocation(root, receipt, report)
    result = checks(root, raw, folder, report['mode'], report['commands'], tools, report['python']['path'], ctx)
    controls = record_controls(root, raw, folder, report['mode'], report['commands'], tools, report['python']['path'], ctx)
    need(json.loads(json.dumps(result)) == report['checks'] and controls == report['record_controls'],
         'Actual fields/source/IR/ordering/coverage and countercase replay')
    return dict(passed=True, receipt=str(receipt), sha256=sha(receipt), actual_native_artifacts_read=True,
                native_bytes=624, instructions=223, relative_source_save_order_preserved=True,
                uncovered_original_bytes=8, original_placement_admitted=False,
                original_ABI_admitted=False, hardware_OTA_proved=False, target_execution=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--tool-dir', type=Path)
    parser.add_argument('--language', choices=['c', 'cpp', 'both'])
    parser.add_argument('--build-root', type=Path)
    parser.add_argument('--replay', type=Path)
    args = parser.parse_args(); root = args.project_root.resolve(strict=True)
    if args.replay:
        need(args.tool_dir is None and args.language is None and args.build_root is None,
             'Read-only replay forbids fresh-build arguments')
        print(json.dumps(replay(root, args.replay))); return
    need(args.tool_dir is not None, 'Explicit pinned local LLVM directory required')
    ctx = context(root); tools = {n: next(p for p in (args.tool_dir / (n + '.exe'), args.tool_dir / n)
                                        if p.is_file()).resolve() for n in TOOLS}
    need(all(sha(p) == TOOLS[n] for n, p in tools.items()), 'Pinned local LLVM tools')
    before = pins(root, ctx, tools); ctx['source']['inspect'](root)
    owner = (root / MODEL / 'build').resolve()
    base = args.build_root.resolve() if args.build_root else owner / ('formal-' + uuid.uuid4().hex)
    need(base.is_relative_to(owner) and base != owner and not base.exists(), 'Create-only new owned build root')
    base.mkdir(parents=True); language = args.language or 'both'
    argv = [sys.executable, '-B', str(HERE / 'probe_gp.py'), '--project-root', str(root), '--tool-dir',
            str(args.tool_dir.resolve()), '--build-root', str(base / 'pre'), '--language', language]
    process = subprocess.run(argv, cwd=root, capture_output=True, timeout=300)
    log = base / 'fresh-generation.log'; log.write_bytes(process.stdout + process.stderr)
    need(process.returncode == 0, 'Actual native generation failed: ' + str(log))
    fresh = json.loads(process.stdout); need(fresh['passed'], 'Actual native generator result')
    results = []
    for item in fresh['results']:
        mode = item['mode']; raw = base / 'pre' / mode; folder = base / 'ordered' / mode
        folder.mkdir(parents=True); tmp = folder / 'compiler-temp'; tmp.mkdir()
        env = dict(os.environ, TMP=str(tmp), TEMP=str(tmp)); commands = []
        (folder / 'component.ld').write_bytes(ctx['M']['LAYOUT'].encode())
        for label, command in ordered_recipes(root, raw, folder, tools, ctx, sys.executable):
            x = subprocess.run([str(v) for v in command], cwd=folder, capture_output=True, timeout=120, env=env)
            output = folder / (label + '.log'); output.write_bytes(x.stdout + x.stderr)
            commands.append(dict(label=label, argv=[str(v) for v in command], exit=x.returncode,
                                 log=output.name, sha256=sha(output), TMP=str(tmp), TEMP=str(tmp)))
            need(x.returncode == 0, 'Actual explicit stage failed: ' + str(output))
        need(before == pins(root, ctx, tools), 'Stable before/after formal source/profile/tool inputs')
        result = checks(root, raw, folder, mode, commands, tools, sys.executable, ctx)
        controls = record_controls(root, raw, folder, mode, commands, tools, sys.executable, ctx)
        report = dict(schema='TSL9-callback-live-GP-reserved-register-component-v1', passed=True, mode=mode,
                      source_pins=before, commands=commands, checks=result, record_controls=controls,
                      python=dict(path=sys.executable, sha256=sha(Path(sys.executable))),
                      tools={n: dict(path=str(p), sha256=sha(p)) for n, p in tools.items()},
                      tool_dir=str(args.tool_dir.resolve()), raw_folder=str(raw),
                      generation_language=language,
                      generation=dict(argv=argv, exit=process.returncode, log=str(log), sha256=sha(log)),
                      raw_artifacts=artifact_map(raw), artifacts=artifact_map(folder),
                      original_placement_admitted=False, original_ABI_admitted=False,
                      hardware_OTA_proved=False, target_execution=False, BIN_exported=False,
                      HOST_suite_rerun=False)
        receipt = folder / 'verification.json'; write(receipt, report); results.append(replay(root, receipt))
    print(json.dumps(dict(passed=True, results=results, original_ABI_admitted=False,
                         original_placement_admitted=False, target_execution=False, BIN_exported=False)))


if __name__ == '__main__':
    main()
