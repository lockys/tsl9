#!/usr/bin/env python3
"""Mutate real compiler readelf output before the reused object checks.

Tests the text checker, not ELF-byte tampering, tool provenance, hardware,
nor a nine-leaf integration. The object is built in a temporary directory.
"""
import ast
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
import compile_diagnostic as diag
import probe as source_check


def normalize(text):
    return (text.replace('tsl9_state_leaf_entry_10402', 'get_witness')
            .replace('tsl9_witness_10402', 'witness')
            .replace('.text.get_witness', '.leaf'))


class RealObjectMutations(unittest.TestCase):
    def test_real_object_output(self):
        prep = source_check.PREP.read_bytes()
        source_check.candidate_contract(prep, source_check.PURE.read_bytes())
        tree = ast.parse(prep)
        leaf = ast.literal_eval(next(x.value for x in tree.body if isinstance(x, ast.Assign)
                                     and any(isinstance(t, ast.Name) and t.id == 'LEAF' for t in x.targets)))
        parser_path = diag.ROOT / 'experiments/v4160-10402-pure-c/probe.py'
        spec = importlib.util.spec_from_file_location('pure_parser_test', parser_path)
        parser = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parser)
        clang, readelf = (diag.TOOLS / n for n in ('clang.exe', 'llvm-readelf.exe'))
        with tempfile.TemporaryDirectory(prefix='tsl9-object-mutation-') as temp:
            source, obj = Path(temp) / 'leaf.c', Path(temp) / 'leaf.o'
            source.write_bytes(leaf)
            for lang, standard in (('c', 'c11'), ('c++', 'c++17')):
                subprocess.run([str(clang), '--target=riscv32-unknown-elf', '-x', lang,
                                '-std=' + standard, '-march=rv32imac_zicsr', '-mabi=ilp32',
                                '-ffreestanding', '-fno-stack-protector', '-Oz', '-fno-pic',
                                '-msmall-data-limit=8', '-c', str(source), '-o', str(obj)], check=True, capture_output=True)
                info = subprocess.run([str(readelf), '-aW', str(obj)], check=True, capture_output=True, text=True).stdout
                text = normalize(info)
                parser.check_object(text, False)
                mutations = (
                    ('HI20 relocation', 'R_RISCV_HI20', 'R_RISCV_LO12_I'),
                    ('LO12 relocation', 'R_RISCV_LO12_I', 'R_RISCV_HI20'),
                    ('relax relocation', 'R_RISCV_RELAX', 'R_RISCV_HI20'),
                    ('undefined witness visibility', 'GLOBAL HIDDEN    UND witness', 'GLOBAL DEFAULT   UND witness'),
                    ('function symbol', 'FUNC    GLOBAL DEFAULT', 'OBJECT  GLOBAL DEFAULT'),
                    ('witness addend', 'witness + 0', 'witness + 1'),
                    ('relocation section', '.rela.leaf', '.rela.changed'),
                )
                for label, old, new in mutations:
                    with self.subTest(language=standard, mutation=label):
                        self.assertIn(old, text)
                        altered = text.replace(old, new, 1)
                        with self.assertRaises(ValueError):
                            parser.check_object(altered, False)


if __name__ == '__main__':
    unittest.main()
