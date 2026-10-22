#!/usr/bin/env python3
"""Compile and statically verify eight genuine C functions; never execute RV32."""
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
PARSER = 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_SHA = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
STDINT_SHA = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
CALLBACK = 'tsl9_nv_write_frame_contract_197be'
TIMER = 'tsl9_delay_registers_19764'
CALLEES = ['tsl9_flash_unlock_18e98', 'tsl9_flash_erase_18ec4',
           'tsl9_flash_program_18ef2', 'tsl9_flash_lock_18eb6', TIMER]
JAL_OFFSETS = [10, 16, 26, 30, 36]
# Derived directly from both actual curated-source origin/unit.o files.
# These are static readback facts, not machine-code source/carriers/providers.
HELPERS = {
    'tsl9_flash_status_18e90': (8, '4937a9406887122dfa589dbe9fee75572e5cccd9ae20f52e7f9a59e140e2c466'),
    'tsl9_flash_unlock_18e98': (30, '577bbb0f43bdde763561002757b9ab8611a578ab1fdd321e62ba13662cb992a2'),
    'tsl9_flash_lock_18eb6': (14, '20c1f57d6f8294aa24230996a9311f4a73ae3da72b0eed0acc4da3e2330ea7de'),
    'tsl9_flash_erase_18ec4': (46, '498d12fe1749927050b5dbc5077ac1704ef412e0af29d71279882b16e65e042f'),
    'tsl9_flash_program_18ef2': (100, 'b43d396fa5e302ae8bc8d41d6b3c8f0c39107e18e58304cb99e4c67458cc0df0'),
    'tsl9_flash_quarter_9c0a': (64, 'cbbeabd3161e639a253239920558fd027f2cd585838d7963e0deef3b17036942'),
}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def timer_profile(root):
    return runpy.run_path(str(root / 'experiments/tsl9-delay-register-contract/verify.py'))


def normal_flags(mode):
    return ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr_zifencei', '-mabi=ilp32', '-Oz',
            '-mllvm', '-enable-machine-outliner=never', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
            '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror',
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17',
            *(['-fno-exceptions'] if mode == 'cpp' else [])]


def sources(root):
    return {'callback': HERE / 'src/write_frame.c', 'providers': HERE / 'src/flash_provider.c',
            'timer': root / 'experiments/tsl9-delay-register-contract/src/delay.c'}


def inputs(root, firmware, tools):
    stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    paths = [Path(__file__).resolve(), HERE / 'component.ld', root / PARSER,
             root / 'experiments/tsl9-delay-register-contract/verify.py', firmware, stdint,
             *sources(root).values(), *tools.values(),
             *[root / 'src/native/nv' / name for name in ('flash_native.h', 'flash_native.c', 'native_io.h')]]
    return {str(p): sha(p) for p in paths}


def recipes(root, folder, mode, tools):
    result = [('resource', [tools['clang'], '-print-resource-dir'])]
    timer = timer_profile(root)
    for name, source in sources(root).items():
        flags = timer['flags'](mode) if name == 'timer' else normal_flags(mode)
        result += [
            ('compile-' + name, [tools['clang'], *flags, '-c', '-MD', '-MF', folder / (name + '.d'),
                                '-MT', name + '.o', source, '-o', folder / (name + '.o')]),
            ('IR-' + name, [tools['clang'], *flags, '-S', '-emit-llvm', source, '-o', folder / (name + '.ll')]),
            ('disassemble-' + name, [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei',
                                    '-d', '-r', folder / (name + '.o')])]
    result += [
        ('link', [tools['ld.lld'], '--no-relax', '-T', HERE / 'component.ld',
                  *[folder / (name + '.o') for name in sources(root)],
                  '-o', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
        ('disassemble-linked', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei',
                                '-d', '-r', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf'])]
    return result


def md(root, folder, stdint):
    result = {}
    for name, source in sources(root).items():
        text = (folder / (name + '.d')).read_text(encoding='utf-8').replace('\\\n', ' ')
        target, sep, tail = text.partition(':')
        paths = {Path(re.sub(r'\\(.)', r'\1', token)).resolve()
                 for token in re.findall(r'(?:\\.|[^\s])+', tail)}
        expected = {source, stdint}
        if name == 'providers':
            expected.update(root / 'src/native/nv' / n for n in ('flash_native.h', 'flash_native.c', 'native_io.h'))
        need(sep and target == name + '.o' and paths == expected, 'Complete actual MD closure: ' + name)
        result[name] = {str(p): sha(p) for p in sorted(paths)}
    return result


def functions(elf):
    defs = [s for s in elf.symbols if s['info'] & 15 == 2 and s['index'] not in (0, 0xfff1) and s['size']]
    need(len({s['name'] for s in defs}) == len(defs) and all(s['info'] >> 4 == 1 for s in defs),
         'Every emitted function is a uniquely inventoried genuine global')
    return {s['name']: s for s in defs}


def inventory(elf, expected, kind, mode):
    found = functions(elf)
    need(set(found) == set(expected) and elf.kind == kind and elf.flags == 1, 'Exact actual global functions and RV32/RVC ELF kind')
    undefined = sorted({s['name'] for s in elf.symbols if s['index'] == 0 and s['name'] and s['info'] >> 4 in (1, 2)})
    absolute = sorted({s['name'] for s in elf.symbols if s['index'] == 0xfff1 and s['info'] >> 4 in (1, 2)})
    need(not absolute, 'No ABS provider')
    allocated = [s for s in elf.sections if s['flags'] & 2 and s['size']]
    need(all(s['type'] == 1 and not s['flags'] & 1 and
             (s['flags'] == 6 or (mode == 'cpp' and s['name'] == '.eh_frame' and s['flags'] == 2))
             for s in allocated), 'All allocation is real code or explicit C++ read-only unwind metadata')
    unwind = [s for s in allocated if not s['flags'] & 4]
    expected_unwind = 40 if mode == 'cpp' and kind == 1 and set(expected) == {TIMER} else 44 if mode == 'cpp' and kind == 2 else 0
    need([(s['name'], s['size'], s['flags'], s['type']) for s in unwind] ==
         ([('.eh_frame', expected_unwind, 2, 1)] if expected_unwind else []), 'Exact compiler unwind allocation; no extra metadata carriers')
    need(sum(s['size'] for s in allocated if s['flags'] & 4) == sum(s['size'] for s in found.values()),
         'No unowned executable carriers, padding or hidden functions')
    return dict(kind=elf.kind, global_functions=[dict(name=n, bytes=s['size'], value=s['value'],
                code_sha256=digest(elf.function_bytes(s))) for n, s in sorted(found.items())],
                allocated_sections=[{k:s[k] for k in ('name', 'size', 'flags', 'type', 'address')} for s in allocated],
                allocated_bytes=sum(s['size'] for s in allocated), UND=undefined,
                global_ABS=absolute, RELA=elf.relocations)


def llvm_rows(elf, log):
    sections = {s['name']: s for s in elf.sections if s['flags'] & 4 and s['size']}
    covered = {n: 0 for n in sections}
    result = {n: [] for n in sections}
    current = None
    for line in log.read_text(encoding='utf-8').splitlines():
        head = re.match(r'Disassembly of section (.+):', line)
        if head:
            current = head[1]
            continue
        match = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)', line)
        if not match:
            continue
        need(current in sections, 'No disassembled code outside executable sections')
        section = sections[current]
        at, raw = int(match[1], 16), bytes.fromhex(match[2])
        offset = at - section['address'] if elf.kind == 2 else at
        need(offset == covered[current] and len(raw) in (2, 4) and
             raw == elf.data(section)[offset:offset + len(raw)] and match[3] not in ('<unknown>', '.word', '.2byte'),
             'Complete contiguous actual LLVM raw-byte coverage')
        result[current].append(dict(address=at, raw=raw.hex(), mnemonic=match[3], operands=match[4]))
        covered[current] += len(raw)
    need(all(covered[n] == s['size'] for n, s in sections.items()), 'No omitted executable bytes')
    return result


def jal_target(code, offset, pc):
    word = int.from_bytes(code[offset:offset + 4], 'little')
    need(word & 0xfff == 0x0ef, 'Actual JAL ra instruction')
    imm = ((word >> 31) << 20) | (((word >> 21) & 1023) << 1) | (((word >> 20) & 1) << 11) | (((word >> 12) & 255) << 12)
    if imm & (1 << 20):
        imm -= 1 << 21
    return (pc + imm) & 0xffffffff


def mask_jal_immediates(code, offsets):
    value = bytearray(code)
    for offset in offsets:
        word = int.from_bytes(value[offset:offset + 4], 'little')
        need(word & 0xfff == 0x0ef, 'Preserve JAL opcode and RA destination while masking only immediate bits')
        value[offset:offset + 4] = (word & 0xfff).to_bytes(4, 'little')
    return bytes(value)


def inspect(root, folder, record):
    tools = {n: Path(p) for n, p in record['tools'].items()}
    need(record['schema'] == 'TSL9-NV-write-frame-static-component-v1' and record['mode'] in ('c', 'cpp'), 'Known actual receipt')
    need(set(tools) == set(TOOLS) and all(sha(tools[n]) == h for n, h in TOOLS.items()), 'Exact existing LLVM tool hashes')
    firmware = Path(record['firmware'])
    need(sha(firmware) == IMAGE_SHA and sha(root / PARSER) == PARSER_SHA, 'Exact original firmware and separate read-only ELF reader')
    need(record['inputs'] == inputs(root, firmware, tools), 'Stable full source/tool/resource/firmware input closure')
    stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    need(sha(stdint) == STDINT_SHA and record['compiler_dependencies'] == md(root, folder, stdint), 'Actual complete compiler MD closure')
    expected_commands = recipes(root, folder, record['mode'], tools)
    need(len(record['commands']) == len(expected_commands), 'Complete single-profile command history')
    for command, (label, argv) in zip(record['commands'], expected_commands):
        need(command == dict(label=label, argv=[str(x) for x in argv], exit=0,
                             log_sha256=sha(folder / (label + '.log'))),
             'Exact successful compiler/link/disassembly recipe and log')
    need(Path((folder / 'resource.log').read_text().strip()) / 'include/stdint.h' == stdint, 'Actual compiler resource directory')
    Reader = runpy.run_path(str(root / PARSER))['ELF']
    objects = {name: Reader(folder / (name + '.o')) for name in sources(root)}
    linked = Reader(folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf')
    sets = {'callback': {CALLBACK}, 'providers': set(HELPERS), 'timer': {TIMER}}
    facts = {name: inventory(elf, sets[name], 1, record['mode']) for name, elf in objects.items()}
    facts['linked'] = inventory(linked, set(HELPERS) | {CALLBACK, TIMER}, 2, record['mode'])
    need(facts['callback']['UND'] == sorted(CALLEES) and not facts['providers']['UND'] and not facts['timer']['UND'],
         'Callback requires only the five real providers; all genuine provider units are defined')
    need(not facts['linked']['UND'] and not linked.relocations, 'Actual linked component has no unresolved symbols or relocations')
    rows = {name: llvm_rows(elf, folder / ('disassemble-' + name + '.log')) for name, elf in objects.items()}
    rows['linked'] = llvm_rows(linked, folder / 'disassemble-linked.log')
    cb = objects['callback']; cb_def = functions(cb)[CALLBACK]; code = cb.function_bytes(cb_def)
    relocations = cb.relocations
    need(len(relocations) == 5 and [(r['offset'], r['type'], r['symbol']['name'], r['addend']) for r in relocations]
         == [(o, 17, n, 0) for o, n in zip(JAL_OFFSETS, CALLEES)], 'Exactly five actual callback R_RISCV_JAL calls')
    image = firmware.read_bytes()
    original = image[0x117be:0x117f0]
    original_timer = image[0x11764:0x1179a]
    need(digest(original) == '3151a48b2f1025b196bfaf5de65799da21b9f699d3049d88879e4c4d3a5a8426'
         and len(code) == len(original) == 50, 'Exact original and candidate callback extents')
    need(mask_jal_immediates(code[:40], JAL_OFFSETS) == mask_jal_immediates(original[:40], JAL_OFFSETS),
         'First 40 bytes match original with only five JAL immediate fields masked')
    need(original[40:].hex() == 'f2406244014505618280' and code[40:].hex() == '0145f240624405618280',
         'Known remaining return-zero / saved-register-restore ordering delta')
    provider_defs = functions(objects['providers'])
    for name, (size, pin) in HELPERS.items():
        actual = objects['providers'].function_bytes(provider_defs[name])
        need(len(actual) == size and digest(actual) == pin, 'Actual genuine helper body equals retained origin object: ' + name)
    provider_ir = (folder / 'providers.ll').read_text(encoding='utf-8')
    for name in CALLEES[:2]:
        match = re.search(r'asm sideeffect "jal ra, ' + name + r'", "([^"]+)"', provider_ir)
        need(match and '~{x11}' in match[1].split(','), 'Actual repaired A1 clobber for ' + name)
    timer = objects['timer'].function_bytes(functions(objects['timer'])[TIMER])
    need(len(timer) == 54 and timer == original_timer, 'Whole timer equals original 54 bytes under exact fixed-register recipe')
    linked_defs = functions(linked)
    need(struct.unpack_from('<I', linked.raw, 24)[0] == linked_defs[CALLBACK]['value'] == linked.byname['.text']['address'], 'Explicit callback entry at the measured nonphysical text start')
    calls = []
    for unit, elf in objects.items():
        defs = functions(elf)
        for name, definition in defs.items():
            before = elf.function_bytes(definition)
            after = linked.function_bytes(linked_defs[name])
            owned = [r for r in elf.relocations if r['owner'] == elf.sections[definition['index']]['name']]
            offsets = []
            for r in owned:
                need(r['type'] == 17 and r['addend'] == 0 and r['symbol']['name'] in linked_defs,
                     'Every code relocation is a real JAL to a genuine provider')
                offset = r['offset'] - definition['value']
                need(0 <= offset <= len(before) - 4, 'Owned call relocation bounds')
                target = linked_defs[r['symbol']['name']]['value']
                pc = linked_defs[name]['value'] + offset
                need(jal_target(after, offset, pc) == target, 'Actual linked JAL resolves to the genuine function definition')
                offsets.append(offset)
                calls.append(dict(owner=name, offset=offset, PC=pc, target=r['symbol']['name'], target_value=target))
            need(len(before) == len(after) and mask_jal_immediates(before, offsets) == mask_jal_immediates(after, offsets),
                 'All non-JAL-immediate function bits preserved through actual link')
    need(len(calls) == 10 and len([c for c in calls if c['owner'] == CALLBACK]) == 5, 'All ten genuine calls including unused quarter retained')
    need(linked.function_bytes(linked_defs[TIMER]) == original_timer, 'Linked timer remains whole-byte original equality')
    return dict(passed=True, actual_artifacts_read=True, mode=record['mode'], ELF_facts=facts,
                LLVM_rows=rows, linked_calls=calls, helper_code_hashes={n: p for n, (_, p) in HELPERS.items()},
                callback_code_sha256=digest(code), callback_bytes=50, callback_instructions=20,
                callback_first40_equal_except_JAL_immediates=True, frame_bytes=32, source_slot_offset=12,
                callback_tail_delta=dict(offset=40, original=original[40:].hex(), candidate=code[40:].hex(),
                    original_order=['restore RA', 'restore S0', 'A0=0', 'SP+=32', 'RET'],
                    candidate_order=['A0=0', 'restore RA', 'restore S0', 'SP+=32', 'RET']),
                callback_whole_bytes_equal=False, timer_entire54_bytes_equal_original=True,
                all_eight_genuine_functions_retained=True, unused_genuine_functions=['tsl9_flash_status_18e90', 'tsl9_flash_quarter_9c0a'],
                full_original_ABI_proved=False, fault_IRQ_equivalence=False, installed_ROM_proved=False,
                physical_placement_proved=False, component_VMA_is_physical=False, target_execution=False,
                HOST_tests_run=False, MMIO_execution=False, network=False, BIN_generated=False,
                rebuilt_flashable_BIN=False)


def replay(root, receipt):
    record = json.loads(receipt.read_bytes())
    folder = receipt.parent
    need(folder.is_relative_to(HERE / 'build'), 'Owned static component receipt')
    actual = {p.relative_to(folder).as_posix(): sha(p) for p in folder.rglob('*') if p.is_file() and p != receipt}
    need(record['artifacts'] == actual, 'Complete actual local artifact inventory')
    result = inspect(root, folder, record)
    need(result == record['result'], 'Exact read-only actual component replay')
    return result


def run(argv, folder, label):
    try:
        actual = subprocess.run([str(x) for x in argv], cwd=folder, capture_output=True, timeout=120,
                                env=dict(os.environ, TMP=str(folder / 'compiler-temp'), TEMP=str(folder / 'compiler-temp')))
    except subprocess.TimeoutExpired as error:
        (folder / (label + '.log')).write_bytes((error.stdout or b'') + (error.stderr or b''))
        (folder / 'terminal-failure.json').write_bytes((json.dumps(dict(label=label, timed_out=True,
              argv=[str(x) for x in argv], retry_performed=False), indent=2) + '\n').encode())
        raise
    log = folder / (label + '.log')
    log.write_bytes(actual.stdout + actual.stderr)
    if actual.returncode:
        (folder / 'terminal-failure.json').write_bytes((json.dumps(dict(label=label, exit=actual.returncode,
              argv=[str(x) for x in argv], retry_performed=False), indent=2) + '\n').encode())
    need(actual.returncode == 0, 'Actual tool failed; retain output and stop: ' + label)
    return dict(label=label, argv=[str(x) for x in argv], exit=actual.returncode, log_sha256=sha(log))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--tool-dir', type=Path)
    p.add_argument('--firmware', type=Path)
    p.add_argument('--build-root', type=Path)
    p.add_argument('--replay', type=Path)
    a = p.parse_args()
    root = a.project_root.resolve()
    need(HERE == root / 'experiments/tsl9-nv-write-frame-contract', 'Canonical model root')
    if a.replay:
        need(not a.tool_dir and not a.firmware and not a.build_root, 'Read-only replay has no generation arguments')
        print(json.dumps(replay(root, a.replay.resolve())))
        return
    need(a.tool_dir and a.firmware and a.build_root, 'Explicit local LLVM/original firmware/new build')
    firmware = a.firmware.resolve()
    need(sha(firmware) == IMAGE_SHA and sha(root / PARSER) == PARSER_SHA, 'Pinned original firmware and reader before compile')
    tools = {n: (a.tool_dir / (n + ('.exe' if os.name == 'nt' else ''))).resolve() for n in TOOLS}
    need(all(sha(tools[n]) == h for n, h in TOOLS.items()), 'Pinned LLVM before compile')
    output = a.build_root.resolve()
    need(output.is_relative_to(HERE / 'build') and not output.exists(), 'New owned create-only build')
    frozen = inputs(root, firmware, tools)
    output.mkdir(parents=True)
    summary = []
    for mode in ('c', 'cpp'):
        folder = output / mode
        folder.mkdir()
        (folder / 'compiler-temp').mkdir()
        commands = [run(argv, folder, label) for label, argv in recipes(root, folder, mode, tools)]
        record = dict(schema='TSL9-NV-write-frame-static-component-v1', mode=mode, firmware=str(firmware),
                      tools={n: str(f) for n, f in tools.items()}, inputs=frozen, commands=commands)
        stdint = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
        record['compiler_dependencies'] = md(root, folder, stdint)
        record['result'] = inspect(root, folder, record)
        need(frozen == inputs(root, firmware, tools), 'Before/after input stability')
        record['artifacts'] = {f.relative_to(folder).as_posix(): sha(f) for f in folder.rglob('*') if f.is_file()}
        receipt = folder / 'verification.json'
        receipt.write_bytes((json.dumps(record, indent=2) + '\n').encode())
        actual = replay(root, receipt)
        summary.append(dict(mode=mode, receipt=str(receipt), receipt_sha256=sha(receipt),
                            callback_code_sha256=actual['callback_code_sha256'],
                            timer_entire54_bytes_equal_original=True, callback_first40_equal_except_JAL_immediates=True,
                            callback_whole_bytes_equal=False, full_original_ABI_proved=False))
    print(json.dumps(dict(passed=True, build_root=str(output), results=summary, target_execution=False)))


if __name__ == '__main__':
    main()
