#!/usr/bin/env python3
"""Compile and compare one real C/C++ leaf; never execute RV32 or MMIO."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SYMBOL = 'tsl9_rebuild_register_mask_19106'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
ORIGINAL = bytes.fromhex('99c5371702405c4b5d8d48cb8280b7170240d84b1345f5ff798dc8cb8280')
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
PARSER = 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
ADAPTER = 'experiments/tsl9-v4160-irq-native/src/native_io.h'
ADAPTER_SHA = 'f98eda2e291d585b086f5e65cd4d8816855e7819350f7b93dd6002bb430a3d2e'
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
            *['-ffixed-x' + str(reg) for reg in range(1, 32) if reg not in {10, 11, 14, 15}],
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17']


def recipes(tools, source, folder, mode):
    return [('compile', [tools['clang'], *flags(mode), '-c', source, '-o', folder / 'native.o']),
            ('IR', [tools['clang'], *flags(mode), '-S', '-emit-llvm', source, '-o', folder / 'native.ll']),
            ('link', [tools['ld.lld'], '--no-relax', '-T', HERE / 'component.ld', folder / 'native.o', '-o', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
            ('disassemble', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf'])]


def inspect(root, folder, record):
    need(record['schema'] == 'TSL9-init-mask-static-component-v2' and record['mode'] in ('c', 'cpp'), 'Known schema and language')
    need(folder.is_relative_to(HERE / 'build'), 'Owned receipt folder')
    tools = {name: Path(path) for name, path in record['tools'].items()}
    need(set(tools) == set(TOOLS) and all(sha(tools[n]) == pin for n, pin in TOOLS.items()), 'Recorded exact tool hashes')
    stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    need(sha(stdint) == STDINT_SHA, 'Recorded exact stdint resource')
    expected_inputs = [Path(__file__).resolve(), HERE / 'src/init_mask.c', HERE / 'component.ld', root / ADAPTER, root / PARSER,
                       Path(record['firmware']), stdint, *tools.values()]
    need(set(record['inputs']) == {str(f) for f in expected_inputs}, 'Complete exact input set')
    for name, digest in record['inputs'].items():
        need(sha(Path(name)) == digest, 'Changed input: ' + name)
    expected_commands = recipes(tools, HERE / 'src/init_mask.c', folder, record['mode'])
    need(len(record['commands']) == len(expected_commands), 'Complete exact command list')
    for command, (label, argv) in zip(record['commands'], expected_commands):
        need(command == dict(label=label, argv=[str(x) for x in argv], exit=0, log_sha256=sha(folder / (label + '.log'))), 'Exact successful command recipe and retained log')
    need(sha(root / PARSER) == PARSER_SHA, 'Pinned separate ELF parser')
    need(sha(root / ADAPTER) == ADAPTER_SHA, 'Pinned shared register adapter')
    firmware = Path(record['firmware'])
    need(sha(firmware) == IMAGE_SHA, 'Exact original V4.1.60 firmware')
    original = firmware.read_bytes()[0x11106:0x11124]
    need(original == ORIGINAL, 'Original leaf bytes and base 0x8000')
    reader = runpy.run_path(str(root / PARSER))['ELF']
    obj = reader(folder / 'native.o')
    linked = reader(folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf')
    facts = []
    for elf, label in [(obj, 'object'), (linked, 'linked')]:
        defs = [s for s in elf.symbols if s['info'] >> 4 == 1 and s['info'] & 15 == 2 and s['index'] != 0]
        need(len(defs) == 1 and defs[0]['name'] == SYMBOL, 'One genuine function')
        need(not [s for s in elf.symbols if s['name'] and s['index'] == 0 and s['info'] >> 4 in (1, 2)], 'No undefined global provider')
        need(not [s for s in elf.symbols if s['index'] == 0xfff1 and s['info'] >> 4 in (1, 2)], 'No global ABS provider')
        code = elf.function_bytes(defs[0])
        need(len(code) == 30 and code == original, 'Whole object/linked leaf equals actual original bytes')
        need(elf.kind == (1 if label == 'object' else 2), 'Expected ELF kind')
        if label == 'linked':
            need(elf.kind == 2 and not elf.relocations, 'Linked ET_EXEC with no unresolved relocations')
            need(code == original, 'Whole linked leaf equals actual original bytes')
        alloc = [dict(name=s['name'], bytes=s['size'], flags=s['flags']) for s in elf.sections if s['flags'] & 2 and s['size']]
        expected_section = '.text.' + SYMBOL if label == 'object' else '.text'
        code_sections = [s for s in alloc if s['flags'] & 4]
        need(len(code_sections) == 1 and code_sections[0]['name'] == expected_section and code_sections[0]['bytes'] == 30, 'Exactly one expected executable section')
        facts.append(dict(kind=label, function_bytes=len(code), function_value=defs[0]['value'],
                          function_section_address=elf.sections[defs[0]['index']]['address'],
                          code_sha256=hashlib.sha256(code).hexdigest(), allocated_sections=alloc,
                          allocated_bytes=sum(s['bytes'] for s in alloc), relocations=len(elf.relocations)))
    return dict(passed=True, actual_artifacts_read=True, mode=record['mode'], original_VA='0x19106', original_file_offset='0x11106',
                original_bytes=30, original_instructions=12, entire_linked_function_equals_original=True,
                original_code_sha256=hashlib.sha256(original).hexdigest(), ELF_facts=facts,
                own_written_GPR=['a0', 'a4', 'a5'], a1_unchanged=True,
                normal_accesses=['R32(0x40021014)', 'W32(0x40021014)'],
                normal_branch_results={'enabled_nonzero': 'fresh_word OR entry_a0', 'enabled_zero': 'fresh_word AND NOT entry_a0'},
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
    need(HERE == root / 'experiments/tsl9-init-mask', 'Canonical model root')
    if a.replay:
        need(not a.tool_dir and not a.firmware and not a.build_root, 'Read-only replay mode')
        print(json.dumps(replay(root, a.replay.resolve())))
        return
    need(a.tool_dir and a.firmware, 'Explicit local LLVM and original firmware')
    firmware = a.firmware.resolve()
    need(sha(firmware) == IMAGE_SHA, 'Original firmware identity before compile')
    need(sha(root / ADAPTER) == ADAPTER_SHA and sha(root / PARSER) == PARSER_SHA, 'Unchanged shared dependencies')
    tools = {name: (a.tool_dir / (name + ('.exe' if os.name == 'nt' else ''))).resolve() for name in TOOLS}
    need(all(sha(tools[name]) == pin for name, pin in TOOLS.items()), 'Exact declared LLVM tools')
    stdint = a.tool_dir.parent / 'lib/clang/18/include/stdint.h'
    need(sha(stdint) == STDINT_SHA, 'Pinned freestanding stdint resource')
    output = (a.build_root or HERE / 'build' / uuid.uuid4().hex).resolve()
    need(output.is_relative_to(HERE / 'build') and not output.exists(), 'New owned build directory only')
    output.mkdir(parents=True)
    source = HERE / 'src/init_mask.c'
    inputs = [Path(__file__).resolve(), source, HERE / 'component.ld', root / ADAPTER, root / PARSER, firmware, stdint, *tools.values()]
    results = []
    for mode in ['c', 'cpp']:
        folder = output / mode
        folder.mkdir()
        commands = [run(argv, folder, label) for label, argv in recipes(tools, source, folder, mode)]
        record = dict(schema='TSL9-init-mask-static-component-v2', mode=mode, firmware=str(firmware),
                      tools={n: str(f) for n, f in tools.items()}, inputs={str(f): sha(f) for f in inputs}, commands=commands)
        record['result'] = inspect(root, folder, record)
        record['artifacts'] = {f.name: sha(f) for f in folder.iterdir() if f.is_file()}
        receipt = folder / 'verification.json'
        receipt.write_bytes((json.dumps(record, indent=2) + '\n').encode())
        results.append(replay(root, receipt))
    print(json.dumps(dict(passed=True, build_root=str(output), results=results)))


if __name__ == '__main__':
    main()
