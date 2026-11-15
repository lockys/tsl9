#!/usr/bin/env python3
"""Compile two GP-relative leaf candidates offline; numeric witnesses only."""
import argparse
import hashlib
import struct
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'v4160-8202-offline-leaf'))
import verify
from verify_compiled import run


def executable_section(data, address):
    verify.require(len(data) >= 52, 'ELF header')
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    verify.require(h[0][:7] == b'\x7fELF\x01\x01\x01' and h[1:4] == (2, 243, 1), 'ELF32 RISC-V executable')
    phoff, shoff, phsize, phnum, shsize, shnum = h[5], h[6], h[9], h[10], h[11], h[12]
    verify.require(phsize == 32 and shsize == 40 and phnum > 0 and shnum > 0, 'ELF tables')
    verify.require(phoff + phsize*phnum <= len(data) and shoff + shsize*shnum <= len(data), 'ELF bounds')
    sections = [struct.unpack_from('<10I', data, shoff+i*shsize) for i in range(shnum)]
    found = [s for s in sections if s[3] == address and s[1] == 1 and s[2]&6 == 6]
    verify.require(len(found) == 1, 'one executable section at original address')
    s = found[0]
    verify.require(s[5] > 0 and s[4]+s[5] <= len(data), 'section bounds')
    mapped = False
    for i in range(phnum):
        p = struct.unpack_from('<8I', data, phoff+i*phsize)
        if p[0] != 1:
            continue
        verify.require(p[4] <= p[5] and p[1]+p[4] <= len(data), 'load bounds')
        if (p[6]&1 and p[2] <= s[3] and s[3]+s[5] <= p[2]+p[4]
                and p[1] <= s[4] and s[4]+s[5] <= p[1]+p[4]
                and s[3]-p[2] == s[4]-p[1]):
            mapped = True
    verify.require(mapped, 'section must be file-backed by executable LOAD')
    return data[s[4]:s[4]+s[5]]


GP = 0x20004000
LEAVES = {
    0x10402: ('direct_successors', 80, bytes.fromhex('03d501058280')),
    0x10408: ('direct_frontier', 82, bytes.fromhex('03c521058280')),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bin', type=Path)
    parser.add_argument('llvm_bin', type=Path)
    args = parser.parse_args()
    raw = args.bin.read_bytes()
    verify.require(hashlib.sha256(raw).hexdigest() == verify.IMAGE_SHA256, 'firmware SHA-256')
    clang = args.llvm_bin / ('clang.exe' if (args.llvm_bin/'clang.exe').exists() else 'clang')
    ld = args.llvm_bin / ('ld.lld.exe' if (args.llvm_bin/'ld.lld.exe').exists() else 'ld.lld')
    with tempfile.TemporaryDirectory(prefix='tsl9-gp-leaves-') as temp:
        root = Path(temp)
        for address, (group, offset, expected) in LEAVES.items():
            original = raw[address-verify.IMAGE_BASE:address-verify.IMAGE_BASE+6]
            verify.require(original == expected, 'original bytes')
            section = '.text.tsl9v4160.' + group + '_' + format(address, 'x')
            data_symbol = 'tsl9_' + format(address, 'x') + '_data'
            for lang, standard in [('c', 'c11'), ('c++', 'c++17')]:
                obj = root/'unit.o'
                run([clang, '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr', '-mabi=ilp32',
                     '-Oz', '-fno-pic', '-msmall-data-limit=8', '-ffreestanding', '-fno-builtin',
                     '-x', lang, '-std='+standard, '-DLEAF='+hex(address), '-c', HERE/'candidate.c', '-o', obj])
                for label, gp, target in [('reference', GP, GP+offset),
                                          ('wrong-offset', GP, GP+offset+2),
                                          ('shifted-pair', GP+4, GP+offset+4)]:
                    script, elf = root/'layout.ld', root/'unit.elf'
                    script.write_text('__global_pointer$ = '+hex(gp)+';\n'+data_symbol+' = '+hex(target)+';\n'
                                      'SECTIONS { '+section+' '+hex(address)+' : { *('+section+') } }\n')
                    run([ld, '--relax', '--relax-gp', '-T', script, obj, '-o', elf])
                    leaf = executable_section(elf.read_bytes(), address)
                    verify.require((leaf == original) == (label != 'wrong-offset'), 'unexpected '+label+' bytes')
                    print(hex(address), lang, label, leaf.hex(), 'matches='+str(leaf == original))
    print('LIMIT: isolated numeric link, not a stock gate, live GP/carrier binding or device proof')
    print('NOTE: shifting both GP and target preserves code bytes; their actual addresses require separate validation')


if __name__ == '__main__':
    main()
