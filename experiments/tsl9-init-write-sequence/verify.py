#!/usr/bin/env python3
"""Build/static-read a 40-byte RV32 C/C++ component; never execute the target."""
import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-init-write-sequence'
SYMBOL = 'tsl9_init_writes_9f4c'
SOURCE = MODEL + '/src/init_writes.c'
SOURCE_PIN = 'e318deef8975d25c84b16489388eb5cc1506a0752f362c2ca336de32d315955a'
LINKER_PIN = '24d23198a31fbe7338b058a16b3e5315757de0832b4756df790dce18fa7ccdb8'
PARSER = 'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py'
PARSER_PIN = '00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
FIRMWARE = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_PIN = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE_PIN = '59ac44eddd4fe4b479d624b08d57d3a8eea6b0cfd273db45b22ec972bb0e38d7'
STDINT_PIN = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
TOOLS = {
    'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
ROWS = [
    ('1567', 'lui a4,0x5'), ('b7370040', 'lui a5,0x40003'),
    ('13075755', 'addi a4,a4,1365'), ('98c3', 'sw a4,0(a5)'),
    ('0d47', 'li a4,3'), ('d8c3', 'sw a4,4(a5)'),
    ('1307c05d', 'li a4,1500'), ('98c7', 'sw a4,8(a5)'),
    ('2d67', 'lui a4,0xb'), ('1307a7aa', 'addi a4,a4,-1366'),
    ('98c3', 'sw a4,0(a5)'), ('3567', 'lui a4,0xd'),
    ('1307c7cc', 'addi a4,a4,-820'), ('98c3', 'sw a4,0(a5)'), ('8280', 'ret'),
]
ORIGINAL = bytes.fromhex(''.join(row[0] for row in ROWS))
NEIGHBOR = bytes.fromhex('a387010a8280')
EXPECTED_IR = '''%1 = tail call i32 asm sideeffect "", "={x14},{x14},~{memory}"(i32 20480)
%2 = tail call { i32, i32 } asm sideeffect "", "={x14},={x15},{x14},{x15},~{memory}"(i32 %1, i32 1073754112)
%3 = extractvalue { i32, i32 } %2, 0
%4 = extractvalue { i32, i32 } %2, 1
%5 = inttoptr i32 %4 to ptr
%6 = add i32 %3, 1365
store volatile i32 %6, ptr %5, align 4
%7 = getelementptr inbounds i32, ptr %5, i32 1
store volatile i32 3, ptr %7, align 4
%8 = getelementptr inbounds i32, ptr %5, i32 2
store volatile i32 1500, ptr %8, align 4
store volatile i32 43690, ptr %5, align 4
store volatile i32 52428, ptr %5, align 4
tail call void asm sideeffect "", "{x14},{x15},~{memory}"(i32 52428, i32 %4)
ret void
'''
ARTIFACTS = {'native.o', 'native.ll', 'native.d', 'COMPONENT-ONLY-NOT-FIRMWARE.elf',
             'compile.log', 'IR.log', 'link.log', 'objdump.log'}


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def portable(value, root, tools, header):
    text = str(value).replace('\\', '/')
    for base, token in [(header.parent, '${CLANG_INCLUDE}'),
                        (tools['clang'].parent, '${LLVM_BIN}'), (root, '${PROJECT_ROOT}')]:
        prefix = base.as_posix()
        if text == prefix or text.startswith(prefix + '/'):
            return token + text[len(prefix):]
    return text


def portable_record(value):
    """Reject absolute/escaped personal paths in all receipt keys and values."""
    if isinstance(value, dict):
        for key, item in value.items():
            portable_record(key)
            portable_record(item)
    elif isinstance(value, list):
        for item in value:
            portable_record(item)
    elif isinstance(value, str):
        need(not re.search(r'(?i)([a-z]:[/\\]|/(?:users|home)/|\\\\)', value)
             and not value.startswith('/'), 'Portable receipt paths only')


def flags(mode):
    need(mode in ('c', 'cpp'), 'Known language mode')
    return ['--target=riscv32-unknown-elf', '-march=rv32imac_zicsr_zifencei', '-mabi=ilp32',
            '-Oz', '-mllvm', '-enable-machine-outliner=never', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
            '-mno-relax', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror',
            *['-ffixed-x' + str(n) for n in range(1, 32) if n not in {14, 15}],
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17',
            *(['-fno-exceptions'] if mode == 'cpp' else [])]


def recipes(root, tools, folder, mode):
    source = root / SOURCE
    common = [tools['clang'], *flags(mode)]
    return [
        ('compile', [*common, '-c', '-MD', '-MF', folder / 'native.d', '-MT', 'native.o',
                     source, '-o', folder / 'native.o']),
        ('IR', [*common, '-S', '-emit-llvm', source, '-o', folder / 'native.ll']),
        ('link', [tools['ld.lld'], '--no-relax', '-T', HERE / 'component.ld', folder / 'native.o',
                  '-o', folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
        ('objdump', [tools['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r',
                     folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
    ]


def load(root, tool_dir):
    need(HERE == root / MODEL, 'Canonical component root')
    need(sha(root / SOURCE) == SOURCE_PIN, 'Reviewed current C source')
    need(sha(HERE / 'component.ld') == LINKER_PIN, 'Reviewed component linker')
    need(sha(root / PARSER) == PARSER_PIN, 'Pinned bounded static ELF parser')
    tools = {name: (tool_dir / (name + ('.exe' if os.name == 'nt' else ''))).resolve()
             for name in TOOLS}
    need(all(sha(tools[n]) == pin for n, pin in TOOLS.items()), 'Pinned existing LLVM executables')
    header = tools['clang'].parent.parent / 'lib/clang/18/include/stdint.h'
    need(sha(header) == STDINT_PIN, 'Pinned freestanding stdint resource')
    reader = runpy.run_path(str(root / PARSER))['ELF']
    return tools, header, reader


def inputs(root, tools, header):
    paths = [Path(__file__).resolve(), root / SOURCE, HERE / 'component.ld', root / PARSER,
             root / FIRMWARE, header, *tools.values()]
    return {portable(p, root, tools, header): sha(p) for p in sorted(paths)}


def original(root):
    image = (root / FIRMWARE).read_bytes()
    need(len(image) == 76800 and digest(image) == IMAGE_PIN, 'Exact original Runtime image')
    need(image[0x1f4c:0x1f74] == ORIGINAL and digest(ORIGINAL) == CODE_PIN,
         'Original 40-byte function at declared base 0x8000')
    need(image[0x1f74:0x1f7a] == NEIGHBOR, 'Adjacent six-byte function; no padding')
    return dict(image_sha256=IMAGE_PIN, image_bytes=len(image), base='0x8000',
                function_VA='[0x9f4c,0x9f74)', file_offset='0x1f4c',
                function_bytes=40, instructions=15, code_sha256=CODE_PIN,
                next_function_VA='[0x9f74,0x9f7a)', next_function_hex=NEIGHBOR.hex(),
                next_function_sha256=digest(NEIGHBOR), padding_bytes=0)


def dependency_closure(root, folder, tools, header):
    text = (folder / 'native.d').read_text(encoding='utf-8').replace('\\\n', ' ')
    target, separator, tail = text.partition(':')
    paths = {Path(re.sub(r'\\(.)', r'\1', token)).resolve()
             for token in re.findall(r'(?:\\.|[^\s])+', tail)}
    need(separator and target == 'native.o' and paths == {root / SOURCE, header},
         'Exact compiler-observed source and stdint closure')
    return {portable(p, root, tools, header): sha(p) for p in sorted(paths)}


def code_contract(code):
    need(code == ORIGINAL, 'Exact complete 40-byte instruction trace')
    rows = []
    cursor = 0x9f4c
    for raw, instruction in ROWS:
        width = len(bytes.fromhex(raw))
        need(width == (4 if int(raw[:2], 16) & 3 == 3 else 2), 'RV32 instruction width')
        rows.append(dict(VA=hex(cursor), bytes=width, hex=raw, instruction=instruction))
        cursor += width
    need(cursor == 0x9f74 and len(rows) == 15, 'Exact function boundary and instruction count')
    return rows


def ir_contract(text):
    matches = re.findall(r'define[^\n]*@([^ (]+)\([^)]*\)[^{]*\{(.*?)\n\}', text, re.S)
    need(len(matches) == 1 and matches[0][0] == SYMBOL, 'One actual IR function')
    need(re.search(r'define dso_local void @' + SYMBOL + r'\(\) #0 \{', text) is not None,
         'Exact public void IR signature')
    lines = []
    for raw in matches[0][1].splitlines():
        line = raw.split(';', 1)[0].strip()
        line = re.sub(r', ![A-Za-z.]+ !\d+', '', line)
        line = re.sub(r' #\d+\b', '', line)
        if line:
            lines.append(re.sub(r'\s+', ' ', line))
    body = '\n'.join(lines) + '\n'
    need(body == EXPECTED_IR, 'Exact ordered volatile-word and empty-register-port IR')
    need(text.count('asm sideeffect ""') == 3 and text.count('store volatile i32 ') == 5,
         'Exactly three empty ports and five volatile word stores')
    globals_ = [line for line in text.splitlines() if line.startswith('@')]
    need(globals_ == ['@llvm.compiler.used = appending global [1 x ptr] [ptr @' + SYMBOL
                     + '], section "llvm.metadata"'], 'Only compiler-used IR metadata global')
    need(not re.search(r'^(?:declare|module asm|@.*(?:alias|ifunc))\b', text, re.M),
         'No external IR function, module assembly or alias')
    return dict(normalized_body_sha256=digest(body.encode()), body_lines=len(lines),
                volatile_i32_stores=5, empty_asm_ports=3, normal_return=True,
                asm_ports_emit_instructions=False, loads=0, calls_to_target_functions=0)


def expected_symbols(linked):
    owner = 1 if linked else 3
    value = 0x9f4c if linked else 0
    rows = [('', 0, 0, 0, 0, 0), ('init_writes.c', 0, 0, 4, 0, 0xfff1),
            ('$x.0', value, 0, 0, 0, owner)]
    if not linked:
        rows.append(('$d.1', 0, 0, 0, 0, 4))
    rows.extend([('$d.2', 0, 0, 0, 0, 0xfff1 if linked else 6),
                 (SYMBOL, value, 40, 18, 0, owner)])
    keys = ('name', 'value', 'size', 'info', 'other', 'index')
    return [dict(zip(keys, row)) for row in rows]


def expected_sections(linked):
    # name/type/flags/address/size/alignment/entry-size, including empty sections.
    if linked:
        return [('', 0, 0, 0, 0, 0, 0), ('.text', 1, 6, 0x9f4c, 40, 2, 0),
                ('.symtab', 2, 0, 0, 80, 4, 16), ('.shstrtab', 3, 0, 0, 33, 1, 0),
                ('.strtab', 3, 0, 0, 47, 1, 0)]
    return [('', 0, 0, 0, 0, 0, 0), ('.strtab', 3, 0, 0, 137, 1, 0),
            ('.text', 1, 6, 0, 0, 2, 0), ('.text.' + SYMBOL, 1, 6, 0, 40, 2, 0),
            ('.comment', 1, 48, 0, 159, 1, 1), ('.note.GNU-stack', 1, 0, 0, 0, 1, 0),
            ('.riscv.attributes', 0x70000003, 0, 0, 64, 1, 0),
            ('.llvm_addrsig', 0x6fff4c03, 0x80000000, 0, 1, 1, 0),
            ('.symtab', 2, 0, 0, 96, 4, 16)]


def elf_contract(elf, linked):
    need(elf.kind == (2 if linked else 1) and elf.flags == 1, 'Exact ELF kind and RVC ABI')
    header = struct.unpack_from('<16sHHIIIIIHHHHHH', elf.raw)
    need(header[4] == (0x9f4c if linked else 0), 'Exact ELF entry')
    need(header[3] == 1 and header[8] == 52 and header[11] == 40, 'ELF version and header sizes')
    need(elf.symbols == expected_symbols(linked), 'Exact symbol inventory; no UND/ABS providers')
    need(not elf.relocations and not any(s['type'] in (4, 9) for s in elf.sections),
         'Zero relocation records or relocation sections')
    fields = ('name', 'type', 'flags', 'address', 'size', 'alignment', 'entry_size')
    sections = [tuple(s[k] for k in fields) for s in elf.sections]
    need(sections == expected_sections(linked), 'Exact complete section metadata')
    symbol = elf.symbols[-1]
    rows = code_contract(elf.function_bytes(symbol))
    programs = []
    need(header[10] == (4 if linked else 0) and header[9] == (32 if linked else 0),
         'Exact program header count and size')
    for index in range(header[10]):
        programs.append(list(struct.unpack_from('<8I', elf.raw, header[5] + 32 * index)))
    expected = [[6, 52, 0x9034, 0x9034, 128, 128, 4, 4],
                [1, 0, 0x9000, 0x9000, 180, 180, 4, 4096],
                [1, 3916, 0x9f4c, 0x9f4c, 40, 40, 5, 4096],
                [0x6474e551, 0, 0, 0, 0, 0, 6, 0]] if linked else []
    need(programs == expected, 'Exact program mapping; no extra load or writable code')
    return dict(kind='linked' if linked else 'object', entry=hex(header[4]),
                code_sha256=CODE_PIN, function_bytes=40, instructions=len(rows),
                function_value=hex(symbol['value']), global_functions=1, UND_providers=0,
                ABS_providers=0, local_ABS_metadata=sum(s['index'] == 0xfff1 for s in elf.symbols),
                relocations=0, allocated_bytes=40, alignment=2,
                symbols=elf.symbols, sections=[dict(zip(fields, row)) for row in sections],
                program_headers=programs, instruction_rows=rows)


class MemoryFile:
    def __init__(self, data):
        self.data = data

    def read_bytes(self):
        return self.data


def negative_controls(reader, obj, linked, ir):
    results = []

    def reject(name, function, message):
        try:
            function()
        except ValueError as error:
            need(str(error) == message, 'Negative control reached its intended contract: ' + name)
            results.append(dict(name=name, rejected=True, gate=message))
        else:
            raise ValueError('Negative control was accepted: ' + name)

    def patched_code(offset, value):
        code = bytearray(ORIGINAL)
        code[offset:offset + len(value)] = value
        return bytes(code)

    for name, code in [('changed_1500_literal', patched_code(18, b'\xc0\x5c')),
                       ('changed_offset8_store', patched_code(20, b'\x98\xc3')),
                       ('changed_store_width_opcode', patched_code(10, b'\x98\xa3')),
                       ('missing_return', ORIGINAL[:-2]),
                       ('reordered_initial_boundaries', ORIGINAL[2:6] + ORIGINAL[:2] + ORIGINAL[6:])]:
        reject(name, lambda code=code: code_contract(code), 'Exact complete 40-byte instruction trace')

    def patch_elf(elf, offset, format_, value):
        raw = bytearray(elf.raw)
        struct.pack_into(format_, raw, offset, value)
        return reader(MemoryFile(bytes(raw)))

    reject('wrong_linked_entry', lambda: elf_contract(patch_elf(linked, 24, '<I', 0x9f4e), True),
           'Exact ELF entry')
    section_offset = struct.unpack_from('<I', obj.raw, 32)[0]
    reject('wrong_code_alignment', lambda: elf_contract(patch_elf(obj, section_offset + 3 * 40 + 32,
                                                                 '<I', 4), False),
           'Exact complete section metadata')
    # Convert the genuine empty GNU-stack section into a zero-entry RELA
    # section in memory. The parser accepts it, and the component gate must
    # reject even an empty relocation section. No mutant file is written.
    altered = bytearray(obj.raw)
    relocation_header = section_offset + 5 * 40
    for offset, value in [(4, 4), (24, 8), (28, 3), (36, 12)]:
        struct.pack_into('<I', altered, relocation_header + offset, value)
    reject('unexpected_relocation_section', lambda: elf_contract(reader(MemoryFile(bytes(altered))), False),
           'Zero relocation records or relocation sections')
    symbol_offset = obj.byname['.symtab']['offset'] + 5 * 16
    reject('undefined_function_provider', lambda: elf_contract(patch_elf(obj, symbol_offset + 14,
                                                                       '<H', 0), False),
           'Exact symbol inventory; no UND/ABS providers')
    for name, changed in [('nonvolatile_store', ir.replace('store volatile i32', 'store i32', 1)),
                          ('halfword_IR_store', ir.replace('store volatile i32 1500', 'store volatile i16 1500')),
                          ('changed_IR_literal', ir.replace('i32 1500', 'i32 1501')),
                          ('nonempty_port', ir.replace('asm sideeffect ""', 'asm sideeffect "nop"', 1))]:
        reject(name, lambda changed=changed: ir_contract(changed),
               'Exact ordered volatile-word and empty-register-port IR')
    return results


def objdump_contract(folder):
    text = (folder / 'objdump.log').read_text(encoding='utf-8')
    rows = []
    for line in text.splitlines():
        match = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)', line)
        if match:
            rows.append((int(match[1], 16), bytes.fromhex(match[2])))
    expected = []
    cursor = 0x9f4c
    for raw, _ in ROWS:
        data = bytes.fromhex(raw)
        expected.append((cursor, data))
        cursor += len(data)
    need(rows == expected and '<' + SYMBOL + '>:' in text,
         'Actual objdump complete original instruction byte projection')
    return dict(instructions=len(rows), bytes=sum(len(row[1]) for row in rows))


def inventory(folder):
    need(all(path.is_file() for path in folder.iterdir()), 'No unrecorded build subdirectories')
    actual = {path.name: sha(path) for path in sorted(folder.iterdir())
              if path.name != 'verification.json'}
    need(set(actual) == ARTIFACTS, 'Exact complete artifact and raw-log inventory')
    return actual


def record(root, folder, mode, tools, header, reader):
    before = inputs(root, tools, header)
    originals = original(root)
    closure = dependency_closure(root, folder, tools, header)
    commands = [dict(label=label, argv=[portable(x, root, tools, header) for x in argv],
                     exit=0, log_sha256=sha(folder / (label + '.log')))
                for label, argv in recipes(root, tools, folder, mode)]
    need(all((folder / (label + '.log')).read_bytes() == b'' for label in ('compile', 'IR', 'link')),
         'Warning-free successful compiler/linker logs')
    obj = reader(folder / 'native.o')
    linked = reader(folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf')
    ir = (folder / 'native.ll').read_text(encoding='utf-8')
    ir_facts = ir_contract(ir)
    facts = [elf_contract(obj, False), elf_contract(linked, True)]
    controls = negative_controls(reader, obj, linked, ir)
    disassembly = objdump_contract(folder)
    after = inputs(root, tools, header)
    need(before == after, 'Unchanged inputs during full static inspection')
    result = dict(passed=True, actual_ELFs=2, source_original_equal=True,
                  ELF_facts=facts, IR=ir_facts, objdump=disassembly,
                  writes=[dict(address=hex(address), value=hex(value), bits=32)
                          for address, value in [(0x40003000, 0x5555), (0x40003004, 3),
                                                 (0x40003008, 1500), (0x40003000, 0xaaaa),
                                                 (0x40003000, 0xcccc)]],
                  normal_exit_GPR={'a4': '0xcccc', 'a5': '0x40003000'},
                  other_GPR_unchanged=True, SP_frame_bytes=0, calls=0, CSR_accesses=0,
                  local_instruction_trace_equal=True, firmware_ready=False,
                  global_fault_IRQ_equivalence=False, physical_chip_identified=False,
                  installed_ROM_proved=False, whole_firmware_equivalence=False,
                  limitations=['Physical peripheral identity and timing are unproved.',
                               'Caller, installed resident ROM, full image closure and physical placement are unproved.',
                               'A component ELF is not an OTA or flashable firmware image.'],
                  target_execution=False, ISA_emulation=False, MMIO_execution=False,
                  hardware=False, network=False, BIN_generated=False)
    value = dict(schema='TSL9-init-write-sequence-static-v1', mode=mode,
                 firmware='${PROJECT_ROOT}/' + FIRMWARE,
                 tools={name: portable(path, root, tools, header) for name, path in tools.items()},
                 inputs_before=before, inputs_after=after, compiler_dependencies=closure,
                 commands=commands, original=originals, artifacts=inventory(folder),
                 negative_controls=controls, result=result)
    portable_record(value)
    return value


def replay(root, receipt, tools, header, reader):
    need(receipt.name == 'verification.json' and receipt.parent.is_relative_to(HERE / 'build')
         and receipt.parent.name in ('c', 'cpp'), 'Owned complete receipt location')
    saved = json.loads(receipt.read_bytes())
    actual = record(root, receipt.parent, receipt.parent.name, tools, header, reader)
    need(actual == saved, 'Complete read-only reconstructed record equality')
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--tool-dir', type=Path, default=os.environ.get('TSL9_LLVM_BIN'))
    parser.add_argument('--build-root', type=Path)
    parser.add_argument('--replay', type=Path)
    parser.add_argument('--require-firmware-ready', action='store_true')
    args = parser.parse_args()
    root = args.project_root.resolve()
    need(args.tool_dir is not None, 'Set TSL9_LLVM_BIN or provide the existing pinned LLVM --tool-dir')
    tools, header, reader = load(root, Path(args.tool_dir).resolve())
    if args.replay:
        need(args.build_root is None, 'Read-only replay cannot build')
        value = replay(root, args.replay.resolve(), tools, header, reader)
        need(not args.require_firmware_ready, 'Firmware readiness is not established; component only')
        print(json.dumps(dict(passed=True, read_only_replay=True, actual_ELFs=2,
                              negative_controls=len(value['negative_controls']), firmware_ready=False,
                              receipt_sha256=sha(args.replay.resolve()))))
        return
    need(not args.require_firmware_ready, 'Firmware readiness is not established; component only')
    need(args.build_root is not None, 'Explicit new owned --build-root required')
    out = args.build_root.resolve()
    need(out.is_relative_to(HERE / 'build') and not out.exists(), 'New owned build directory required')
    frozen = inputs(root, tools, header)
    original(root)
    out.mkdir(parents=True)
    receipts = []
    for mode in ('c', 'cpp'):
        folder = out / mode
        folder.mkdir()
        for label, argv in recipes(root, tools, folder, mode):
            actual = subprocess.run([str(x) for x in argv], cwd=root, capture_output=True, timeout=120)
            (folder / (label + '.log')).write_bytes(actual.stdout + actual.stderr)
            need(actual.returncode == 0, 'Local build command failed; inspect ' + label + '.log')
            need(inputs(root, tools, header) == frozen, 'Unchanged pre/post inputs for each recipe')
        value = record(root, folder, mode, tools, header, reader)
        need(value['inputs_before'] == value['inputs_after'] == frozen, 'Unchanged complete build inputs')
        receipt = folder / 'verification.json'
        receipt.write_bytes((json.dumps(value, indent=2) + '\n').encode('utf-8'))
        replay(root, receipt, tools, header, reader)
        receipts.append(dict(mode=mode, receipt=portable(receipt, root, tools, header), sha256=sha(receipt)))
    need(inputs(root, tools, header) == frozen, 'Unchanged inputs across both language builds')
    need((out / 'c/native.o').read_bytes() == (out / 'cpp/native.o').read_bytes()
         and (out / 'c/COMPONENT-ONLY-NOT-FIRMWARE.elf').read_bytes()
         == (out / 'cpp/COMPONENT-ONLY-NOT-FIRMWARE.elf').read_bytes(), 'C/C++ whole ELF byte equality')
    print(json.dumps(dict(passed=True, receipts=receipts, actual_ELFs=4,
                          negative_controls_per_mode=13, firmware_ready=False,
                          target_execution=False, BIN_generated=False)))


if __name__ == '__main__':
    main()
