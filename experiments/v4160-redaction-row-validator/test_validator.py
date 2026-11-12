import copy
import hashlib
import json
import unittest
from dataclasses import replace

import validator as v


def encode(value):
    return json.dumps(value, separators=(',', ':')).encode()


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.a, self.b = b'original text', b'public'
        self.path = 'synthetic/path'
        digest = lambda x: hashlib.sha256(x).hexdigest()
        self.old = {'files': [{'path': self.path, 'bytes': len(self.a), 'sha256': digest(self.a)}]}
        self.new = {'files': [{'path': self.path, 'bytes': len(self.a), 'sha256': digest(self.b)}]}
        self.red = {'schema': 'TSL9-public-path-redaction-v1', 'original_HEAD': 'parent',
                    'original_receipts_preserved_privately': True, 'Git_history_rewritten': False,
                    'files': {self.path: {'original_sha256': digest(self.a), 'public_sha256': digest(self.b),
                    'original_bytes': len(self.a), 'public_bytes': len(self.b),
                    'personal_path_or_label_changed': True, 'dependent_text_hash_pins_changed': True,
                    'native_editor_LF_representation': True,
                    'status': 'anonymized historical/public derivative; not the original receipt'}}}
        self.spec = v.Spec(self.path, 'parent', 'commit', digest(self.a), digest(self.b),
                           len(self.a), len(self.b), v.git_blob_oid(self.a), v.git_blob_oid(self.b),
                           v.git_blob_oid(encode(self.red)))

    def run_validation(self, old=None, new=None, red=None, a=None, b=None, parent='parent', commit='commit', spec=None):
        return v.validate_with_spec(encode(self.old) if old is None else old,
            encode(self.new) if new is None else new, encode(self.red) if red is None else red,
            self.a if a is None else a, self.b if b is None else b, parent, commit, spec or self.spec)

    def test_positive(self):
        self.assertTrue(self.run_validation())
        self.assertEqual(v.git_blob_oid(b'hello\n'), 'ce013625030ba8dba906f756967f9e9ca394464a')

    def test_invalid_inputs(self):
        cases = [dict(parent='wrong'), dict(commit='wrong'), dict(a=b'bad'), dict(b=b'bad'),
                 dict(old=b'{"files":[],"files":[]}'), dict(new=b'{"files":null}'),
                 dict(old=b'{}\xff'), dict(red=b'{}'), dict(old=b' ' * (v.MAX_MANIFEST + 1)),
                 dict(a=b'\xff'), dict(new=encode({'files': [self.new['files'][0]] * 2})),
                 dict(new=encode({'files': [{'path': self.path, 'bytes': True, 'sha256': self.spec.new_sha256}]})),
                 dict(new=encode({'files': [{'path': self.path, 'bytes': len(self.b), 'sha256': self.spec.new_sha256}]})),
                 dict(spec=replace(self.spec, old_oid='0' * 40))]
        for case in cases:
            with self.subTest(case=list(case)):
                with self.assertRaises(v.Invalid):
                    self.run_validation(**case)

    def test_redaction_checks_after_valid_oid(self):
        mutations = [
            (None, 'schema', 'wrong'), (None, 'original_HEAD', 'wrong'),
            (None, 'original_receipts_preserved_privately', False),
            (None, 'Git_history_rewritten', True),
            ('row', 'original_sha256', '0' * 64), ('row', 'public_sha256', '0' * 64),
            ('row', 'original_bytes', True), ('row', 'public_bytes', True),
            ('row', 'personal_path_or_label_changed', False),
            ('row', 'dependent_text_hash_pins_changed', False),
            ('row', 'native_editor_LF_representation', False),
            ('row', 'status', 'wrong'),
        ]
        for location, key, value in mutations:
            with self.subTest(key=key):
                doc = copy.deepcopy(self.red)
                (doc['files'][self.path] if location else doc)[key] = value
                data = encode(doc)
                with self.assertRaises(v.Invalid):
                    self.run_validation(red=data, spec=replace(self.spec, redaction_oid=v.git_blob_oid(data)))

    def test_nonfinite_float_rejected(self):
        for number in (b'1e999', b'-1e999'):
            with self.subTest(number=number):
                with self.assertRaises(v.Invalid):
                    self.run_validation(old=b'{"extra":' + number + b',' + encode(self.old)[1:])

    def test_invalid_utf8_blob_with_matching_spec(self):
        blob = b'\xff'
        digest = hashlib.sha256(blob).hexdigest()
        spec = replace(self.spec, old_size=len(blob), old_sha256=digest, old_oid=v.git_blob_oid(blob))
        self.old['files'][0].update(bytes=len(blob), sha256=digest)
        self.new['files'][0]['bytes'] = len(blob)
        with self.assertRaisesRegex(v.Invalid, 'blob is not UTF-8'):
            self.run_validation(a=blob, spec=spec)

    def test_duplicate_nested_key(self):
        data = b'{"files":{},"x":{"a":1,"a":2}}'
        with self.assertRaises(v.Invalid):
            self.run_validation(red=data, spec=replace(self.spec, redaction_oid=v.git_blob_oid(data)))

    def test_fixed_policy_cannot_use_synthetic_spec(self):
        with self.assertRaises(v.Invalid):
            v.validate(encode(self.old), encode(self.new), encode(self.red), self.a, self.b, 'parent', 'commit')


if __name__ == '__main__':
    unittest.main()
