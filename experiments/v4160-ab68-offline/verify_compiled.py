#!/usr/bin/env python3
"""Isolated C/C++ comparison, not full-graph or device verification."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
OTHER = HERE.parent / 'v4160-8202-offline-leaf'
sys.path.insert(0, str(OTHER))
import verify
spec = importlib.util.spec_from_file_location('v8202_compiler', OTHER / 'verify_compiled.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
PC, TARGET = 0xab68, 0x2000bee8
EXPECTED = bytes.fromhex('17150020034505388280')
SECTION = '.text.tsl9_ab68'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('bin', type=Path)
    p.add_argument('llvm_bin', type=Path)
    a = p.parse_args()
    image = a.bin.read_bytes()
    verify.require(hashlib.sha256(image).hexdigest() == verify.IMAGE_SHA256, 'firmware SHA-256')
    original = image[PC-verify.IMAGE_BASE:PC-verify.IMAGE_BASE+10]
    verify.require(original == EXPECTED, 'original bytes')
    verify.PC = PC
    verify.require(verify.decode(original) == TARGET, 'decoded target')
    source = (HERE/'candidate.c').read_text(encoding='utf-8')
    variants = {'original': source,
                'signed': source.replace('unsigned char tsl9_ab68_data', 'signed char tsl9_ab68_data'),
                'increment': source.replace('return tsl9_ab68_data;', 'return tsl9_ab68_data + 1;'),
                'constant': source.replace('return tsl9_ab68_data;', 'return 0;')}
    verify.require(len(set(variants.values())) == 4, 'mutation anchors')
    clang = a.llvm_bin / ('clang.exe' if (a.llvm_bin/'clang.exe').exists() else 'clang')
    ld = a.llvm_bin / ('ld.lld.exe' if (a.llvm_bin/'ld.lld.exe').exists() else 'ld.lld')
    with tempfile.TemporaryDirectory(prefix='tsl9-ab68-') as tmp:
        root = Path(tmp)
        for lang, std in [('c','c11'), ('c++','c++17')]:
            for name, content in variants.items():
                src, obj, elf, script = (root/'unit.c', root/'unit.o', root/'unit.elf', root/'layout.ld')
                src.write_text(content, encoding='utf-8')
                helper.run([clang, '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32', '-Oz', '-fpic', '-mno-relax', '-ffreestanding', '-fno-builtin', '-x', lang, '-std='+std, '-c', src, '-o', obj])
                for label, address in [('correct', TARGET), ('wrong-address', TARGET+1)] if name == 'original' else [('correct', TARGET)]:
                    script.write_text(f'tsl9_ab68_data = {address:#x};\nSECTIONS {{ {SECTION} {PC:#x} : {{ *({SECTION}) }} }}\n')
                    helper.run([ld, '--no-relax', '-T', script, obj, '-o', elf])
                    leaf = helper.executable_section(elf.read_bytes())
                    expected_match = name == 'original' and label == 'correct'
                    verify.require((leaf == original) == expected_match, lang+' '+name+' '+label)
                    print(lang, name, label, leaf.hex(), 'matches='+str(leaf == original))
    print('LIMIT: isolated numeric binding; no full graph, actual RAM, device or flash proof')

if __name__ == '__main__':
    main()
