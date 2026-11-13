import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.image = bytes(range(16))
        self.regions = [self.region('first_100', 0x100, 0x104),
                        self.region('second_104', 0x104, 0x108),
                        self.region('third_10a', 0x10a, 0x10c)]
        self.source = b'REGION void first_100(void) {}\nREGION void second_104(void) {}\nREGION void third_10a(void) {}'

    def region(self, name, start, end):
        return dict(name=name, start=start, end=end, bytes=end-start,
                    original_sha256=v.sha(self.image[start-0x100:end-0x100]))

    def check(self, regions=None, image=None):
        return v.validate_windows(self.regions if regions is None else regions,
                                  self.image if image is None else image, 0x100)

    def test_valid_and_adjacency(self):
        ordered = self.check(list(reversed(self.regions)))
        self.assertEqual(set(v.source_inventory(self.source, ordered)), {r['name'] for r in ordered})
        self.assertEqual(v.summary(ordered), dict(regions=3, bytes=10, min_start=0x100,
                         max_end_exclusive=0x10c, adjacent_groups=[[0x100, 0x108], [0x10a, 0x10c]], gaps=[[0x108, 0x10a]]))

    def test_overlap_zero_and_bounds(self):
        cases = [self.region('overlap_102', 0x102, 0x106), self.region('zero_100', 0x100, 0x100),
                 self.region('below_fe', 0xfe, 0x102), self.region('above_110', 0x110, 0x112),
                 self.region('odd_101', 0x101, 0x104)]
        for r in cases:
            with self.subTest(r=r), self.assertRaises(ValueError):
                self.check(self.regions + [r])

    def test_type_name_suffix_hash_and_size(self):
        for key, value in [('start', True), ('end', False), ('bytes', True), ('start', -2),
                           ('bytes', -1), ('bytes', 2), ('name', 'wrong_102'),
                           ('name', 'bad-name_100'), ('name', 'no_suffix'),
                           ('original_sha256', 'x'*64), ('original_sha256', 'A'*64),
                           ('original_sha256', 123)]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                rs = copy.deepcopy(self.regions); rs[0][key] = value; self.check(rs)
        with self.assertRaisesRegex(ValueError, 'duplicate name'):
            self.check(self.regions + [self.regions[0]])

    def test_slice_comparison_independent(self):
        changed = bytearray(self.image); changed[1] ^= 1
        with self.assertRaisesRegex(ValueError, 'slice SHA-256 mismatch: first_100'):
            self.check(image=bytes(changed))
        rs = copy.deepcopy(self.regions)
        rs[0]['original_sha256'], rs[1]['original_sha256'] = rs[1]['original_sha256'], rs[0]['original_sha256']
        with self.assertRaisesRegex(ValueError, 'slice SHA-256 mismatch'):
            self.check(rs)

    def test_inventory(self):
        for source in [self.source.replace(b'REGION void first_100(void) {}', b''),
                       self.source + b'\nREGION void first_100(void) {}',
                       self.source.replace(b'first_100', b'other_100'),
                       self.source + b'\nREGION int fake_110(void) {}',
                       self.source + b'\nREGION void fake_110(void) {}']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                v.source_inventory(source, self.regions)
        self.assertEqual(len(v.source_inventory(b'// REGION void fake(void) {}\n#define REGION x\n' + self.source, self.regions)), 3)

    def test_duplicate_json_keys(self):
        self.assertEqual(v.parse_spec(b'{"regions": [{"name": "x"}]}'), {'regions': [{'name': 'x'}]})
        for spec in (b'{"regions": [], "regions": []}',
                     b'{"regions": [{"name": "x", "name": "y"}]}',
                     b'{"nested": {"key": 1, "key": 2}}'):
            with self.subTest(spec=spec), self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
                v.parse_spec(spec)

    def test_b0_reference_independently(self):
        data = bytes.fromhex('97170020a38da7e28280')
        image = b'\xaa\xbb' + data + b'\xcc'
        region = dict(name='tsl9_record_dispatch_provider_b0b0', start=0xb0b0,
                      end=0xb0ba, bytes=10, original_sha256=v.B0)
        v.validate_b0([region], image, 0xb0ae)
        for field, value in [('start', 0xb0b2), ('end', 0xb0b8), ('bytes', 8),
                             ('bytes', True), ('original_sha256', '0'*64)]:
            changed = dict(region, **{field: value})
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, 'b0b0 reference mismatch'):
                v.validate_b0([changed], image, 0xb0ae)
        for regions in ([], [region, region], [dict(region, name='other_b0b0')]):
            with self.subTest(regions=regions), self.assertRaisesRegex(ValueError, 'b0b0 missing or duplicate'):
                v.validate_b0(regions, image, 0xb0ae)
        for i in range(10):
            changed = bytearray(image); changed[2+i] ^= 1
            with self.subTest(byte=i), self.assertRaisesRegex(ValueError, 'b0b0 bytes mismatch'):
                v.validate_b0([region], bytes(changed), 0xb0ae)
        for size in range(10):
            with self.subTest(truncated=size), self.assertRaisesRegex(ValueError, 'b0b0 bytes mismatch'):
                v.validate_b0([region], image[:2+size], 0xb0ae)
        with self.assertRaisesRegex(ValueError, 'b0b0 bytes mismatch'):
            v.validate_b0([region], image, 0xb0b2)

    def test_full_verifier_synthetic_and_guards(self):
        image = bytes.fromhex('97170020a38da7e28280') + b'\x00\x00\x12\x34'
        regions = [dict(name='tsl9_record_dispatch_provider_b0b0', start=0xb0b0, end=0xb0ba,
                        bytes=10, original_sha256=v.B0),
                   dict(name='other_b0bc', start=0xb0bc, end=0xb0be, bytes=2,
                        original_sha256=v.sha(image[12:14]))]
        spec = json.dumps({'regions': regions}).encode()
        source = b'REGION void tsl9_record_dispatch_provider_b0b0(void) {}\nREGION void other_b0bc(void) {}'
        with patch.multiple(v, BASE=0xb0b0, LENGTH=len(image), SPEC_SHA=v.sha(spec),
                            SOURCE_SHA=v.sha(source), IMAGE_SHA=v.sha(image)):
            self.assertEqual(v.verify(spec, source, image)['bytes'], 12)
            with self.assertRaisesRegex(ValueError, 'spec SHA-256'): v.verify(spec+b' ', source, image)
            with self.assertRaisesRegex(ValueError, 'source SHA-256'): v.verify(spec, source+b' ', image)
            with self.assertRaisesRegex(ValueError, 'slice SHA-256'): v.verify(spec, source, image[:12]+b'\x00\x34')
            with self.assertRaisesRegex(ValueError, 'image SHA-256'): v.verify(spec, source, image[:10]+b'\x01'+image[11:])
            with self.assertRaisesRegex(ValueError, 'length'): v.verify(spec, source, image[:-1])
            duplicate = spec.replace(b'{"regions":', b'{"regions": [], "regions":', 1)
            with patch.object(v, 'SPEC_SHA', v.sha(duplicate)):
                with self.assertRaisesRegex(ValueError, 'duplicate JSON key'): v.verify(duplicate, source, image)

    def test_no_success_output_on_failure_or_optimized(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / 'bad.bin'; image.write_bytes(b'\0' * v.LENGTH)
            for optimized in ([], ['-O']):
                cmd = [sys.executable, *optimized, str(Path(v.__file__)), '--bin', str(image)]
                p = subprocess.run(cmd, capture_output=True, text=True)
                self.assertNotEqual(p.returncode, 0)
                self.assertEqual(p.stdout, '')
                self.assertIn('slice SHA-256 mismatch', p.stderr)
                missing = subprocess.run(cmd + ['--spec', str(Path(temp) / 'missing.json')], capture_output=True, text=True)
                self.assertNotEqual(missing.returncode, 0)
                self.assertEqual(missing.stdout, '')
                self.assertIn('verification failed:', missing.stderr)


if __name__ == '__main__':
    unittest.main()
