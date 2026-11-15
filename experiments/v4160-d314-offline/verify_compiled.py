#!/usr/bin/env python3
"""Isolated d314 compilation and negative controls; never executes firmware."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
COMMON = HERE.parent / 'v4160-8202-offline-leaf'
sys.path.insert(0, str(COMMON))
import verify
spec = importlib.util.spec_from_file_location('v4160_8202_compile', COMMON / 'verify_compiled.py')
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

PC = 0xd314
EXPECTED = bytes.fromhex('17f5ff1f035585c43335a0008280')
SECTION = '.text.tsl9v4160.direct_closure_d314'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bin', type=Path)
    parser.add_argument('llvm_bin', type=Path)
    args = parser.parse_args()
    raw = args.bin.read_bytes()
    verify.require(hashlib.sha256(raw).hexdigest() == verify.IMAGE_SHA256, 'firmware SHA-256')
    original = raw[PC-verify.IMAGE_BASE:PC-verify.IMAGE_BASE+len(EXPECTED)]
    verify.require(original == EXPECTED, 'original d314 bytes')
    source = (HERE / 'candidate.c').read_text(encoding='utf-8')
    variants = {'original': source,
                'constant': source.replace('return tsl9_d314_data != 0;', 'return 0;'),
                'inverted': source.replace('return tsl9_d314_data != 0;', 'return tsl9_d314_data == 0;'),
                'byte': source.replace('unsigned short tsl9_d314_data', 'unsigned char tsl9_d314_data')}
    verify.require(len(set(variants.values())) == 4, 'mutation anchors')
    clang = args.llvm_bin / ('clang.exe' if (args.llvm_bin/'clang.exe').exists() else 'clang')
    ld = args.llvm_bin / ('ld.lld.exe' if (args.llvm_bin/'ld.lld.exe').exists() else 'ld.lld')
    verify.PC = PC
    with tempfile.TemporaryDirectory(prefix='tsl9-d314-isolated-') as temp:
        root = Path(temp)
        script = root / 'layout.ld'
        script.write_text('tsl9_d314_data = 0x2000bf5c;\nSECTIONS { '+SECTION+' 0xd314 : { *('+SECTION+') } }\n')
        for lang, standard in [('c', 'c11'), ('c++', 'c++17')]:
            for name, contents in variants.items():
                src, obj, elf = root/'unit.c', root/'unit.o', root/'unit.elf'
                src.write_text(contents, encoding='utf-8')
                common.run([clang, '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32',
                            '-Oz', '-fpic', '-mno-relax', '-ffreestanding', '-fno-builtin',
                            '-x', lang, '-std='+standard, '-c', src, '-o', obj])
                common.run([ld, '--no-relax', '-T', script, obj, '-o', elf])
                leaf = common.executable_section(elf.read_bytes())
                verify.require((leaf == original) == (name == 'original'), lang+' '+name+' mismatch: '+leaf.hex())
                print(lang, name, leaf.hex(), 'matches='+str(leaf == original))
                if name == 'original':
                    script.write_text('tsl9_d314_data = 0x2000bf5e;\nSECTIONS { '+SECTION+' 0xd314 : { *('+SECTION+') } }\n')
                    common.run([ld, '--no-relax', '-T', script, obj, '-o', elf])
                    wrong = common.executable_section(elf.read_bytes())
                    verify.require(wrong != original, lang+' wrong address was not detected')
                    print(lang, 'wrong-address', wrong.hex(), 'matches=False')
                    script.write_text('tsl9_d314_data = 0x2000bf5c;\nSECTIONS { '+SECTION+' 0xd314 : { *('+SECTION+') } }\n')
    print('LIMIT: isolated numeric witness; no runtime, RAM binding, full graph or device proof')


if __name__ == '__main__':
    main()
