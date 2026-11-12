"""Offline synthetic regression for the publication verifier, including python -O."""
import copy
import hashlib
import io
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'verify-publication.py'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def apk_bytes(manifest=True):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        archive.writestr(zipfile.ZipInfo('AndroidManifest.xml' if manifest else 'other.xml'), b'fake-xml')
    return stream.getvalue()


def fixture(root):
    (root / 'scripts').mkdir()
    (root / 'scripts' / 'verify-publication.py').write_bytes(SCRIPT.read_bytes())
    (root / 'firmware-downloads').mkdir()
    rows = []
    for i in range(22):
        name = 'firmware-downloads/fake%02d.bin' % i
        data = ('fake-%02d' % i).encode('ascii')
        (root / name).write_bytes(data)
        rows.append({'path': name, 'bytes': len(data), 'sha256': digest(data)})
    data = apk_bytes()
    (root / 'fake.apk').write_bytes(data)
    rows.append({'path': 'fake.apk', 'bytes': len(data), 'sha256': digest(data)})
    return {'files': rows, 'APK': {'path': 'fake.apk', 'bytes': len(data),
                                  'sha256': digest(data)}, 'target_ready': False,
            'rebuilt_flashable_BIN': False}


def replace_apk(root, manifest, data):
    (root / 'fake.apk').write_bytes(data)
    row = manifest['files'][-1]
    row['bytes'], row['sha256'] = len(data), digest(data)
    manifest['APK']['bytes'], manifest['APK']['sha256'] = len(data), digest(data)


def mutate(root, manifest, case):
    rows = manifest['files']
    if case == 'outside':
        rows[0]['path'] = '../outside.bin'
    elif case == 'duplicate_path':
        rows[1] = copy.deepcopy(rows[0])
    elif case == 'size':
        rows[0]['bytes'] += 1
    elif case == 'sha':
        rows[0]['sha256'] = '0' * 64
    elif case == 'count':
        del rows[0]
    elif case == 'unique_sha':
        (root / rows[1]['path']).write_bytes((root / rows[0]['path']).read_bytes())
        rows[1]['sha256'] = rows[0]['sha256']
    elif case == 'crc':
        replace_apk(root, manifest, apk_bytes().replace(b'fake-xml', b'Fake-xml', 1))
    elif case == 'android_manifest':
        replace_apk(root, manifest, apk_bytes(False))
    elif case == 'apk_unlisted':
        (root / 'other.apk').write_bytes(apk_bytes())
        manifest['APK']['path'] = 'other.apk'
    elif case == 'apk_outside':
        (root.parent / 'outside.apk').write_bytes(apk_bytes())
        manifest['APK']['path'] = '../outside.apk'
    elif case == 'apk_absolute_outside':
        outside = root.parent / 'outside.apk'
        outside.write_bytes(apk_bytes())
        manifest['APK']['path'] = str(outside)
    elif case == 'apk_alias':
        manifest['APK']['path'] = './fake.apk'
    elif case == 'apk_metadata_bytes':
        manifest['APK']['bytes'] += 1
    elif case == 'apk_metadata_sha':
        manifest['APK']['sha256'] = '0' * 64
    elif case == 'apk_metadata_missing_bytes':
        del manifest['APK']['bytes']
    elif case == 'apk_metadata_missing_sha':
        del manifest['APK']['sha256']
    elif case == 'apk_duplicate':
        rows.append(copy.deepcopy(rows[-1]))
    elif case in ('apk_switch_good', 'apk_switch_bad'):
        data = apk_bytes(case == 'apk_switch_good')
        (root / 'second.apk').write_bytes(data)
        rows.append({'path': 'second.apk', 'bytes': len(data), 'sha256': digest(data)})
        manifest['APK'].update(path='second.apk', bytes=len(data), sha256=digest(data))
    elif case == 'target_ready':
        manifest['target_ready'] = True
    elif case == 'rebuilt_flashable_BIN':
        manifest['rebuilt_flashable_BIN'] = True
    else:
        raise ValueError(case)


class PublicationOptimizedRegression(unittest.TestCase):
    def test_cli_matrix(self):
        cases = {
            'outside': ('if not (path.is_relative_to(ROOT)', ''),
            'duplicate_path': ('if not (path.is_relative_to(ROOT)', ''),
            'size': ("if not len(raw) == row['bytes']:", 'firmware-downloads/fake00.bin'),
            'sha': ('if not hashlib.sha256(raw).hexdigest()', 'firmware-downloads/fake00.bin'),
            'count': ('if not len(firmware) ==', ''),
            'unique_sha': ('if not len(firmware) ==', ''),
            'crc': ('if not archive.testzip() is None:', 'APK member CRC failure'),
            'android_manifest': ("if not 'AndroidManifest.xml' in archive.namelist():", ''),
            'apk_unlisted': ('if apk_raw is None:', 'APK path not listed'),
            'apk_outside': ('if apk_raw is None:', 'APK path not listed'),
            'apk_absolute_outside': ('if apk_raw is None:', 'APK path not listed'),
            'apk_alias': ('if apk_raw is None:', 'APK path not listed'),
            'apk_metadata_bytes': ("if any(manifest['APK'].get(key)", 'APK metadata mismatch'),
            'apk_metadata_sha': ("if any(manifest['APK'].get(key)", 'APK metadata mismatch'),
            'apk_metadata_missing_bytes': ("if any(manifest['APK'].get(key)", 'APK metadata mismatch'),
            'apk_metadata_missing_sha': ("if any(manifest['APK'].get(key)", 'APK metadata mismatch'),
            'apk_duplicate': ('if not (path.is_relative_to(ROOT)', ''),
            'apk_switch_bad': ("if not 'AndroidManifest.xml' in archive.namelist():", ''),
            'target_ready': ("if not (not manifest['target_ready']", ''),
            'rebuilt_flashable_BIN': ("if not (not manifest['target_ready']", ''),
        }
        for flags in (['-I', '-S', '-B'], ['-I', '-S', '-O', '-B']):
            for case in ['positive', 'apk_switch_good', *cases]:
                with self.subTest(flags=flags, case=case), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / 'root'
                    root.mkdir()
                    manifest = fixture(root)
                    if case != 'positive':
                        mutate(root, manifest, case)
                    (root / 'publication-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
                    script = root / 'scripts' / 'verify-publication.py'
                    result = subprocess.run([sys.executable, *flags, str(script)],
                                            capture_output=True, text=True, timeout=15)
                    if case in ('positive', 'apk_switch_good'):
                        self.assertEqual(result.returncode, 0, result.stderr)
                        output = json.loads(result.stdout)
                        self.assertEqual(output['unique_original_BINs'], 22)
                        self.assertTrue(output['passed'])
                    else:
                        marker, message = cases[case]
                        lines = script.read_text(encoding='utf-8').splitlines()
                        line = next(i + 2 for i, text in enumerate(lines) if marker in text)
                        self.assertNotEqual(result.returncode, 0, case)
                        self.assertIn('line %d, in main' % line, result.stderr)
                        self.assertEqual(result.stderr.splitlines()[-1],
                                         'AssertionError' + (': ' + message if message else ''))
                        self.assertNotIn('"passed": true', result.stdout)

    def test_empty_verified_apk_fails_as_invalid_zip(self):
        for flags in (['-I', '-S', '-B'], ['-I', '-S', '-O', '-B']):
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                manifest = fixture(root)
                replace_apk(root, manifest, b'')
                (root / 'publication-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
                result = subprocess.run([sys.executable, *flags, str(root / 'scripts' / 'verify-publication.py')],
                                        capture_output=True, text=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('zipfile.BadZipFile', result.stderr)
                self.assertNotIn('APK path not listed', result.stderr)
                self.assertNotIn('"passed": true', result.stdout)

    def test_zip_receives_verified_bytes_without_reopening(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = fixture(root)
            expected = apk_bytes()
            replacement = apk_bytes(False)
            (root / 'publication-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            spec = importlib.util.spec_from_file_location('publication_verifier', SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.ROOT = root
            real_zip = zipfile.ZipFile
            real_read = Path.read_bytes
            reads = []
            calls = []

            def read_bytes(path):
                reads.append(path)
                return real_read(path)

            def open_zip(stream, *args, **kwargs):
                self.assertIsInstance(stream, io.BytesIO)
                self.assertEqual(stream.getvalue(), expected)
                calls.append(stream.getvalue())
                # Replacement after hashing must not change the archive being checked.
                (root / 'fake.apk').write_bytes(replacement)
                return real_zip(stream, *args, **kwargs)

            with mock.patch.object(Path, 'read_bytes', read_bytes), \
                    mock.patch.object(module.zipfile, 'ZipFile', side_effect=open_zip), \
                    mock.patch('sys.stdout', new_callable=io.StringIO):
                module.main()
            self.assertEqual(calls, [expected])
            self.assertEqual(reads.count((root / 'fake.apk').resolve()), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
