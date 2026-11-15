#!/usr/bin/env python3
"""Negative controls mutate actual generated ELF relocation bytes offline.

This is a narrow trusted-ELF fixture, not an adversarial ELF parser or device
execution. Every mutation is applied to a fresh copy of the real object.
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


def rela_offset(blob):
    if blob[:7] != b'\x7fELF\x01\x01\x01':
        raise ValueError('expected ELF32 little endian')
    shoff = struct.unpack_from('<I', blob, 32)[0]
    entsize, count = struct.unpack_from('<HH', blob, 46)
    if entsize != 40 or shoff + entsize * count > len(blob):
        raise ValueError('bad section table')
    matches = []
    for i in range(count):
        s = struct.unpack_from('<10I', blob, shoff + i * entsize)
        if s[1] == 4 and s[5] == 48 and s[9] == 12:
            matches.append(s[4])
    if len(matches) != 1 or matches[0] + 48 > len(blob):
        raise ValueError('unexpected relocation table')
    return matches[0]


class BinaryMutations(unittest.TestCase):
    def test_real_relocation_bytes(self):
        prep = source_check.PREP.read_bytes()
        source_check.candidate_contract(prep, source_check.PURE.read_bytes())
        tree = ast.parse(prep)
        leaf = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign)
                                     and any(isinstance(t, ast.Name) and t.id == 'LEAF' for t in n.targets)))
        spec = importlib.util.spec_from_file_location('pure_parser_binary', diag.ROOT / 'experiments/v4160-10402-pure-c/probe.py')
        parser = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parser)
        with tempfile.TemporaryDirectory(prefix='tsl9-elf-mutations-') as temp:
            root = Path(temp)
            source, obj = root / 'leaf.c', root / 'leaf.o'
            source.write_bytes(leaf)
            clang, readelf = (str(diag.TOOLS / n) for n in ('clang.exe', 'llvm-readelf.exe'))
            for lang, standard in (('c', 'c11'), ('c++', 'c++17')):
                subprocess.run([clang, '--target=riscv32-unknown-elf', '-x', lang, '-std=' + standard,
                                '-march=rv32imac_zicsr', '-mabi=ilp32', '-ffreestanding',
                                '-fno-stack-protector', '-Oz', '-fno-pic', '-msmall-data-limit=8',
                                '-c', str(source), '-o', str(obj)], check=True, capture_output=True)
                raw = obj.read_bytes()
                offset = rela_offset(raw)
                original = subprocess.run([readelf, '-aW', str(obj)], check=True, capture_output=True, text=True).stdout
                parser.check_object(normalize(original), False)
                # ELF32 Rela rows are (offset, r_info, addend), 12 bytes each.
                for label, delta in (('first offset', 0), ('first type', 4), ('first addend', 8),
                                     ('relax type', 16), ('second offset', 24), ('second type', 28),
                                     ('second addend', 32)):
                    with self.subTest(language=standard, mutation=label):
                        mutated = bytearray(raw)
                        mutated[offset + delta] ^= 1
                        altered = root / 'mutated.o'
                        altered.write_bytes(mutated)
                        result = subprocess.run([readelf, '-aW', str(altered)], capture_output=True, text=True)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        with self.assertRaises(ValueError):
                            parser.check_object(normalize(result.stdout), False)


if __name__ == '__main__':
    unittest.main()
