"""Synthetic-only checks; no parser, compiler, linker, target or network."""
import copy
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guard

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.symbol = dict(name='external', index=0, value=0, size=0, info=16, other=0)
        self.elf = SimpleNamespace(sections=[dict(name='', index=0), dict(name='.keep', index=1),
                                             dict(name='.rela', index=2, type=4, info=1, size=36)],
                                   relocations=[])
        self.a = dict(owner='.keep', offset=0, type=1, addend=0, symbol=self.symbol)
        self.b = dict(self.a, type=2)
        self.c = dict(self.a, offset=4, type=3)
    def facts(self, elf=None):
        obj = self.elf if elf is None else elf
        guard.check_owners(obj)
        return guard.relocation_facts(obj, '.target', None, 'target', lambda s: None)
    def test_order_and_composition(self):
        for before, after in (([self.a, self.b], [self.b, self.a]),
                              ([self.a, self.c], [self.c, self.a]),
                              ([self.a, self.c, self.b], [self.a, self.b, self.c]),
                              ([self.a, self.a, self.b], [self.a, self.b, self.a]),
                              ([self.a, self.a], [self.a])):
            self.elf.relocations = before
            left = self.facts()
            self.elf.relocations = after
            self.assertNotEqual(left, self.facts())
    def test_metadata_pairing(self):
        self.elf.relocations = [self.a, dict(self.b, symbol=dict(self.symbol, value=1))]
        expected = self.facts()
        for field, value in [('name', 'changed'), ('index', 1), ('value', 2), ('size', 1),
                             ('info', 17), ('other', 2)]:
            mutant = copy.deepcopy(self.elf)
            mutant.relocations[1]['symbol'][field] = value
            self.assertNotEqual(expected, self.facts(mutant), field)
        mutant = copy.deepcopy(self.elf)
        mutant.relocations[0]['symbol'], mutant.relocations[1]['symbol'] = (
            mutant.relocations[1]['symbol'], mutant.relocations[0]['symbol'])
        self.assertNotEqual(expected, self.facts(mutant))
    def test_boundary_and_encoding(self):
        self.elf.relocations = [self.a, self.b]
        self.facts()
        for size in (0, 12):
            mutant = copy.deepcopy(self.elf)
            mutant.sections.append(dict(name='.second', index=3, type=4, info=1, size=size))
            with self.assertRaisesRegex(ValueError, 'multiple relocation sections'):
                self.facts(mutant)
        for owner in (0, -1, 99):
            mutant = copy.deepcopy(self.elf)
            mutant.sections[2]['info'] = owner
            with self.assertRaisesRegex(ValueError, 'invalid relocation section owner'):
                self.facts(mutant)
        self.elf.sections[2]['type'] = 9
        with self.assertRaisesRegex(ValueError, 'RELA encoding only'):
            self.facts()
    def test_retained_reference_to_target_rejected(self):
        self.elf.sections.append(dict(name='.target', index=3))
        for symbol in (dict(self.symbol, name='target'), dict(self.symbol, index=3)):
            self.elf.relocations = [dict(self.a, symbol=symbol)]
            with self.assertRaisesRegex(ValueError, 'retained relocation references removed section'):
                guard.relocation_facts(self.elf, '.target', 3, 'target', lambda s: None)
        self.elf.relocations = [dict(self.a, owner='.target', symbol=dict(self.symbol, name='target', index=3))]
        self.assertEqual(len(guard.relocation_facts(self.elf, '.target', 3, 'target', lambda s: None)[1]), 1)
    def test_mapping_symbol_relocation_rejected(self):
        self.elf.sections.append(dict(name='.target', index=3))
        for owner in ('.keep', '.target'):
            self.elf.relocations = [dict(self.a, owner=owner, symbol=dict(self.symbol, name='$x.1'))]
            with self.assertRaisesRegex(ValueError, 'relocation references a mapping symbol'):
                guard.relocation_facts(self.elf, '.target', 3, 'target', lambda s: 'x' if s['name'] == '$x.1' else None)
    def test_section_symbol_invalid_index(self):
        self.elf.sections.append(dict(name='.target', index=3))
        for owner in ('.keep', '.target'):
            for index in (0, -1, len(self.elf.sections), 0xfff1):
                self.elf.relocations = [dict(self.a, owner=owner, symbol=dict(self.symbol, info=3, index=index))]
                with self.subTest(owner=owner, index=index):
                    with self.assertRaisesRegex(ValueError, 'invalid relocation section symbol target'):
                        self.facts()
        self.elf.relocations = [dict(self.a, symbol=dict(self.symbol, info=3, index=1))]
        self.assertEqual(len(self.facts()[0]), 1)
    def test_no_mutation_and_removed_records(self):
        self.elf.sections.append(dict(name='.target', index=3))
        self.elf.relocations = [self.a, dict(self.b, owner='.target')]
        before = copy.deepcopy(self.elf)
        retained, removed = self.facts()
        self.assertEqual(len(retained), 1)
        self.assertEqual(removed, [('.target', 0, 2, 0, 'external')])
        self.assertEqual(before, self.elf)
        self.assertEqual(self.facts(), (retained, removed))

if __name__ == '__main__':
    unittest.main()
