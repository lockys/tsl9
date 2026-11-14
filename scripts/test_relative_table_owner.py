#!/usr/bin/env python3
"""Negative controls against actual diagnostic C/C++ ELF owners; no target execution."""
import argparse
import copy
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parent.parent
ELF = runpy.run_path(str(ROOT / 'src/native/tx_candidate/postpass/elf32.py'))['ELF']
check = runpy.run_path(str(ROOT / 'scripts/relative_table_owner.py'))['check_relative_table_owner']


def rejected(elf, mutate, label):
    variant = copy.deepcopy(elf)
    mutate(variant)
    try:
        check(variant)
    except ValueError:
        return
    raise RuntimeError('mutant accepted: ' + label)


def symbol(elf, name):
    return next(s for s in elf.symbols if s['name'] == name)


def section(elf, address):
    return next(s for s in elf.sections if s['address'] == address and s['flags'] & 2 and s['size'])


def modify_bytes(elf, address, byte):
    data = bytearray(elf.raw)
    data[section(elf, address)['offset'] + byte] ^= 1
    elf.raw = bytes(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', type=Path, required=True, help='Candidate build output directory')
    args = parser.parse_args()
    alias = 'tsl9_opaque_gap_0001a6a0'
    prefix = 'tsl9_opaque_prefix_0001a6a0'
    table = 'tsl9_relative_table_0001a6a4'
    for mode in ('c', 'cpp'):
        elf = ELF(args.build / 'selected/build' / ('NOT-FLASHABLE-compact-source-layout-' + mode + '.elf'))
        check(elf)
        for i in range(20):
            rejected(elf, lambda e, i=i: modify_bytes(e, 0x1a6a4, i), f'table byte {i}')
        for name in (alias, prefix, table):
            for field, val in (('index', 0xfff1), ('size', 1), ('info', 1), ('other', 1), ('value', 0)):
                rejected(elf, lambda e, n=name, f=field, v=val: symbol(e,n).__setitem__(f,v), f'{name} {field}')
        for address in (0x1a6a0, 0x1a6a4):
            for field, val in (('address', address + 1), ('flags', 3), ('flags', 0x12), ('flags', 0x402), ('type', 8), ('size', 3)):
                rejected(elf, lambda e, a=address, f=field, v=val: section(e,a).__setitem__(f,v), f'{address:x} {field}')
        for i in range(4):
            rejected(elf, lambda e, i=i: modify_bytes(e, 0x1a6a0, i), f'prefix byte {i}')
        rejected(elf, lambda e: e.symbols.remove(symbol(e, alias)), 'missing alias')
        rejected(elf, lambda e: e.symbols.append(copy.copy(symbol(e, alias))), 'duplicate alias')
        rejected(elf, lambda e: e.sections.append(copy.copy(section(e, 0x1a6a4))), 'overlapping section')
        print(f'PASS {mode}: actual ELF accepted; 54 section, symbol and byte mutations rejected')


if __name__ == '__main__':
    main()
