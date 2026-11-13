"""Standard-library synthetic objects only; no ELF, tools, target, or network."""
import copy
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guard import comment_projections


def symbol(name, info=0, index=1):
    return dict(name=name, value=0, size=0, info=info, other=0, index=index)


class Object:
    def __init__(self, count):
        self.kind, self.flags = 1, 1
        self.sections = [dict(name='', index=0), dict(name='.comment', index=1,
            type=1, flags=48, size=3, alignment=1, address=0, link=0, info=0,
            entry_size=0, data=b'abc')]
        self.symbols = [symbol('', 3), symbol('keep', 16, 0)]
        self.symbols += [symbol('$d.%d' % n) for n in range(count)]
        self.relocations = []

    def data(self, section):
        return section['data']

    def function_bytes(self, sym):
        return b''


def objects():
    return [Object(2), Object(3), Object(1)]


def project(objs):
    return comment_projections(*objs, objs)


class Tests(unittest.TestCase):
    def test_positive_and_only_mappings_projected(self):
        objs = objects()
        objs[1].symbols[-1]['name'] = '$d.999'
        before = [list(o.symbols) for o in objs]
        views = project(objs)
        for obj, view, symbols in zip(objs, views, before):
            self.assertEqual(view.symbols, symbols[:2])
            self.assertIs(view.symbols[0], symbols[0])
            self.assertIs(view.sections, obj.sections)
            self.assertIs(view.relocations, obj.relocations)
            self.assertEqual((view.kind, view.flags), (obj.kind, obj.flags))
            self.assertEqual(view.data(obj.sections[1]), b'abc')
            self.assertEqual(view.function_bytes(symbols[0]), b'')
            self.assertEqual(obj.symbols, symbols)
        # Existing view exclusions are preserved, not reconstructed from the object.
        views = copy.copy(objs)
        views[0] = copy.copy(objs[0])
        views[0].symbols = [objs[0].symbols[0]]
        self.assertEqual(comment_projections(*objs, views)[0].symbols, views[0].symbols)

    def test_nobits_on_each_side_and_all_three_rejected_before_data(self):
        for sides in ((0,), (1,), (2,), (0, 1, 2)):
            objs = objects()
            for i in sides:
                objs[i].sections[1]['type'] = 8
                objs[i].data = mock.Mock(side_effect=AssertionError('NOBITS read'))
            with self.subTest(sides=sides), self.assertRaisesRegex(ValueError, 'SHT_PROGBITS'):
                project(objs)
            for i in sides:
                objs[i].data.assert_not_called()

    def test_mapping_counts_including_paired_extras(self):
        for side in range(3):
            for action in ('missing', 'extra'):
                objs = objects()
                if action == 'missing':
                    objs[side].symbols.pop()
                else:
                    objs[side].symbols.append(symbol('$d.50'))
                with self.subTest(side=side, action=action), self.assertRaises(ValueError):
                    project(objs)
        objs = objects()
        for i in (1, 2):
            objs[i].symbols.append(symbol('$d.50'))
        with self.assertRaisesRegex(ValueError, 'leaf_partial must have exactly one'):
            project(objs)

    def test_section_shape_metadata_and_bytes(self):
        changes = [('name', '.other'), ('index', 0), ('index', 2), ('size', 0),
                   ('type', 8), ('flags', 0), ('size', 2), ('alignment', 2),
                   ('address', 1), ('link', 1), ('info', 1), ('entry_size', 1),
                   ('data', b'abd'), ('data', b'ab')]
        for side in range(3):
            for field, value in changes:
                objs = objects()
                objs[side].sections[1][field] = value
                with self.subTest(side=side, field=field, value=value), self.assertRaises(ValueError):
                    project(objs)
            objs = objects()
            objs[side].sections.append(copy.deepcopy(objs[side].sections[1]))
            with self.subTest(side=side, duplicate=True), self.assertRaisesRegex(ValueError, 'unique .comment'):
                project(objs)
        objs = objects()
        for obj in objs:
            obj.sections[1].update(size=0, data=b'')
        with self.assertRaisesRegex(ValueError, 'invalid .comment section'):
            project(objs)

    def test_section_symbols_missing_duplicate_bad_or_referenced(self):
        for side in range(3):
            for field, value in [('missing', None), ('duplicate', None), ('name', 'alias'),
                                 ('value', 1), ('size', 1), ('info', 19), ('other', 1),
                                 ('index', 0), ('referenced', None)]:
                objs = objects()
                obj, sym = objs[side], objs[side].symbols[0]
                if field == 'missing':
                    obj.symbols.remove(sym)
                elif field == 'duplicate':
                    obj.symbols.append(copy.deepcopy(sym))
                elif field == 'referenced':
                    obj.relocations.append(dict(symbol=sym))
                else:
                    sym[field] = value
                with self.subTest(side=side, field=field), self.assertRaises(ValueError):
                    project(objs)

    def test_mapping_shapes_aliases_and_references(self):
        changes = [('name', '$x.1'), ('name', '$d.１'), ('name', '$d.1x'),
                   ('name', '.Lalias'), ('name', 'global_alias'), ('value', 1),
                   ('size', 1), ('info', 1), ('info', 16), ('other', 1)]
        for side in range(3):
            for field, value in changes:
                objs = objects()
                objs[side].symbols[-1][field] = value
                with self.subTest(side=side, field=field, value=value), self.assertRaisesRegex(
                        ValueError, 'unexpected or invalid .comment symbol'):
                    project(objs)
            objs = objects()
            objs[side].symbols.append(symbol('global_alias', 16))
            with self.subTest(side=side, extra_global=True), self.assertRaises(ValueError):
                project(objs)
            objs = objects()
            obj = objs[side]
            obj.relocations.append(dict(symbol=obj.symbols[-1]))
            with self.subTest(side=side, reference=True), self.assertRaisesRegex(ValueError, 'mapping symbol referenced'):
                project(objs)


if __name__ == '__main__':
    unittest.main()
