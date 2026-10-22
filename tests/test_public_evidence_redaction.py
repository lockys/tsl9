#!/usr/bin/env python3
"""Offline regression checks for redaction and evidence preservation."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

SPEC = importlib.util.spec_from_file_location(
    'redaction', Path(__file__).resolve().parents[1]/'scripts/anonymize_public_evidence.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def members(values):
    return {name:(text.encode(),text) for name,text in values.items()}


def test_directory():
    return tempfile.TemporaryDirectory(dir=os.environ.get('TSL9_TEST_TMP'))


class RedactionTests(unittest.TestCase):
    def test_escaped_json_project_path(self):
        home = 'C:'+'\\Users\\'+'sample'
        raw = json.dumps({'path':home+'\\Documents\\projects\\tsl9-reversed\\analysis\\a.json'})
        got = json.loads(M.redact(raw,['sample']))['path'].replace('\\','/')
        self.assertEqual(got,'${PROJECT_ROOT}/analysis/a.json')

    def test_platform_homes_and_account_boundaries(self):
        windows = 'C:'+'/Users/'+'sample'+'/notes'
        for raw in [windows,'/home/'+'sample'+'/notes','/Users/'+'sample'+'/notes']:
            self.assertEqual(M.redact(raw,['sample']),'${HOME}/notes')
        self.assertEqual(M.redact('sample samples sample_name',['sample']),
                         '${LOCAL_ACCOUNT} samples sample_name')

    def test_tool_root_maps_to_variable(self):
        raw = ('C:'+'/Users/'+'sample'+'/AppData/Local/Android/Sdk/ndk/v/toolchains/'
               'llvm/prebuilt/windows-x86_64/bin/clang.exe')
        self.assertEqual(M.redact(raw,['sample']),'${LLVM_BIN}/clang.exe')

    def test_transitive_text_hashes_and_binary_hash_remain(self):
        first = json.dumps({'path':'C:'+'/Users/'+'sample'+'/notes'})+'\r\n'
        second = json.dumps({'source_sha256':M.digest(first.encode())})+'\n'
        third = json.dumps({'reader_sha256':M.digest(second.encode()).upper()})+'\n'
        binary_sha = M.digest(bytes([0,1,255]))
        files = members({'first.json':first,'second.json':second,'third.json':third,
                         'binary-ref.json':json.dumps({'bin':binary_sha})+'\n'})
        texts,changed,depth = M.plan(files,['sample'])
        self.assertEqual(json.loads(texts['second.json'])['source_sha256'],
                         M.digest(texts['first.json'].encode()))
        self.assertEqual(json.loads(texts['third.json'])['reader_sha256'],
                         M.digest(texts['second.json'].encode()).upper())
        self.assertEqual(texts['binary-ref.json'],files['binary-ref.json'][1])
        self.assertEqual(files['first.json'][0],first.encode())
        self.assertFalse(changed['first.json']['dependent_text_hash_pins_changed'])
        self.assertTrue(changed['second.json']['dependent_text_hash_pins_changed'])
        self.assertNotIn('\r',texts['first.json'])
        self.assertEqual(depth,2)

    def test_duplicate_original_members_have_identical_public_digest(self):
        raw = 'C:'+'/Users/'+'sample'+'/notes\n'
        files = members({'a.txt':raw,'copy.txt':raw,'pin.txt':M.digest(raw.encode())+'\n'})
        texts,_,_ = M.plan(files,['sample'])
        self.assertEqual(texts['a.txt'],texts['copy.txt'])
        self.assertEqual(texts['pin.txt'].strip(),M.digest(texts['a.txt'].encode()))

    def test_cycle_rejected_before_edit(self):
        a,b = 'a'*64,'b'*64
        files = members({'a.txt':b,'b.txt':a})
        with mock.patch.object(M,'digest',side_effect=lambda data:a if data==b.encode() else b):
            with self.assertRaisesRegex(ValueError,'Cyclic'):
                M.plan(files,[])

    def test_private_backup_exact_bytes_and_tamper_rejection(self):
        with test_directory() as directory:
            base=Path(directory);tree=base/'repo';tree.mkdir()
            files=members({'receipt.json':'{"historical":true}\r\n'})
            with mock.patch.object(M,'ROOT',tree),mock.patch.object(M,'git',return_value='synthetic-head'):
                backup=M.backup(files,base/'private')
                saved=M.verify_backup(backup)
                self.assertEqual(saved['HEAD'],'synthetic-head')
                with zipfile.ZipFile(backup) as original:
                    self.assertEqual(original.read('receipt.json'),files['receipt.json'][0])
                    damaged=base/'damaged.zip'
                    with zipfile.ZipFile(damaged,'w') as target:
                        for name in original.namelist():
                            target.writestr(name,b'changed' if name=='receipt.json' else original.read(name))
                with self.assertRaisesRegex(ValueError,'Original backup byte equality'):
                    M.verify_backup(damaged)

    def test_private_backup_must_be_outside_project(self):
        with test_directory() as directory:
            tree=Path(directory)
            with mock.patch.object(M,'ROOT',tree):
                with self.assertRaisesRegex(ValueError,'outside'):
                    M.backup({},tree/'private')

    def test_public_digest_guard_rejects_changed_receipt(self):
        with test_directory() as directory:
            tree=Path(directory)
            (tree/'receipt.json').write_text('{}\n',encoding='utf-8')
            public=tree/M.PUBLIC;public.parent.mkdir(parents=True)
            public.write_text(json.dumps({'files':{'receipt.json':{'public_sha256':'0'*64}}}),
                              encoding='utf-8')
            with mock.patch.object(M,'ROOT',tree):
                with self.assertRaisesRegex(ValueError,'Public derivative digest'):
                    M.check_public()


if __name__=='__main__':
    unittest.main()
