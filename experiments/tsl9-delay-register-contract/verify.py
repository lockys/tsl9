#!/usr/bin/env python3
"""Compile and compare one real C/C++ leaf; never execute RV32 or MMIO."""
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
HERE = Path(__file__).resolve().parent
SYMBOL = 'tsl9_delay_registers_19764'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ORIGINAL = bytes.fromhex('b7f700e0d8438146799bd8c303c7e1173306a70290cbd4cb98431367070198c398431367170298c3d843058b75df9843799b98c38280')
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
PARSER = 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
STDINT_SHA = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flags(mode):
    return ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-Oz', '-mllvm', '-enable-machine-outliner=never',
            '-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
            '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror',
            *['-ffixed-x' + str(reg) for reg in range(1, 32) if reg not in {10, 12, 13, 14, 15}],
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17']


def recipes(tools, source, folder, mode):
    return [('compile', [tools['clang'], *flags(mode), '-c', '-MD', '-MF', folder / 'native.d', '-MT', 'native.o', source, '-o', folder / 'native.o']),
            ('IR', [tools['clang'], *flags(mode), '-S', '-emit-llvm', source, '-o', folder / 'native.ll']),
            ('link', [tools['ld.lld'], '--no-relax', '-T', HERE / 'component.ld', folder / 'native.o', '-o', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
            ('disassemble', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf'])]


def compiler_dependencies(folder, source, stdint):
    text = (folder / 'native.d').read_text(encoding='utf-8').replace('\\\n', ' ')
    target, separator, tail = text.partition(':')
    need(separator and target == 'native.o', 'Actual compiler dependency target')
    paths = {Path(re.sub(r'\\(.)', r'\1', token)).resolve() for token in re.findall(r'(?:\\.|[^\s])+', tail)}
    need(paths == {source.resolve(), stdint.resolve()}, 'Exact compiler-observed source and stdint closure')
    return {str(path): sha(path) for path in sorted(paths)}


def inspect(root, folder, record):
    need(record['schema'] == 'TSL9-delay-register-static-component-v2' and record['mode'] in ('c', 'cpp'), 'Known schema and language')
    need(folder.is_relative_to(HERE / 'build'), 'Owned receipt folder')
    tools = {name: Path(path) for name, path in record['tools'].items()}
    need(set(tools) == set(TOOLS) and all(sha(tools[n]) == pin for n, pin in TOOLS.items()), 'Recorded exact tool hashes')
    stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    need(sha(stdint) == STDINT_SHA, 'Recorded exact stdint resource')
    expected_inputs = [Path(__file__).resolve(), HERE / 'src/delay.c', HERE / 'component.ld', root / PARSER,
                       Path(record['firmware']), stdint, *tools.values()]
    need(set(record['inputs']) == {str(f) for f in expected_inputs}, 'Complete exact input set')
    for name, digest in record['inputs'].items():
        need(sha(Path(name)) == digest, 'Changed input: ' + name)
    need(record['compiler_dependencies'] == compiler_dependencies(folder, HERE / 'src/delay.c', stdint), 'Complete compiler-observed header hashes')
    expected_commands = recipes(tools, HERE / 'src/delay.c', folder, record['mode'])
    need(len(record['commands']) == len(expected_commands), 'Complete exact command list')
    for command, (label, argv) in zip(record['commands'], expected_commands):
        need(command == dict(label=label, argv=[str(x) for x in argv], exit=0, log_sha256=sha(folder / (label + '.log'))), 'Exact successful command recipe and retained log')
    need(sha(root / PARSER) == PARSER_SHA, 'Pinned separate ELF parser')
    firmware = Path(record['firmware'])
    need(sha(firmware) == IMAGE_SHA, 'Exact original V4.1.60 firmware')
    original = firmware.read_bytes()[0x11764:0x1179a]
    need(original == ORIGINAL, 'Original leaf bytes and base 0x8000')
    reader = runpy.run_path(str(root / PARSER))['ELF']
    obj = reader(folder / 'native.o')
    linked = reader(folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf')
    facts = []
    for elf, label in [(obj, 'object'), (linked, 'linked')]:
        defs = [s for s in elf.symbols if s['info'] & 15 == 2 and s['index'] != 0 and s['size']]
        need(len(defs) == 1 and defs[0]['name'] == SYMBOL and defs[0]['info'] >> 4 == 1, 'Exactly one genuine global function')
        need(elf.flags == 1, 'Actual RV32 RVC ABI flags')
        need(not [s for s in elf.symbols if s['name'] and s['index'] == 0 and s['info'] >> 4 in (1, 2)], 'No undefined global provider')
        need(not [s for s in elf.symbols if s['index'] == 0xfff1 and s['info'] >> 4 in (1, 2)], 'No global ABS provider')
        code = elf.function_bytes(defs[0])
        need(len(code) == 54 and code == original, 'Whole object/linked leaf equals actual original bytes')
        need(elf.kind == (1 if label == 'object' else 2), 'Expected ELF kind')
        if label == 'linked':
            need(elf.kind == 2 and not elf.relocations, 'Linked ET_EXEC with no unresolved relocations')
            need(code == original, 'Whole linked leaf equals actual original bytes')
        alloc = [dict(name=s['name'], bytes=s['size'], flags=s['flags']) for s in elf.sections if s['flags'] & 2 and s['size']]
        expected_section = '.text.' + SYMBOL if label == 'object' else '.text'
        code_sections = [s for s in alloc if s['flags'] & 4]
        need(len(code_sections) == 1 and code_sections[0]['name'] == expected_section and code_sections[0]['bytes'] == 54, 'Exactly one expected executable section')
        shape = sorted((s['name'], s['size'], s['flags'], s['type']) for s in elf.sections if s['flags'] & 2 and s['size'])
        expected_shape = [(expected_section, 54, 6, 1)]
        if record['mode'] == 'cpp':
            expected_shape.append(('.eh_frame', 40 if label == 'object' else 44, 2, 1))
        need(shape == sorted(expected_shape), 'Exact allocated sections; no extra writable/NOBITS/carrier data')
        need(not elf.relocations if record['mode'] == 'c' or label == 'linked' else
             len(elf.relocations) == 3 and all(r['owner'] == '.eh_frame' for r in elf.relocations), 'Only expected C++ object unwind relocations')
        facts.append(dict(kind=label, function_bytes=len(code), function_value=defs[0]['value'],
                          function_section_address=elf.sections[defs[0]['index']]['address'],
                          code_sha256=hashlib.sha256(code).hexdigest(), allocated_sections=alloc,
                          allocated_bytes=sum(s['bytes'] for s in alloc), relocations=len(elf.relocations)))
    return dict(passed=True, actual_artifacts_read=True, mode=record['mode'], original_VA='0x19764', original_file_offset='0x11764',
                original_bytes=54, original_instructions=22, entire_linked_function_equals_original=True,
                original_code_sha256=hashlib.sha256(original).hexdigest(), ELF_facts=facts,
                own_written_GPR=['a2', 'a3', 'a4', 'a5'], a0_a1_unchanged=True,
                normal_outputs={'a2': 'u32(fresh_u8(live_GP+382)*entry_A0)', 'a3': '0', 'a4': 'fresh_final_CTRL&~1', 'a5': '0xe000f000'},
                local_instruction_trace_equal=True, global_fault_IRQ_context_proved=False,
                physical_chip_identified=False, installed_ROM_proved=False, physical_placement_proved=False,
                whole_startup_equivalence=False, fault_IRQ_equivalence=False, target_execution=False, network=False,
                BIN_generated=False, rebuilt_flashable_BIN=False)


def replay(root, receipt):
    record = json.loads(receipt.read_bytes())
    folder = receipt.parent
    actual = {p.name: sha(p) for p in folder.iterdir() if p.is_file() and p != receipt}
    need(actual == record['artifacts'], 'Complete actual build inventory')
    result = inspect(root, folder, record)
    need(result == record['result'], 'Read-only replay equality')
    return result


def run(argv, folder, label):
    result = subprocess.run([str(x) for x in argv], cwd=folder, capture_output=True, timeout=120)
    log = folder / (label + '.log')
    log.write_bytes(result.stdout + result.stderr)
    need(result.returncode == 0, label + ' failed; see retained local log')
    return dict(label=label, argv=[str(x) for x in argv], exit=result.returncode, log_sha256=sha(log))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--tool-dir', type=Path)
    p.add_argument('--firmware', type=Path)
    p.add_argument('--build-root', type=Path)
    p.add_argument('--replay', type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    need(HERE == root / 'experiments/tsl9-delay-register-contract', 'Canonical model root')
    if a.replay:
        need(not a.tool_dir and not a.firmware and not a.build_root, 'Read-only replay mode')
        print(json.dumps(replay(root, a.replay.resolve())))
        return
    need(a.tool_dir and a.firmware, 'Explicit local LLVM and original firmware')
    firmware = a.firmware.resolve()
    need(sha(firmware) == IMAGE_SHA, 'Original firmware identity before compile')
    need(sha(root / PARSER) == PARSER_SHA, 'Unchanged separate ELF reader')
    tools = {name: (a.tool_dir / (name + ('.exe' if os.name == 'nt' else ''))).resolve() for name in TOOLS}
    need(all(sha(tools[name]) == pin for name, pin in TOOLS.items()), 'Exact declared LLVM tools')
    stdint = a.tool_dir.parent / 'lib/clang/18/include/stdint.h'
    need(sha(stdint) == STDINT_SHA, 'Pinned freestanding stdint resource')
    output = (a.build_root or HERE / 'build' / uuid.uuid4().hex).resolve()
    need(output.is_relative_to(HERE / 'build') and not output.exists(), 'New owned build directory only')
    output.mkdir(parents=True)
    source = HERE / 'src/delay.c'
    inputs = [Path(__file__).resolve(), source, HERE / 'component.ld', root / PARSER, firmware, stdint, *tools.values()]
    results = []
    for mode in ['c', 'cpp']:
        folder = output / mode
        folder.mkdir()
        commands = [run(argv, folder, label) for label, argv in recipes(tools, source, folder, mode)]
        record = dict(schema='TSL9-delay-register-static-component-v2', mode=mode, firmware=str(firmware),
                      tools={n: str(f) for n, f in tools.items()}, inputs={str(f): sha(f) for f in inputs}, commands=commands)
        record['compiler_dependencies'] = compiler_dependencies(folder, source, stdint)
        record['result'] = inspect(root, folder, record)
        record['artifacts'] = {f.name: sha(f) for f in folder.iterdir() if f.is_file()}
        receipt = folder / 'verification.json'
        receipt.write_bytes((json.dumps(record, indent=2) + '\n').encode())
        results.append(replay(root, receipt))
    print(json.dumps(dict(passed=True, build_root=str(output), results=results)))


if __name__ == '__main__':
    main()
