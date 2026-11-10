#!/usr/bin/env python3
"""Offline, isolated original-coordinate table link; outputs stay in a temporary directory."""
import argparse
import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x1a6a4
TARGETS = (0x1452e, 0x1453e, 0x1454a, 0x1473e, 0x14748)


def run(*args):
    subprocess.run([str(x) for x in args], check=True, capture_output=True)


def section(path):
    data = path.read_bytes()
    assert data[:7] == b'\x7fELF\x01\x01\x01'
    assert struct.unpack_from('<H', data, 18)[0] == 243
    shoff = struct.unpack_from('<I', data, 32)[0]
    entsize, count, names = struct.unpack_from('<HHH', data, 46)
    sh = [struct.unpack_from('<10I', data, shoff + entsize*i) for i in range(count)]
    strings = data[sh[names][4]:sh[names][4]+sh[names][5]]
    found = [s for s in sh if strings[s[0]:].split(b'\0', 1)[0] == b'.table']
    assert len(found) == 1
    s = found[0]
    assert s[1] == 1 and s[2] & 3 == 2 and s[3] == BASE and s[5] == 20
    return data[s[4]:s[4]+s[5]]


def verify(table, reference):
    if len(table) != 20 or table != reference:
        raise ValueError('20-byte reference mismatch')
    if tuple(BASE + v for v in struct.unpack('<5i', table)) != TARGETS:
        raise ValueError('target mismatch')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tool-dir', type=Path, required=True)
    a = p.parse_args()
    clang, linker = (a.tool_dir / n for n in ('clang.exe', 'ld.lld.exe'))
    image = IMAGE.read_bytes()
    assert len(image) == 0x12c00 and hashlib.sha256(image).hexdigest() == SHA
    reference = image[BASE-0x8000:BASE-0x8000+20]
    with tempfile.TemporaryDirectory(prefix='tsl9-relative-table-') as tmp:
        tmp = Path(tmp)
        for language, standard in [('c', 'c11'), ('c++', 'c++17')]:
            obj, elf, ld = (tmp / name for name in ('table.o', 'table.elf', 'layout.ld'))
            run(clang, '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32',
                '-ffreestanding', '-x', language, '-std='+standard, '-c', HERE/'table.c', '-o', obj)
            def link(mutated=None):
                bindings = '\n'.join('target_%x = 0x%x;' % (t, t + (2 if i == mutated else 0))
                                     for i, t in enumerate(TARGETS))
                ld.write_text(bindings + '\nSECTIONS { .table 0x1a6a4 : { KEEP(*(.rodata.relative_table)) } }\n', encoding='ascii')
                run(linker, '--no-relax', '-T', ld, obj, '-o', elf)
                return section(elf)
            original = link()
            verify(original, reference)
            for i in range(5):
                changed = link(i)
                assert all(changed[4*j:4*j+4] == original[4*j:4*j+4] for j in range(5) if j != i)
                assert changed[4*i:4*i+4] != original[4*i:4*i+4]
                try:
                    verify(changed, reference)
                except ValueError:
                    pass
                else:
                    raise AssertionError('mutated target accepted')
            print(language, 'PASS: original 20 bytes and five targets; five linked target mutations rejected')
    print('Reference SHA256:', SHA, '; no candidate image written')


if __name__ == '__main__':
    main()
