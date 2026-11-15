#!/usr/bin/env python3
"""Audit retained original-layout ELF ownership; diagnostic only, not flashable.

Only one of the three original address-materialization sites is present in this
selected layout. Presence and static references do not establish execution.
"""
import argparse
import hashlib
import struct
from pathlib import Path
import materialized_references as refs

OWNER = 'tsl9_rom_dependency_entry_9f74'
LEAF = bytes.fromhex('a387010a8280')
WINDOW_SHA = '551e0bd058e88a00ef29c2d561808a758ace0ff36fdb09af56e8a915ccdd31e8'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def region(data, offset, size):
    require(offset >= 0 and size >= 0 and offset + size <= len(data), 'ELF range')
    return data[offset:offset + size]

def string(data, offset):
    require(0 <= offset < len(data), 'string offset')
    end = data.find(b'\0', offset)
    require(end >= 0, 'unterminated string')
    return data[offset:end].decode('ascii')

def audit(data, image, expected_present=(0xa356,), expected_missing=(0xa0b8, 0xa1b8)):
    references = refs.inspect(image)
    require(hashlib.sha256(LEAF).hexdigest() == WINDOW_SHA, 'leaf hash')
    require(len(data) >= 52, 'short ELF')
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    require(h[0][:7] == b'\x7fELF\x01\x01\x01' and h[1] == 2 and h[2] == 243, 'ELF32 little-endian RISC-V executable')
    shoff, phoff, ehsize, phentsize, phnum, shentsize, shnum, shstr = h[6], h[5], h[8], h[9], h[10], h[11], h[12], h[13]
    require(ehsize == 52 and shentsize == 40 and 0 < shnum and shstr < shnum, 'ELF headers')
    region(data, shoff, shnum * shentsize)
    sections = [struct.unpack_from('<IIIIIIIIII', data, shoff+i*40) for i in range(shnum)]
    require(phnum == 0 or phentsize == 32, 'program header size')
    region(data, phoff, phnum*phentsize)
    loads = sum(struct.unpack_from('<I', data, phoff+i*phentsize)[0] == 1 for i in range(phnum))
    require(loads == 0, 'expected nonloadable diagnostic')
    def allocated(pc, size):
        found = [s for s in sections if s[2]&2 and s[5] and s[3] < pc+size and pc < s[3]+s[5]]
        if not found:
            return None
        require(len(found) == 1, 'overlapping allocated sections')
        s = found[0]
        require(s[1] == 1 and s[2]&4 and s[3] <= pc and pc+size <= s[3]+s[5], 'partially covered or non-executable PROGBITS range')
        return region(data, s[4]+pc-s[3], size)
    require(allocated(0x9f74, 6) == LEAF, 'leaf bytes')
    symbols = []
    for s in sections:
        if s[1] != 2:
            continue
        require(s[6] < shnum and sections[s[6]][1] == 3 and s[9] == 16 and s[5] % 16 == 0, 'symbol table')
        strings = region(data, sections[s[6]][4], sections[s[6]][5])
        table = region(data, s[4], s[5])
        for off in range(0, len(table), 16):
            name, value, size, info, other, index = struct.unpack_from('<IIIBBH', table, off)
            if string(strings, name) == OWNER:
                symbols.append((value, size, info, other, index))
    require(len(symbols) == 1, 'unique owner')
    value, size, info, other, index = symbols[0]
    require((value, size, info & 15) == (0x9f74, 6, 2) and 0 < index < shnum, 'owner symbol')
    require(sections[index][2]&6 == 6 and sections[index][1] == 1 and sections[index][3] <= value and value+size <= sections[index][3]+sections[index][5], 'executable owner section')
    present = []
    missing = []
    for (pc, expected, _jal, _target, _rd), (_, addr, *_rest) in zip(refs.SITES, references):
        raw = allocated(pc, len(bytes.fromhex(expected)))
        if raw is None:
            missing.append(pc)
        else:
            require(raw == bytes.fromhex(expected) and refs.decode_address(pc, raw) == value == addr, 'materialized address')
            present.append(pc)
    require(tuple(present) == tuple(expected_present) and tuple(missing) == tuple(expected_missing), 'selected reference scope')
    return {'owner': hex(value), 'bytes': LEAF.hex(), 'present': [hex(x) for x in present], 'absent': [hex(x) for x in missing], 'load_segments': loads}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--all-references', action='store_true', help='require all three sites (e.g. safe-gap-v2); bytes may be retained original code')
    p.add_argument('c', type=Path)
    p.add_argument('cpp', type=Path)
    args = p.parse_args()
    image = refs.BIN.read_bytes()
    for language, path in [('C', args.c), ('C++', args.cpp)]:
        scope = (0xa0b8, 0xa1b8, 0xa356) if args.all_references else (0xa356,)
        missing = () if args.all_references else (0xa0b8, 0xa1b8)
        print(language, audit(path.read_bytes(), image, scope, missing))
    print('LIMIT: retained nonloadable selected-layout artifacts; no build provenance, callback execution, live GP, device or OTA proof')

if __name__ == '__main__':
    main()
