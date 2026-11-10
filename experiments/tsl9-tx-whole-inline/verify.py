#!/usr/bin/env python3
"""Offline original-PC reconstruction; all compiler output is temporary."""
import argparse
import hashlib
import subprocess
import tempfile
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--tool-dir', type=Path, required=True)
p.add_argument('--reference', type=Path, required=True)
a = p.parse_args()

def run(*args):
    return subprocess.run(list(map(str, args)), check=True, capture_output=True, text=True).stdout

def tool(name):
    path = a.tool_dir / name
    if path.with_suffix('.exe').is_file():
        path = path.with_suffix('.exe')
    return path.resolve()

def branch(data, pc):
    w = int.from_bytes(data[pc-0x8a56:pc-0x8a56+4], 'little')
    if w & 127 != 0x63:
        raise ValueError('not a B-type branch')
    imm = ((w >> 31) & 1) << 12 | ((w >> 7) & 1) << 11 | ((w >> 25) & 63) << 5 | ((w >> 8) & 15) << 1
    return pc + (imm - 8192 if imm & 4096 else imm)

def jump(data):
    w = int.from_bytes(data[0x8b6a-0x8a56:0x8b6c-0x8a56], 'little')
    if w & 0xe003 != 0xa001:
        raise ValueError('not C.J')
    imm = ((w >> 12) & 1) << 11 | ((w >> 11) & 1) << 4 | ((w >> 9) & 3) << 8 | ((w >> 8) & 1) << 10 | ((w >> 7) & 1) << 6 | ((w >> 6) & 1) << 7 | ((w >> 3) & 7) << 1 | ((w >> 2) & 1) << 5
    return 0x8b6a + (imm - 4096 if imm & 2048 else imm)

def check_ref(ref):
    if len(ref) != 76800 or hashlib.sha256(ref[0xa56:0xb6e]).hexdigest() != '3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b':
        raise ValueError('reference size or digest mismatch')

ref = a.reference.read_bytes()
check_ref(ref)
for bad in (ref[:-1], ref[:0xb20] + bytes([ref[0xb20] ^ 1]) + ref[0xb21:]):
    try:
        check_ref(bad)
    except ValueError:
        pass
    else:
        raise ValueError('bad reference accepted')
source = (Path(__file__).parent / 'tx.c').read_text(encoding='utf-8')
targets = {0x8a5a: 0x8b6c, 0x8a76: 0x8a96, 0x8a7e: 0x8a96,
           0x8a92: 0x8acc, 0x8a9a: 0x8abe, 0x8aa2: 0x8abe,
           0x8aba: 0x8ace, 0x8b10: 0x8b52}
with tempfile.TemporaryDirectory(prefix='tx-whole-') as tmp:
    d = Path(tmp)
    (d / 'link.ld').write_text('OUTPUT_ARCH(riscv)\nSECTIONS { .text 0x8a56 : { *(.text.tx) } }\n')
    def build(mode, text):
        (d / 'tx.c').write_text(text, encoding='utf-8')
        run(tool('clang'), '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-mno-relax', '-ffreestanding', '-x', mode, '-std=' + ('c11' if mode == 'c' else 'c++17'), '-c', d/'tx.c', '-o', d/'tx.o')
        rel = run(tool('llvm-readelf'), '-r', d/'tx.o')
        if 'There are no relocations in this file.' not in rel:
            raise ValueError('unexpected relocation')
        run(tool('ld.lld'), '--no-relax', '-T', d/'link.ld', d/'tx.o', '-o', d/'tx.elf')
        run(tool('llvm-objcopy'), '-O', 'binary', '--only-section=.text', d/'tx.elf', d/'tx.bin')
        return (d/'tx.bin').read_bytes()
    for mode in ('c', 'c++'):
        data = build(mode, source)
        if data != ref[0xa56:0xb6e] or len(data) != 280:
            raise ValueError(f'byte mismatch: {mode}, length {len(data)}, first differences ' + str([(hex(0x8a56+i), hex(x), hex(y)) for i, (x, y) in enumerate(zip(data, ref[0xa56:0xb6e])) if x != y][:12]))
        if any(branch(data, pc) != target for pc, target in targets.items()) or jump(data) != 0x8b0a:
            raise ValueError('branch target mismatch')
        mutations = [('addi a5, zero, 1039', 'addi a5, zero, 1038'),
                     ('.insn b 0x63, 6, a5, a3, .Learly', '.insn b 0x63, 7, a5, a3, .Learly'),
                     ('.insn b 0x63, 6, a5, a3, .Learly', '.insn b 0x63, 6, a5, a3, .Learly-2'),
                     ('.insn cj 1, 5, .Lloop', '.insn cj 1, 5, .Lloop+2')]
        for old, new in mutations:
            if source.count(old) != 1:
                raise ValueError('mutation source ambiguous')
            changed = build(mode, source.replace(old, new))
            if changed == data:
                raise ValueError('mutation not detected')
            if new.endswith('.Learly-2') and branch(changed, 0x8a5a) != 0x8b6a:
                raise ValueError('early target mutation mismatch')
            if new.endswith('.Lloop+2') and jump(changed) != 0x8b0c:
                raise ValueError('back-edge mutation mismatch')
        print(mode, '280/280 exact; eight B targets and C.J checked; four mutations detected')
print('modified and truncated references rejected; offline only')
