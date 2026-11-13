#!/usr/bin/env python3
"""Offline, bounded RV32 object and non-loadable link witness; no target execution."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
READER = ROOT / 'experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py'
NDK = Path(r'C:\Users\locky\AppData\Local\Android\Sdk\ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin')
PINS = {'bin': '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
        'source': '4e50f5efd36b2e52597c74c6e2058732d5b0c8bff2e8dbd107be027af004457f',
        'reader': 'a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a',
        'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
        'lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
ORIGINAL = bytes.fromhex('17d5ff1f034505028280')
WRONG = bytes.fromhex('17e5ff1f034505028280')
PC, TARGET = 0xef6c, 0x2000bf8c
# Measured from both controlled C/C++ objects and both linked address cases.
RISCV_FLAGS = 0x1  # RVC, soft-float ABI


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def pinned(data, name):
    need(hashlib.sha256(data).hexdigest() == PINS[name], name + ' SHA-256 mismatch')
    return data


def reference(data):
    pinned(data, 'bin')
    need(len(data) == 76800, 'BIN size')
    b = data[PC-0x8000:PC-0x8000+10]
    need(b == ORIGINAL, 'BIN getter bytes')
    hi, lo = int.from_bytes(b[:4], 'little'), int.from_bytes(b[4:8], 'little')
    need((hi & 0xfff) == 0x517, 'AUIPC a0')
    need((lo & 0xfffff) == 0x54503 and b[8:] == b'\x82\x80', 'LBU a0,(a0); ret')
    imm = lo >> 20
    if imm & 0x800: imm -= 0x1000
    target = (PC + (hi & 0xfffff000) + imm) & 0xffffffff
    need(target == TARGET, 'BIN decoded target')
    return b


def load_reader():
    # Execute exactly the byte snapshot that was hashed, not a second file read.
    data = pinned(READER.read_bytes(), 'reader')
    ns = {'__name__': 'pinned_elf_reader'}
    exec(compile(data, str(READER), 'exec'), ns)
    return ns['ELF']


def sym(e, name):
    found = [s for s in e.symbols if s['name'] == name]
    need(len(found) == 1, 'symbol ' + name + ' count')
    return found[0]


def eqsym(s, value, size, info, other, section, message):
    need((s['value'], s['size'], s['info'], s['other'], s['section']) ==
         (value, size, info, other, section), message)


def leaf(e, address):
    s = e.section('.leaf')
    need((s['type'], s['flags'], s['address'], s['size'], s['align']) == (1, 6, address, 10, 2), 'leaf section')
    return s


def null_symbol(e):
    table = e.section('.symtab')
    need(table['size'] >= 16 and e.data(table)[:16] == bytes(16), 'null symbol 0')


def object_check(e):
    need(e.header[0] == 1 and not e.program_headers, 'ET_REL header')
    need(e.header[6] == RISCV_FLAGS, 'object ABI e_flags')
    null_symbol(e)
    s = leaf(e, 0)
    eqsym(sym(e, 'get_status'), 0, 10, 0x12, 0, s['index'], 'object FUNC')
    data = sym(e, 'status_byte')
    eqsym(data, 0, 0, 0x10, 2, 0, 'object data symbol')
    need([x['index'] for x in e.symbols[1:] if x['section'] == 0] == [data['index']], 'object undefined symbols')
    anchor = sym(e, '.Lpcrel_hi0')
    eqsym(anchor, 0, 0, 0, 0, s['index'], 'object anchor')
    rsec = [x for x in e.sections if x['type'] == 4]
    need(len(rsec) == 1 and rsec[0]['name'] == '.rela.leaf' and rsec[0]['info'] == s['index'] and rsec[0]['size'] == 24, 'object relocation section')
    expected = [(s['index'], 0, 23, data['index'], 0), (s['index'], 4, 24, anchor['index'], 0)]
    got = [(r['section'], r['offset'], r['type'], r['symbol'], r['addend']) for r in e.relocations]
    need(got == expected, 'object relocations')
    code = e.data(s)
    hi, lo = int.from_bytes(code[:4], 'little'), int.from_bytes(code[4:8], 'little')
    need((hi & 0xfff) == 0x517, 'object AUIPC opcode/register')
    need((lo & 0xfffff) == 0x54503, 'object LBU opcode/registers')
    need(code[8:] == b'\x82\x80', 'object ret opcode/register')
    need(code == bytes.fromhex('17050000034505008280'), 'object instruction bytes')


def final_check(e, target, expected):
    need(e.header[0] == 2 and all(p[0] != 1 for p in e.program_headers), 'final EXEC/no PT_LOAD')
    need(e.header[6] == RISCV_FLAGS, 'final ABI e_flags')
    null_symbol(e)
    s = leaf(e, PC)
    for other in e.sections:
        if other['index'] == s['index'] or not other['flags'] & 2 or not other['size']:
            continue
        start, size = other['address'], other['size']
        need(start + size <= 0x100000000, 'final alloc VMA extent')
        need(start + size <= s['address'] or start >= s['address'] + s['size'], 'final alloc VMA overlap')
        if other['type'] != 8:  # SHT_NOBITS occupies no file bytes.
            off = other['offset']
            need(off + size <= s['offset'] or off >= s['offset'] + s['size'], 'final alloc file overlap')
    eqsym(sym(e, 'get_status'), PC, 10, 0x12, 0, s['index'], 'final FUNC')
    eqsym(sym(e, 'status_byte'), target, 0, 0, 2, 0xfff1, 'final ABS data symbol')
    need(not e.relocations and not any(x['type'] in (4, 9) for x in e.sections), 'final relocations')
    need(all(x['section'] != 0 for x in e.symbols[1:]), 'final undefined symbol')
    need(e.data(s) == expected, 'final exact bytes')


def run(cmd):
    result = subprocess.run(list(map(str, cmd)), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError('command failed: ' + repr(list(map(str, cmd))) + '\n' + result.stdout + result.stderr)
    return result.stdout + result.stderr


def toolpaths(ndk):
    suffix = '.exe' if os.name == 'nt' else ''
    clang, lld = ndk / ('clang' + suffix), ndk / ('ld.lld' + suffix)
    pinned(clang.read_bytes(), 'clang'); pinned(lld.read_bytes(), 'lld')
    return clang, lld


def build(directory, clang, lld, language, source):
    src = directory / 'leaf.c'; src.write_bytes(source)
    obj = directory / 'leaf.o'
    run([clang, '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32',
         '-mcmodel=medany', '-mno-relax', '-fno-pic', '-ffreestanding', '-fno-stack-protector',
         '-Oz', '-x', language, '-std=' + ('c11' if language == 'c' else 'c++17'), '-c', src, '-o', obj])
    return obj


def link(directory, lld, obj, target):
    layout = directory / 'layout.ld'; elf = directory / 'leaf.elf'
    layout.write_text('status_byte = 0x%x;\nPHDRS { none PT_NULL; }\nSECTIONS { .leaf 0xef6c : { *(.leaf) } :none }\n' % target, encoding='ascii')
    run([lld, '--no-relax', '-T', layout, '-o', elf, obj])
    return elf


def experiment(bin_path=BIN, ndk=NDK):
    original = reference(bin_path.read_bytes())
    source = pinned((HERE / 'leaf.c').read_bytes(), 'source')
    reader = load_reader(); clang, lld = toolpaths(ndk)
    results = []
    with tempfile.TemporaryDirectory(dir=HERE, prefix='scratch-') as tmp:
        for language in ('c', 'c++'):
            d = Path(tmp) / language.replace('+', 'p'); d.mkdir()
            obj = build(d, clang, lld, language, source)
            object_check(reader(obj))
            for target, expected in ((TARGET, original), (TARGET + 0x1000, WRONG)):
                elf = link(d, lld, obj, target)
                final_check(reader(elf), target, expected)
                results.append({'language': language, 'data_address': hex(target), 'bytes': expected.hex(), 'matches_original': expected == original})
    return {'original': original.hex(), 'decoded_target': hex(TARGET), 'cases': results}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--bin', type=Path, default=BIN); p.add_argument('--ndk-bin', type=Path, default=NDK)
    a = p.parse_args()
    print(json.dumps(experiment(a.bin, a.ndk_bin), indent=2))


if __name__ == '__main__':
    main()
