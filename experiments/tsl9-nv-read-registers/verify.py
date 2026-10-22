#!/usr/bin/env python3
"""Compile/static-read one genuine read callback; no target or MMIO execution."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SYMBOL = 'tsl9_nv_read_registers_1979a'
PARSER = 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
LEDGER = 'analysis/v4160-callback-frontiers-2026-10-22/binding-review/ledger.json'
LEDGER_SHA = 'd2feba7d20867a39682af97b7f2f719516117a14c0cf2f3007a2cb286f5c478b'
SOURCE_SHA = 'e165c4a4dd39376ceb52e2838145c435126b50709ad9e82b853eae152bd5023f'
LINKER_SHA = '298f98cf90e2ba2be82872cc4a7bcfa2a9a41e59e45024d344b35e00001bdb11'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
STDINT_SHA = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
ORIGINAL = bytes.fromhex('b7070400fc474111328706c613962500aa853a858297b240014541018280')
ORIGINAL_SHA = 'e9e2a0f4b50184fa5c7b37ee004867f393b8c960fe9e66e81dc40af897114f62'
# Static expected-byte guard, not a machine-code source/provider/carrier.
# Calculated from both real native-v4 objects using the pinned ELF reader.
CANDIDATE = bytes.fromhex('411106c6b7070400fc478a0532872e86aa853a8582970145b24041018280')
CANDIDATE_SHA = '55eaeff68d528f2e86c97ce41148fa5ef921bd325a35e86d439df5a1cc6dedda'
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
# These annotations are guarded by exact candidate bytes and LLVM raw readback.
# They are not an independent ISA semantics evaluator.
ANNOTATIONS = [
    ('addi', 2), ('sw', None), ('lui', 15), ('lw', 15), ('slli', 11),
    ('mv', 14), ('mv', 12), ('mv', 11), ('mv', 10), ('jalr', 1),
    ('li', 10), ('lw', 1), ('addi', 2), ('ret', 0),
]


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def flags(mode):
    return ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr_zifencei', '-mabi=ilp32',
            '-Oz', '-mllvm', '-enable-machine-outliner=never', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
            '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror',
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17',
            *(['-fno-exceptions'] if mode == 'cpp' else [])]


def recipes(tools, folder, mode):
    source = HERE / 'src/read_registers.c'
    return [
        ('resource', [tools['clang'], '-print-resource-dir']),
        ('compile', [tools['clang'], *flags(mode), '-c', '-MD', '-MF', folder / 'native.d',
                     '-MT', 'native.o', source, '-o', folder / 'native.o']),
        ('IR', [tools['clang'], *flags(mode), '-S', '-emit-llvm', source, '-o', folder / 'native.ll']),
        ('link', [tools['ld.lld'], '--no-relax', '-T', HERE / 'component.ld', folder / 'native.o',
                  '-o', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
        ('disassemble-object', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei',
                                '-d', '-r', folder / 'native.o']),
        ('disassemble-linked', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei',
                                '-d', '-r', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
    ]


def pins(root, firmware, tools):
    stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    paths = [Path(__file__).resolve(), HERE / 'src/read_registers.c', HERE / 'component.ld',
             root / PARSER, root / LEDGER, firmware, stdint, *tools.values()]
    return {str(path): sha(path) for path in paths}


def dependencies(folder, stdint):
    text = (folder / 'native.d').read_text(encoding='utf-8').replace('\\\n', ' ')
    target, sep, tail = text.partition(':')
    paths = {Path(re.sub(r'\\(.)', r'\1', token)).resolve()
             for token in re.findall(r'(?:\\.|[^\s])+', tail)}
    need(sep and target == 'native.o' and paths == {HERE / 'src/read_registers.c', stdint},
         'Complete actual compiler source/stdint dependency closure')
    return {str(path): sha(path) for path in sorted(paths)}


def original_ledger(root, image):
    need(sha(root / LEDGER) == LEDGER_SHA, 'Pinned original operand ledger')
    ledger = json.loads((root / LEDGER).read_bytes())
    need(ledger['firmware_sha256'] == IMAGE_SHA, 'Ledger belongs to this original image')
    rows = ledger['groups']['read_cb']
    pc = 0x1979a
    raw = bytearray()
    for row in rows:
        value = bytes.fromhex(row['raw_hex'])
        need(row['PC'] == pc and row['bytes'] == len(value) and len(value) in (2, 4),
             'Contiguous original callback ledger rows')
        need(image[pc - 0x8000:pc - 0x8000 + len(value)] == value, 'Every original ledger row equals actual firmware')
        raw.extend(value)
        pc += len(value)
    need(pc == 0x197b8 and len(rows) == 13 and bytes(raw) == ORIGINAL
         and digest(raw) == ORIGINAL_SHA, 'Whole original 30-byte/13-row callback')
    return rows


def llvm_rows(elf, log, function):
    owner = elf.sections[function['index']]
    expected = elf.function_bytes(function)
    rows = []
    current = None
    for line in log.read_text(encoding='utf-8').splitlines():
        head = re.match(r'Disassembly of section (.+):', line)
        if head:
            current = head[1]
            continue
        match = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)', line)
        if not match:
            continue
        address, raw = int(match[1], 16), bytes.fromhex(match[2])
        offset = address - function['value']
        covered = sum(len(bytes.fromhex(row['raw'])) for row in rows)
        need(current == owner['name'] and offset == covered and len(raw) in (2, 4)
             and raw == expected[offset:offset + len(raw)]
             and match[3] not in ('<unknown>', '.word', '.2byte'),
             'Complete contiguous actual LLVM function bytes')
        rows.append(dict(offset=offset, raw=raw.hex(), mnemonic=match[3], operands=match[4]))
    need(sum(len(bytes.fromhex(row['raw'])) for row in rows) == 30 and len(rows) == 14,
         'All actual 30 executable bytes and 14 instructions retained')
    need([row['mnemonic'] for row in rows] == [name for name, _ in ANNOTATIONS],
         'Actual LLVM spelling agrees with fixed-byte annotations')
    return rows


def ir_gate(path):
    ir = path.read_text(encoding='utf-8')
    variable = r'%[A-Za-z0-9$._-]+'
    header = re.search(r'define[^\n]*@' + SYMBOL + r'\(([^)]*)\)', ir)
    need(header is not None, 'Actual three-word public IR definition')
    args = re.findall(r'i32(?: noundef)? (' + variable + r')', header[1])
    need(len(args) == 3, 'Source/word-count/destination entry arguments')
    source, words, destination = args

    def assigned(expression):
        match = re.search(r'(?m)^  (' + variable + r') = ' + expression, ir)
        need(match is not None, 'Actual IR dependency: ' + expression)
        return match[1]

    base = assigned(r'(?:tail )?call i32 asm sideeffect "", "=\{x15\},\{x15\},~\{memory\}"\(i32 262144\)')
    address = assigned(r'add i32 ' + re.escape(base) + r', 76')
    pointer = assigned(r'inttoptr i32 ' + re.escape(address) + r' to ptr')
    loaded = assigned(r'load volatile i32, ptr ' + re.escape(pointer) + r', align 4')
    need(len(re.findall(r'\bload volatile i32\b', ir)) == 1, 'Exactly one fresh volatile 32-bit slot read')
    target = assigned(r'(?:tail )?call i32 asm sideeffect "", "=\{x15\},\{x15\},~\{memory\}"\(i32 ' + re.escape(loaded) + r'\)')
    saved = assigned(r'(?:tail )?call(?: noundef)? i32 asm sideeffect "mv \$0, \$1", "=\{x14\},r,~\{memory\}"\(i32 ' + re.escape(destination) + r'\)')
    shifted = assigned(r'shl i32 ' + re.escape(words) + r', 2')
    byte_count = assigned(r'(?:tail )?call i32 asm sideeffect "", "=\{x12\},\{x12\},~\{memory\}"\(i32 ' + re.escape(shifted) + r'\)')
    marker = r'asm sideeffect "mv $1, $0\0A\09mv $0, $3\0A\09jalr ra, 0($4)"'
    calls = [line for line in ir.splitlines() if marker in line]
    need(len(calls) == 1 and ir.index('load volatile i32') < ir.index(marker), 'Fresh slot dependency precedes the one opaque indirect call port')
    call = re.search(r'asm sideeffect ".*", "([^"]+)"\(([^)]*)\)', calls[0])
    need(call is not None, 'Actual indirect call constraints and SSA arguments')
    values = re.findall(r'i32 (' + variable + r')', call[2])
    need(values == [source, byte_count, saved, target], 'Actual source/count/destination/fresh-target SSA call dependencies')
    tokens = call[1].split(',')
    output = {int(n) for token in tokens if token.startswith('=') for n in re.findall(r'\{x(\d+)\}', token)}
    clobbers = {int(n) for token in tokens if token.startswith('~') for n in re.findall(r'\{x(\d+)\}', token)}
    need(output == {10, 11, 12, 14, 15} and clobbers == {1, 5, 6, 7, 13, 16, 17, 28, 29, 30, 31}
         and '~{memory}' in tokens and 'ret i32 0' in ir, 'Explicit opaque-callee clobbers and normal zero result')
    return dict(fresh_volatile_u32_slot_address='0x4004c', byte_count='u32(entry_words << 2)',
                source_argument_dependencies_checked=True, actual_call_constraints=call[1],
                dynamic_callee_ABI_proved=False)


def inspect(root, folder, record):
    need(record['schema'] == 'TSL9-NV-read-register-static-component-v1' and record['mode'] in ('c', 'cpp'),
         'Known static component schema and language')
    tools = {name: Path(value) for name, value in record['tools'].items()}
    need(set(tools) == set(TOOLS) and all(sha(tools[name]) == pin for name, pin in TOOLS.items()), 'Exact declared LLVM tools')
    firmware = Path(record['firmware'])
    need(sha(firmware) == IMAGE_SHA and sha(root / PARSER) == PARSER_SHA, 'Pinned original image and separate read-only ELF reader')
    need(sha(HERE / 'src/read_registers.c') == SOURCE_SHA and sha(HERE / 'component.ld') == LINKER_SHA,
         'Exact current candidate source and explicit source linker script')
    stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    need(sha(stdint) == STDINT_SHA and record['inputs'] == pins(root, firmware, tools), 'Stable complete input hashes and compiler resource')
    need(Path((folder / 'resource.log').read_text().strip()) / 'include/stdint.h' == stdint, 'Actual compiler resource directory')
    need(record['compiler_dependencies'] == dependencies(folder, stdint), 'Actual compiler-observed MD closure')
    commands = recipes(tools, folder, record['mode'])
    need(len(record['commands']) == len(commands), 'Complete single fixed compiler/link/static-readback profile')
    for command, (label, argv) in zip(record['commands'], commands):
        need(command == dict(label=label, argv=[str(x) for x in argv], exit=0, log_sha256=sha(folder / (label + '.log'))),
             'Exact successful command recipe and retained log')
    image = firmware.read_bytes()
    original_rows = original_ledger(root, image)
    need(image[0x1179a:0x117b8] == ORIGINAL and digest(ORIGINAL) == ORIGINAL_SHA, 'Actual original read-callback bytes')
    Reader = runpy.run_path(str(root / PARSER))['ELF']
    facts = []
    for label, filename, expected_kind in [('object', 'native.o', 1), ('linked', 'COMPONENT-ONLY-NOT-FIRMWARE.elf', 2)]:
        elf = Reader(folder / filename)
        defs = [s for s in elf.symbols if s['info'] & 15 == 2 and s['index'] not in (0, 0xfff1) and s['size']]
        need(len(defs) == 1 and defs[0]['name'] == SYMBOL and defs[0]['info'] >> 4 == 1,
             'Exactly one genuine allocated global function')
        function = defs[0]
        need(elf.kind == expected_kind and elf.flags == 1, 'Actual RV32/RVC relocatable or component ELF')
        undefined = [s['name'] for s in elf.symbols if s['name'] and s['index'] == 0 and s['info'] >> 4 in (1, 2)]
        absolute = [s['name'] for s in elf.symbols if s['index'] == 0xfff1 and s['info'] >> 4 in (1, 2)]
        need(not undefined and not absolute and not elf.relocations, 'No static UND/ABS provider or relocations; dynamic provider remains unknown')
        code = elf.function_bytes(function)
        need(code == CANDIDATE and digest(code) == CANDIDATE_SHA and code != ORIGINAL,
             'Whole actual candidate bytes fixed, explicitly unequal to original')
        allocated = [s for s in elf.sections if s['flags'] & 2 and s['size']]
        expected_section = '.text.' + SYMBOL if label == 'object' else '.text'
        need([(s['name'], s['size'], s['flags'], s['type']) for s in allocated] == [(expected_section, 30, 6, 1)],
             'Exactly 30 allocated executable bytes; no writable/NOBITS/eh_frame/carrier data')
        if label == 'linked':
            need(function['value'] == struct.unpack_from('<I', elf.raw, 24)[0] == 0, 'Explicit nonphysical component VMA zero entry')
        rows = llvm_rows(elf, folder / ('disassemble-' + label + '.log'), function)
        facts.append(dict(kind=label, function_bytes=len(code), instructions=len(rows),
                          function_value=function['value'], code_sha256=digest(code),
                          allocated_sections=[{k:s[k] for k in ('name', 'size', 'flags', 'type', 'address')} for s in allocated],
                          allocated_bytes=30, global_functions=[SYMBOL], UND=undefined, global_ABS=absolute,
                          RELA=elf.relocations, LLVM_rows=rows))
    ir = ir_gate(folder / 'native.ll')
    return dict(passed=True, actual_artifacts_read=True, mode=record['mode'], ELF_facts=facts, IR_facts=ir,
                original_VA='0x1979a', original_file_offset='0x1179a', original_bytes=30, original_instructions=13,
                original_code_sha256=ORIGINAL_SHA, original_ledger_rows=original_rows,
                candidate_bytes=30, candidate_instructions=14, candidate_code_sha256=CANDIDATE_SHA,
                own_wrapper_written_GPRs=[1, 2, 10, 11, 12, 14, 15], no_A3_wrapper_write=True,
                call_boundary={'A0': 'entry_A2', 'A1': 'entry_A0', 'A2': 'u32(entry_A1 << 2)',
                               'A4': 'entry_A2', 'A5': 'fresh_u32[0x4004c]'},
                evidence_basis='Fixed whole candidate bytes plus raw original operand ledger and LLVM byte/IR readback; not independent ISA semantics proof',
                order_deltas=[
                    'Candidate allocates 16-byte frame and stores RA before the fresh slot read; original reads slot before SP decrement and later RA store',
                    'Candidate transiently shifts A1 then moves A2, and moves destination into A4 at a different point; original shifts directly into A2',
                    'Candidate writes A0=0 before restoring RA; original restores RA before A0=0'],
                dynamic_provider_identity_proved=False, dynamic_callee_ABI_proved=False,
                static_UND_zero_does_not_prove_dynamic_provider=True, full_original_ABI_proved=False,
                whole_code_equal_original=False, fault_IRQ_equivalence=False, installed_ROM_proved=False,
                physical_placement_proved=False, independent_ISA_semantics_proof=False, target_execution=False,
                HOST_tests_run=False, MMIO_execution=False, network=False, BIN_generated=False, rebuilt_flashable_BIN=False)


def replay(root, receipt):
    folder = receipt.parent
    need(folder.is_relative_to(HERE / 'build'), 'Owned static component receipt')
    record = json.loads(receipt.read_bytes())
    artifacts = {path.relative_to(folder).as_posix(): sha(path) for path in folder.rglob('*') if path.is_file() and path != receipt}
    need(record['artifacts'] == artifacts, 'Whole actual artifact inventory')
    actual = inspect(root, folder, record)
    need(actual == record['result'], 'Exact read-only actual object/IR/component replay')
    return actual


def run(argv, folder, label):
    env = dict(os.environ, TMP=str(folder / 'compiler-temp'), TEMP=str(folder / 'compiler-temp'))
    try:
        result = subprocess.run([str(x) for x in argv], cwd=folder, capture_output=True, timeout=120, env=env)
    except subprocess.TimeoutExpired as error:
        (folder / (label + '.log')).write_bytes((error.stdout or b'') + (error.stderr or b''))
        (folder / 'terminal-failure.json').write_bytes((json.dumps(dict(label=label, timed_out=True, retry_performed=False), indent=2) + '\n').encode())
        raise
    log = folder / (label + '.log')
    log.write_bytes(result.stdout + result.stderr)
    if result.returncode:
        (folder / 'terminal-failure.json').write_bytes((json.dumps(dict(label=label, exit=result.returncode, retry_performed=False), indent=2) + '\n').encode())
    need(result.returncode == 0, label + ' failed; retain local artifacts and stop')
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
    need(HERE == root / 'experiments/tsl9-nv-read-registers', 'Canonical model root')
    if a.replay:
        need(not a.tool_dir and not a.firmware and not a.build_root, 'Read-only replay arguments')
        print(json.dumps(replay(root, a.replay.resolve())))
        return
    need(a.tool_dir and a.firmware and a.build_root, 'Explicit local LLVM, original firmware and new output')
    firmware = a.firmware.resolve()
    need(sha(firmware) == IMAGE_SHA and sha(root / PARSER) == PARSER_SHA and sha(root / LEDGER) == LEDGER_SHA,
         'Original firmware/ledger/reader identities before any compile')
    need(sha(HERE / 'src/read_registers.c') == SOURCE_SHA and sha(HERE / 'component.ld') == LINKER_SHA,
         'Fixed candidate source and component script before compile')
    tools = {name: (a.tool_dir / (name + ('.exe' if os.name == 'nt' else ''))).resolve() for name in TOOLS}
    need(all(sha(tools[name]) == pin for name, pin in TOOLS.items()), 'Existing exact local LLVM tools')
    need(sha(tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h') == STDINT_SHA, 'Pinned existing compiler stdint resource')
    output = a.build_root.resolve()
    need(output.is_relative_to(HERE / 'build') and not output.exists(), 'New owned create-only build')
    frozen = pins(root, firmware, tools)
    output.mkdir(parents=True)
    summary = []
    for mode in ('c', 'cpp'):
        folder = output / mode
        folder.mkdir()
        (folder / 'compiler-temp').mkdir()
        commands = [run(argv, folder, label) for label, argv in recipes(tools, folder, mode)]
        record = dict(schema='TSL9-NV-read-register-static-component-v1', mode=mode, firmware=str(firmware),
                      tools={name: str(path) for name, path in tools.items()}, inputs=frozen, commands=commands)
        stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
        record['compiler_dependencies'] = dependencies(folder, stdint)
        record['result'] = inspect(root, folder, record)
        need(frozen == pins(root, firmware, tools), 'Before/after immutable input hashes')
        record['artifacts'] = {path.relative_to(folder).as_posix(): sha(path) for path in folder.rglob('*') if path.is_file()}
        receipt = folder / 'verification.json'
        receipt.write_bytes((json.dumps(record, indent=2) + '\n').encode())
        actual = replay(root, receipt)
        summary.append(dict(mode=mode, receipt=str(receipt), receipt_sha256=sha(receipt),
                            candidate_code_sha256=actual['candidate_code_sha256'], passed=True,
                            whole_code_equal_original=False, dynamic_provider_identity_proved=False,
                            full_original_ABI_proved=False))
    print(json.dumps(dict(passed=True, build_root=str(output), results=summary, target_execution=False)))


if __name__ == '__main__':
    main()
