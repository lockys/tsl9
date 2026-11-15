#!/usr/bin/env python3
"""Demonstrate that the readelf metadata check is not an opcode check.

This negative control intentionally expects metadata acceptance of a mutated
instruction; the separate linked-byte comparisons remain necessary.
"""
import ast
import importlib.util
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
import compile_diagnostic as diag
import probe as source_check
from test_object_mutations import normalize


def leaf_range(blob):
    if blob[:7] != b'\x7fELF\x01\x01\x01':
        raise ValueError('expected ELF32 little endian')
    shoff = struct.unpack_from('<I', blob, 32)[0]
    size, count, names_index = struct.unpack_from('<HHH', blob, 46)
    if size != 40 or names_index >= count or shoff + size * count > len(blob):
        raise ValueError('bad section table')
    sections = [struct.unpack_from('<10I', blob, shoff + size * i) for i in range(count)]
    names = sections[names_index]
    if names[4] + names[5] > len(blob):
        raise ValueError('bad section names')
    strings = blob[names[4]:names[4] + names[5]]
    hits = []
    for section in sections:
        start = section[0]
        end = strings.find(b'\0', start)
        if end >= 0 and strings[start:end] == b'.text.tsl9_state_leaf_entry_10402':
            hits.append(section)
    if len(hits) != 1 or hits[0][5] != 10 or hits[0][4] + 10 > len(blob):
        raise ValueError('unexpected leaf section')
    return hits[0][4], hits[0][5]


class MetadataBoundary(unittest.TestCase):
    def test_instruction_byte_mutation_is_not_checked(self):
        prep, pure = source_check.PREP.read_bytes(), source_check.PURE.read_bytes()
        source_check.candidate_contract(prep, pure)
        tree = ast.parse(prep)
        leaf = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign)
                                   and any(isinstance(t, ast.Name) and t.id == 'LEAF' for t in n.targets)))
        spec = importlib.util.spec_from_file_location('checker_boundary', diag.ROOT / 'experiments/v4160-10402-pure-c/probe.py')
        parser = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parser)
        clang, readelf, linker = (str(diag.TOOLS / n) for n in ('clang.exe', 'llvm-readelf.exe', 'ld.lld.exe'))
        with tempfile.TemporaryDirectory(prefix='tsl9-metadata-boundary-') as temp:
            source, obj = Path(temp) / 'leaf.c', Path(temp) / 'leaf.o'
            source.write_bytes(leaf)
            for lang, standard in (('c', 'c11'), ('c++', 'c++17')):
                with self.subTest(language=standard):
                    subprocess.run([clang, '--target=riscv32-unknown-elf', '-x', lang,
                        '-std=' + standard, '-march=rv32imac_zicsr', '-mabi=ilp32',
                        '-ffreestanding', '-fno-stack-protector', '-Oz', '-fno-pic',
                        '-msmall-data-limit=8', '-c', str(source), '-o', str(obj)],
                        check=True, capture_output=True)
                    original = obj.read_bytes()
                    layout = Path(temp) / 'layout.ld'
                    layout.write_text('__global_pointer$ = 0x20004000;\n'
                        'tsl9_witness_10402 = 0x20004050;\n'
                        'SECTIONS { .leaf 0x10402 : { *(.text.tsl9_state_leaf_entry_10402) } }\n')
                    elf = Path(temp) / 'leaf.elf'
                    link = [linker, '--relax', '--relax-gp', '-T', str(layout), '-o', str(elf), str(obj)]
                    subprocess.run(link, check=True, capture_output=True)
                    _, expected = parser.section(elf.read_bytes())
                    self.assertEqual(expected.hex(), '03d501058280')
                    offset, length = leaf_range(original)
                    altered = bytearray(original)
                    # Flip a bit in the final instruction, leaving all ELF metadata intact.
                    altered[offset + length - 1] ^= 1
                    obj.write_bytes(altered)
                    result = subprocess.run([readelf, '-aW', str(obj)], check=True, capture_output=True, text=True)
                    parser.check_object(normalize(result.stdout), False)
                    self.assertNotEqual(original[offset:offset + length], altered[offset:offset + length])
                    subprocess.run(link, check=True, capture_output=True)
                    _, actual = parser.section(elf.read_bytes())
                    self.assertNotEqual(actual, expected, 'linked-byte check must detect this mutation')


if __name__ == '__main__':
    unittest.main()
