#!/usr/bin/env python3
"""Offline isolated 8202 C/C++ compilation; numeric link is NOT deployable."""
import argparse
import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile
import verify

HERE = Path(__file__).resolve().parent
SECTION = '.text.tsl9v4160.direct_closure_8202'


def executable_section(data):
    require = verify.require
    require(len(data) >= 52, 'ELF header')
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    require(h[0][:7] == b'\x7fELF\x01\x01\x01' and h[1:4] == (2, 243, 1), 'ELF32 RISC-V executable')
    phoff, shoff, phsize, phnum, shsize, shnum = h[5], h[6], h[9], h[10], h[11], h[12]
    require(phsize == 32 and shsize == 40 and phnum > 0 and shnum > 0, 'ELF tables')
    require(phoff + phsize*phnum <= len(data) and shoff + shsize*shnum <= len(data), 'ELF table bounds')
    sections = [struct.unpack_from('<10I', data, shoff+i*shsize) for i in range(shnum)]
    found = [s for s in sections if s[3] == verify.PC and s[1] == 1 and s[2]&6 == 6]
    require(len(found) == 1, 'one executable section at original address')
    s = found[0]
    require(s[5] > 0 and s[4]+s[5] <= len(data), 'section bounds')
    mapped = False
    for i in range(phnum):
        p = struct.unpack_from('<8I', data, phoff+i*phsize)
        if p[0] != 1:
            continue
        require(p[4] <= p[5] and p[1]+p[4] <= len(data), 'load bounds')
        if (p[6]&1 and p[2] <= s[3] and s[3]+s[5] <= p[2]+p[4]
                and p[1] <= s[4] and s[4]+s[5] <= p[1]+p[4]
                and s[3]-p[2] == s[4]-p[1]):
            mapped = True
    require(mapped, 'section must be file-backed by executable LOAD')
    return data[s[4]:s[4]+s[5]]


def run(args):
    p = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    verify.require(p.returncode == 0, 'tool failed: ' + p.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bin', type=Path)
    parser.add_argument('llvm_bin', type=Path, help='directory containing clang and ld.lld')
    args = parser.parse_args()
    raw = args.bin.read_bytes()
    verify.require(hashlib.sha256(raw).hexdigest() == verify.IMAGE_SHA256, 'firmware SHA-256')
    original = raw[verify.PC-verify.IMAGE_BASE:verify.PC-verify.IMAGE_BASE+10]
    verify.check_leaf(original)
    source = (HERE/'candidate.c').read_text(encoding='utf-8')
    variants = {'original': source,
                'signed': source.replace('unsigned char tsl9_8202_data', 'signed char tsl9_8202_data'),
                'increment': source.replace('return tsl9_8202_data;', 'return tsl9_8202_data + 1;'),
                'constant': source.replace('return tsl9_8202_data;', 'return 0;')}
    verify.require(len(set(variants.values())) == 4, 'mutation anchors')
    clang = args.llvm_bin / ('clang.exe' if (args.llvm_bin/'clang.exe').exists() else 'clang')
    ld = args.llvm_bin / ('ld.lld.exe' if (args.llvm_bin/'ld.lld.exe').exists() else 'ld.lld')
    with tempfile.TemporaryDirectory(prefix='tsl9-8202-isolated-') as temp:
        root = Path(temp)
        script = root/'layout.ld'
        script.write_text('tsl9_8202_data = 0x2000bee1;\nSECTIONS { '+SECTION+' 0x8202 : { *('+SECTION+') } }\n')
        for lang, standard in [('c', 'c11'), ('c++', 'c++17')]:
            for name, contents in variants.items():
                src, obj, elf = root/'unit.c', root/'unit.o', root/'unit.elf'
                src.write_text(contents, encoding='utf-8')
                run([clang, '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32',
                     '-Oz', '-fpic', '-mno-relax', '-ffreestanding', '-fno-builtin',
                     '-x', lang, '-std='+standard, '-c', src, '-o', obj])
                run([ld, '--no-relax', '-T', script, obj, '-o', elf])
                leaf = executable_section(elf.read_bytes())
                verify.require((leaf == original) == (name == 'original'), lang+' '+name+' mismatch')
                print(lang, name, leaf.hex(), 'matches=' + str(leaf == original))
    print('LIMIT: isolated numeric witness only; no full graph, live RAM, device or flash proof')


if __name__ == '__main__':
    main()
