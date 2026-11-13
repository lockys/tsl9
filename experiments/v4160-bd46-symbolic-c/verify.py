#!/usr/bin/env python3
"""Offline, bounded comparison; no target execution."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
READER = ROOT / 'experiments/tsl9-feature-dispatch-tree/elf_reader-v4.py'
TOOL_DIR = Path(r'C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin')
PINS = {'clang.exe': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
        'ld.lld.exe': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
SOURCE_SHA = '39d194961f6aba4d503a3fe122a9b312e372d5e45273a4871ccaaf425d29949f'
READER_SHA = '2f7a5dc2d4eeb823e0e4c63f81b3c4fdcffe7cbb39262dc7f6731be675016b15'
BIN_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
REFERENCE = bytes.fromhex('170500201305b51c8280')
FUNC = 'tsl9_record_helpers_provider_bd46'
FLAG = 'record_flag_bd46'
ADDR = 0xbd46
WITNESS = 0x2000bf11


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path, digest):
    data = path.read_bytes()
    need(sha(data) == digest, 'hash mismatch: ' + str(path))
    return data


def reader_class():
    # Execute precisely the verified bytes, not a second file read/import.
    source = pinned(READER, READER_SHA)
    namespace = {'__name__': 'pinned_elf_reader'}
    exec(compile(source, str(READER), 'exec'), namespace)
    return namespace['ELF']


def one_symbol(elf, name):
    matches = [s for s in elf.symbols if s['name'] == name]
    need(len(matches) == 1, 'symbol count: ' + name)
    return matches[0]


def check_tables(elf):
    need(not any(s['type'] in (9, 11, 19) for s in elf.sections),
         'SHT_REL, SHT_DYNSYM and SHT_RELR forbidden')
    tables = [s for s in elf.sections if s['type'] == 2]
    need(len(tables) == 1, 'exactly one SHT_SYMTAB')
    table = tables[0]
    need(table['entsize'] == 16 and table['size'] == 16 * len(elf.symbols) and
         0 <= table['link'] < len(elf.sections) and
         elf.sections[table['link']]['type'] == 3, 'SHT_SYMTAB shape/string table')


def leaf_section(elf, address):
    section = elf.section('.leaf')
    need(section['type'] == 1 and section['flags'] == 6 and
         section['address'] == address and section['size'] == 10,
         'leaf section shape')
    return section


def function(elf, section, value):
    s = one_symbol(elf, FUNC)
    need((s['value'], s['size'], s['info'], s['other'], s['section']) ==
         (value, 10, 0x12, 0, section['index']), 'function symbol identity')


def check_object(elf):
    check_tables(elf)
    need(elf.header[0] == 1 and elf.header[3] == 0 and not elf.program_headers, 'ET_REL header')
    section = leaf_section(elf, 0)
    function(elf, section, 0)
    witness = one_symbol(elf, FLAG)
    need((witness['value'], witness['size'], witness['info'], witness['other'], witness['section']) ==
         (0, 0, 0x10, 0, 0), 'undefined witness symbol')
    relsecs = [s for s in elf.sections if s['type'] == 4]
    need(len(relsecs) == 1 and relsecs[0]['info'] == section['index'] and
         relsecs[0]['size'] == 24, 'relocation section shape')
    rel = elf.relocations
    need(len(rel) == 2, 'relocation count')
    hi, lo = rel
    need((hi['section'], hi['offset'], hi['type'], hi['symbol'], hi['addend']) ==
         (section['index'], 0, 23, witness['index'], 0), 'PCREL_HI20 target/addend')
    need((lo['section'], lo['offset'], lo['type'], lo['addend']) ==
         (section['index'], 4, 24, 0), 'PCREL_LO12_I shape')
    need(0 <= lo['symbol'] < len(elf.symbols), 'anchor index')
    anchor = elf.symbols[lo['symbol']]
    need(anchor['index'] == lo['symbol'] and anchor['info'] == 0 and anchor['other'] == 0 and
         anchor['section'] == section['index'] and anchor['value'] == hi['offset'] and
         anchor['size'] == 0, 'LO12 anchor must identify HI20 location')
    return {'hi': hi, 'lo': lo, 'hi_symbol': witness['name'], 'anchor': anchor['name']}


def check_exec(elf, witness_value):
    check_tables(elf)
    need(elf.header[0] == 2 and elf.header[3] == 0, 'ET_EXEC/entry')
    need(not any(p[0] == 1 for p in elf.program_headers), 'PT_LOAD forbidden')
    need(not elf.relocations, 'linked relocations forbidden')
    section = leaf_section(elf, ADDR)
    function(elf, section, ADDR)
    witness = one_symbol(elf, FLAG)
    need((witness['value'], witness['size'], witness['info'], witness['other'], witness['section']) ==
         (witness_value, 0, 0x10, 0, 0xfff1), 'ABS data witness')
    need(all(s['index'] == 0 or s['section'] != 0 for s in elf.symbols), 'unresolved symbol')
    return elf.data(section)


def expected_bytes(witness):
    # R_RISCV_PCREL_HI20/LO12_I, P = address of AUIPC, A = 0.
    delta = witness - ADDR
    hi = (delta + 0x800) >> 12
    lo = delta - (hi << 12)
    need(0 <= hi < (1 << 20) and -2048 <= lo <= 2047, 'relocation range')
    auipc = (hi << 12) | 0x517  # auipc a0, hi
    addi = ((lo & 0xfff) << 20) | 0x50513  # addi a0, a0, lo
    return auipc.to_bytes(4, 'little') + addi.to_bytes(4, 'little') + b'\x82\x80'


def check_bytes(payload, witness):
    expected = expected_bytes(witness)
    need(payload == expected, 'linked bytes comparison')


def run(command):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True)
    need(result.returncode == 0, 'command failed: ' + repr([str(x) for x in command]) +
         '\n' + result.stdout + result.stderr)
    return result.stdout + result.stderr


def main():
    source = pinned(HERE / 'candidate.c', SOURCE_SHA)
    original = pinned(BIN, BIN_SHA)
    need(len(original) == 76800, 'BIN length')
    need(original[ADDR - 0x8000:ADDR - 0x8000 + 10] == REFERENCE, 'BIN window')
    need(expected_bytes(WITNESS) == REFERENCE and
         expected_bytes(WITNESS + 0x1000) == bytes.fromhex('171500201305b51c8280'),
         'independent relocation expectation')
    ELF = reader_class()
    tools = {name: TOOL_DIR / name for name in PINS}
    for name, path in tools.items():
        pinned(path, PINS[name])
    versions = {name: run([path, '--version']) for name, path in tools.items()}
    report = {'bin_path': str(BIN), 'bin_sha256': BIN_SHA, 'bin_length': len(original),
              'bin_base': '0x8000', 'reference': REFERENCE.hex(),
              'source_sha256': sha(source), 'reader_sha256': READER_SHA,
              'verify_sha256': sha(Path(__file__).read_bytes()),
              'python': sys.version, 'optimize': sys.flags.optimize,
              'tool_paths': {n: str(p) for n, p in tools.items()}, 'tool_hashes': PINS,
              'tool_versions': versions, 'cases': []}
    with tempfile.TemporaryDirectory(prefix='bd46-') as td:
        temp = Path(td)
        snapshot = temp / 'candidate.c'
        snapshot.write_bytes(source)
        need(snapshot.read_bytes() == source, 'source snapshot')
        for lang, standard in [('c', 'c11'), ('c++', 'c++17')]:
            obj = temp / (standard + '.o')
            cmd = [tools['clang.exe'], '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr',
                   '-mabi=ilp32', '-mcmodel=medany', '-mno-relax', '-fno-pic', '-ffreestanding',
                   '-fno-stack-protector', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                   '-Oz', '-Wall', '-Wextra', '-Werror', '-x', lang, '-std=' + standard,
                   '-c', snapshot, '-o', obj]
            run(cmd)
            reloc = check_object(ELF(obj.read_bytes()))
            for label, value in [('positive', WITNESS), ('wrong_address', WITNESS + 0x1000)]:
                script = temp / (standard + '-' + label + '.ld')
                image = temp / (standard + '-' + label + '.elf')
                layout = ('PHDRS { none PT_NULL; }\n' + FLAG + ' = 0x%x;\n' % value +
                          'SECTIONS { .leaf 0xbd46 : { *(.leaf) } :none }\n')
                script.write_text(layout, encoding='ascii')
                link = [tools['ld.lld.exe'], '--no-relax', '-T', script, '-o', image, obj]
                run(link)
                payload = check_exec(ELF(image.read_bytes()), value)
                check_bytes(payload, value)
                report['cases'].append({'language': standard, 'case': label, 'witness': hex(value),
                                        'compile': [str(x).replace(str(temp), '<temp>') for x in cmd],
                                        'link': [str(x).replace(str(temp), '<temp>') for x in link],
                                        'linker_script': layout, 'object_sha256': sha(obj.read_bytes()),
                                        'elf_sha256': sha(image.read_bytes()), 'relocations': reloc,
                                        'bytes': payload.hex(), 'exact': payload == REFERENCE})
    need(len(report['cases']) == 4, 'empty/incomplete case matrix')
    report['passed'] = True
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
